"""Self-check: no board part may overlap the lid or the base, and each port must sit in its window."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import case  # noqa: E402
import official_board  # noqa: E402
from build123d import Align, Cylinder, Pos, Rot  # noqa: E402

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
pcb_gap = ports["PCB-Z3"].solids()[0].bounding_box().min.Y - case.Y_IN[0]
assert 0.2 <= pcb_gap <= 0.3 + 1e-3, f"main board edge is {pcb_gap:.2f} mm from the -Y wall"
tips = {k: case.Y_OUT[0] - ports[k].bounding_box().min.Y for k in
        ("03_11_13_0003_HDMI0001", "TYPE_C_CC", "_USB_ASM_3_ASM", "RJ45")}
print(f"main board {pcb_gap:.2f} mm off the -Y wall, ports "
      f"{-max(tips.values()):.2f} to {-min(tips.values()):.2f} mm behind the outside face")
slab = case.box(-60, 60, case.Y_OUT[0] - 1, case.Y_IN[0] + 1.5, -10, 60)
wins = case.port_windows(case.PORTS_MINUS_Y, case.PORT_CLEAR, case.MERGED_PORTS)
for label, key in (("03_11_13_0003_HDMI0001", "micro_hdmi"), ("TYPE_C_CC", "usb_c"),
                   ("_USB_ASM_3_ASM", "usb_a"), ("RJ45", "rj45")):
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

# Round audio window: the jack front, where it passes the wall, fits inside the circle
jack = board["shield"].solids()
wall = case.box(-60, 60, case.Y_IN[1], case.Y_OUT[1] + 1, -10, 60)
hole = case.round_window(case.PORTS_PLUS_Y["audio"], case.SHIELD_PORT_CLEAR)
x0, x1, z0, z1 = case.PORTS_PLUS_Y["audio"]
for s in jack:
    b = s.bounding_box()
    if not (x0 <= b.center().X <= x1 and b.max.Y > case.Y_IN[1]):
        continue
    front = s & wall
    rest = front - hole if front is not None else None
    assert rest is None or rest.volume < 0.01, f"audio jack hits the round window: {rest.volume:.2f} mm3"
print(f"audio window round, d = {max(x1 - x0, z1 - z0) + 2 * case.SHIELD_PORT_CLEAR:.1f} mm")

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

# Antenna on the +Y face: tie holes and the cable hole clear of the other openings,
# each tie's inside loop clear of the boards, antenna clear of the case
ay, az = case.antenna_axis()
w, hh = case.TIE_HOLE
holes = case.tie_holes()
sd_top = case.MICROSD[3] + 1.5
sd_x = (case.MICROSD[0] - 1.5, case.MICROSD[1] + 1.5)
usb_bottom = min(w_[2] for w_ in case.port_windows(case.PORTS_PLUS_Y, case.SHIELD_PORT_CLEAR))
audio = case.PORTS_PLUS_Y["audio"]
audio_r = max(audio[1] - audio[0], audio[3] - audio[2]) / 2 + case.SHIELD_PORT_CLEAR
hx, hz = case.ANT_HOLE
for x, z in holes:
    assert not (sd_x[0] < x + w / 2 and x - w / 2 < sd_x[1] and z - hh / 2 < sd_top), f"tie hole at x={x} hits the microSD notch"
    assert z + hh / 2 <= usb_bottom, f"tie hole at x={x} runs into the USB window"
    d = math.hypot(x - (audio[0] + audio[1]) / 2, z - (audio[2] + audio[3]) / 2)
    assert d > audio_r + hh, f"tie hole at x={x} is too close to the audio jack"
    assert abs(x - hx) >= w / 2 + case.ANT_HOLE_D / 2 + 1.0, f"tie hole at x={x} is too close to the cable hole"
    probe = case.box(x - 0.5, x + 0.5, case.Y_IN[1] - 1, case.Y_OUT[1] + 1, z - 0.3, z + 0.3)
    c = probe & parts["lid"]
    assert c is None or c.volume < 0.01, f"tie hole at ({x}, {z:.1f}) is blocked"
for x in case.TIE_X:   # inside, the tie runs up the wall from one hole to the other
    zs = [z for x_, z in holes if x_ == x]
    loop = case.box(x - w / 2, x + w / 2, case.Y_IN[1] - 1.2, case.Y_IN[1] - 0.01, min(zs) - hh / 2, max(zs) + hh / 2)
    for name, p in [("lid", parts["lid"])] + list(board.items()):
        c = loop & p
        assert c is None or c.volume < 0.01, f"zip tie at x={x} hits {name} inside"
assert hz + case.ANT_HOLE_D / 2 <= usb_bottom, "cable hole runs into the USB window"
assert hz + case.ANT_HOLE_D / 2 <= az - case.ANT_D / 2 + 1e-6, "cable hole is not under the antenna"
if sd_x[0] < hx + case.ANT_HOLE_D / 2 and hx - case.ANT_HOLE_D / 2 < sd_x[1]:
    bridge = hz - case.ANT_HOLE_D / 2 - sd_top
    assert bridge >= 0.6 - 1e-6, f"only {bridge:.2f} mm of wall between the cable hole and the microSD notch"
c = case.make_antenna() & parts["lid"]
assert c is None or c.volume < 0.01, f"antenna hits the lid: {c.volume:.2f} mm3"
# Cable hole: clear of the board and the shield, from the shield edge to the wall
y0 = case.SHIELD_EDGE_Y - 1.0
hole = Pos(hx, y0, hz) * Rot(-90, 0, 0) * Cylinder(case.ANT_HOLE_D / 2, case.Y_IN[1] - y0,
                                                   align=(Align.CENTER, Align.CENTER, Align.MIN))
for name, p in [("lid", parts["lid"])] + list(board.items()):
    c = hole & p
    assert c is None or c.volume < 0.01, f"antenna cable path hits {name}"
print(f"antenna: {case.ANT_D:g} mm whip on the +Y face at z {az:.1f}, 2 zip ties at x {case.TIE_X}, "
      f"4 holes {w} x {hh} mm, cable hole at z {hz:.1f}")

# Tower ribs: each tower is tied to its 2 nearest walls (a probe at mid-rib hits the lid)
for x, y in case.BOARD_HOLES:
    xw = case.X_IN[0] if x < 0 else case.X_IN[1]
    yw = case.Y_IN[0] if y < 0 else case.Y_IN[1]
    zm = (case.TOWER_RIB_Z0 + case.ROOF_IN) / 2
    for px, py in (((x + xw) / 2, y), (x, (y + yw) / 2)):
        c = parts["lid"] & case.box(px - 0.2, px + 0.2, py - 0.2, py + 0.2, zm - 0.2, zm + 0.2)
        assert c is not None and c.volume > 0.05, f"tower at ({x}, {y}) has no rib at ({px:.1f}, {py:.1f})"

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
