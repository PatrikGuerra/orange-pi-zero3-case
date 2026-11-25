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

# Shield screws: the nut + screw tip under the shield must not touch the main board or heatsink.
# M3 x 25 from the roof head recess must reach through the nut.
under = case.SHIELD_TOP_Z - case.SHIELD_PCB
for x, y in case.SHIELD_HOLES:
    nut = case.cyl_z(x, y, case.NUT_D, under - case.NUT_H - 1.0, under)
    for label in ("PCB-Z3", "heatsink", "RJ45", "_USB_ASM_3_ASM", "TYPE_C_CC"):
        c = board[label] & nut
        assert c is None or c.volume < 0.01, f"shield nut at ({x}, {y}) hits {label}"
    grip = (case.Z_TOP - case.HEAD_H) - (under - case.NUT_H)
    assert grip <= 25.0 - 0.5, f"M3 x 25 too short for the shield screw: needs {grip:.1f} mm"
    print(f"shield screw at ({x}, {y}): M3 x 25, {25.0 - grip:.1f} mm past the nut")

# Ports: every port of the official board ends inside the case and faces its window
ports = official_board.load()
for label, key in (("03_11_13_0003_HDMI0001", "micro_hdmi"), ("TYPE_C_CC", "usb_c"),
                   ("_USB_ASM_3_ASM", "usb_a"), ("RJ45", "rj45")):
    b = ports[label].bounding_box()
    x0, x1, z0, z1 = case.PORTS_MINUS_Y[key]
    tol = 0.01   # the dict values are rounded to 0.01 mm
    assert x0 <= b.min.X + tol and b.max.X <= x1 + tol and z0 <= b.min.Z + tol and b.max.Z <= z1 + tol, \
        f"{key} window does not cover the official part"
    assert b.min.Y > case.Y_IN[0], f"{key} sticks into the wall"

# Shield ports end near the outside face (flush look), not deep inside the case
recess = case.Y_OUT[1] - 26.80
assert 0 <= recess <= 0.5, f"shield ports sit {recess:.2f} mm behind the outside face"
print(f"shield ports {recess:.2f} mm behind the outside face")

# Fan: nuts clear the plate and the roof, and the fan stays inside the case outline
low, high = case.FAN_ZC - case.FAN_HOLE_PITCH / 2, case.FAN_ZC + case.FAN_HOLE_PITCH / 2
assert low - case.NUT_R >= case.PLATE_TOP_Z - 1e-6, "low fan nuts hit the base plate"
assert high + case.NUT_R <= case.ROOF_IN + 1e-6, "high fan nuts hit the roof"
assert case.FAN_ZC - case.FAN / 2 >= case.Z_BOT and case.FAN_ZC + case.FAN / 2 <= case.Z_TOP, "fan sticks out"

# Bosses: the screw head counterbore keeps >= 1 mm of plate to the plate edge
for x, y in case.BOSSES:
    edge = min(x - case.X_IN[0], case.X_IN[1] - x, y - case.Y_IN[0], case.Y_IN[1] - y) - case.FIT
    assert edge - case.HEAD_D / 2 >= 1.0 - 1e-6, f"screw head too close to the wall at ({x:.1f}, {y:.1f})"

# Fan grille: enough open area, and cells big enough for a 2-pin Dupont plug (5.1 x 2.5 mm)
g = case.fan_grille(case.X_OUT[0] - 1, 4.0)
open_ratio = g.volume / 4.0 / (math.pi * (case.GRILLE_D / 2) ** 2)
assert open_ratio >= 0.55, f"fan grille only {open_ratio:.0%} open"
assert case.GRILLE_CELL >= math.hypot(5.1, 2.5), "Dupont plug does not pass a grille cell"
print(f"fan grille {open_ratio:.0%} open")

# Port walls: a strip thinner than MIN_RIB between two windows must be cut away
for ports in (case.PORTS_MINUS_Y, case.PORTS_PLUS_Y):
    wins = case.port_windows(ports)
    edges = {(w[0], w[1]) for w in wins}
    for a in wins:
        for b in wins:
            gap = b[0] - a[1]
            if 0 < gap < case.MIN_RIB and min(a[3], b[3]) > max(a[2], b[2]):
                assert (a[1], b[0]) in edges, f"thin rib {gap:.2f} mm left at x={a[1]:.2f}"
print("fit check OK")
