"""Self-check: no board part may overlap the lid or the base, and each port must sit in its window."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import case  # noqa: E402
import official_board  # noqa: E402

parts = {"lid": case.make_lid(), "base": case.make_base()}
board = official_board.board_and_shield()
bad = 0
for label, shape in board.items():
    for s in shape.solids():
        for name, p in parts.items():
            common = s & p
            v = common.volume if common is not None else 0.0
            if v > 0.01:
                print(f"OVERLAP {label} with {name}: {v:.2f} mm3")
                bad += 1
print(f"outer {case.X_OUT[1] - case.X_OUT[0]:.1f} x {case.Y_OUT[1] - case.Y_OUT[0]:.1f} x {case.HEIGHT:.1f} mm")
assert bad == 0, f"{bad} overlaps"

common = parts["lid"] & parts["base"]
assert common is None or common.volume < 0.01, f"base and lid overlap: {common.volume:.2f} mm3"

# Shield screws: M3 x 5 from under the shield into the post. The head must not touch the
# main board or heatsink, and the thread must bite >= 3 mm into the post.
under = case.SHIELD_TOP_Z - case.SHIELD_PCB
for x, y in case.SHIELD_HOLES:
    head = case.cyl_z(x, y, case.SHIELD_HEAD_D, under - case.SHIELD_HEAD_H, under)
    for label in ("PCB-Z3", "heatsink", "RJ45", "_USB_ASM_3_ASM", "TYPE_C_CC"):
        c = board[label] & head
        assert c is None or c.volume < 0.01, f"shield screw head at ({x}, {y}) hits {label}"
    bite = case.SHIELD_SCREW_L - case.SHIELD_PCB - 0.05
    assert bite >= 3.0, f"M3 x {case.SHIELD_SCREW_L:g} bites only {bite:.1f} mm into the post"
    print(f"shield screw at ({x}, {y}): M3 x {case.SHIELD_SCREW_L:g}, {bite:.1f} mm into the post")

# Ports: each official connector, where it passes the wall, sits inside its window
ports = official_board.load()
slab = case.box(-60, 60, case.Y_OUT[0] - 1, case.Y_IN[0] + 1.5, -10, 60)
wins = case.port_windows(case.PORTS_MINUS_Y, case.PORT_CLEAR, case.MERGED_PORTS)
for label, key in (("03_11_13_0003_HDMI0001", "micro_hdmi"), ("TYPE_C_CC", "usb_c"),
                   ("_USB_ASM_3_ASM", "usb_a"), ("RJ45", "rj45")):
    assert ports[label].bounding_box().min.Y > case.Y_IN[0], f"{key} sticks into the wall"
    for s in ports[label].solids():
        c = s & slab
        if c is None or c.volume < 0.001:
            continue
        b = c.bounding_box()
        tol = 0.01   # the dict values are rounded to 0.01 mm
        assert any(w[0] <= b.min.X + tol and b.max.X <= w[1] + tol and w[2] <= b.min.Z + tol
                   and b.max.Z <= w[3] + tol for w in wins), f"{key} window does not cover the connector"
merged = [w for w in wins if w[0] <= case.PORTS_MINUS_Y["usb_a"][0] and case.PORTS_MINUS_Y["rj45"][1] <= w[1]]
assert merged, "USB-A and RJ45 are not one window"
print("main ports:", ", ".join(f"{w[1] - w[0]:.1f} x {w[3] - w[2]:.1f}" for w in sorted(wins)))

# Shield ports end near the outside face (flush look), not deep inside the case
recess = case.Y_OUT[1] - 26.80
assert 0 <= recess <= 0.5, f"shield ports sit {recess:.2f} mm behind the outside face"
print(f"shield ports {recess:.2f} mm behind the outside face")

# Fan: inside the case, touching neither the lid, the base nor any board part
fan = case.make_fan()
for name, p in [("lid", parts["lid"]), ("base", parts["base"])] + list(board.items()):
    c = fan & p
    assert c is None or c.volume < 0.01, f"fan hits {name}: {c.volume:.2f} mm3"
fb = fan.bounding_box()
assert case.X_IN[0] <= fb.min.X and fb.max.X <= case.PCB_X[0], "fan is not between the -X wall and the board"
assert case.PLATE_TOP_Z <= fb.min.Z and fb.max.Z <= case.ROOF_IN, "fan does not fit in height"

# Board screws: M3 x BOARD_SCREW_L from below bites >= 6 mm into each tower
bite = case.BOARD_SCREW_L - (case.PCB_TOP_Z - case.Z_BOT)
assert bite >= 6.0, f"M3 x {case.BOARD_SCREW_L:g} bites only {bite:.1f} mm into the towers"
print(f"board screws: M3 x {case.BOARD_SCREW_L:g}, {bite:.1f} mm into the towers")

# Fan grille: enough open area, and cells big enough for a 2-pin Dupont plug (5.1 x 2.5 mm)
g = case.fan_grille(case.X_OUT[0] - 1, 4.0)
open_ratio = g.volume / 4.0 / (math.pi * (case.GRILLE_D / 2) ** 2)
assert open_ratio >= 0.55, f"fan grille only {open_ratio:.0%} open"
assert case.GRILLE_CELL >= math.hypot(5.1, 2.5), "Dupont plug does not pass a grille cell"
print(f"fan grille {open_ratio:.0%} open")

# Port walls: a strip thinner than MIN_RIB between two windows must be cut away
for ports, clear, merge in ((case.PORTS_MINUS_Y, case.PORT_CLEAR, case.MERGED_PORTS),
                            (case.PORTS_PLUS_Y, case.SHIELD_PORT_CLEAR, ())):
    wins = case.port_windows(ports, clear, merge)
    edges = {(w[0], w[1]) for w in wins}
    for a in wins:
        for b in wins:
            gap = b[0] - a[1]
            if 0 < gap < case.MIN_RIB and min(a[3], b[3]) > max(a[2], b[2]):
                assert (a[1], b[0]) in edges, f"thin rib {gap:.2f} mm left at x={a[1]:.2f}"
print("fit check OK")
