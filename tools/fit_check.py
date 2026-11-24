"""Self-check: no board part may overlap the lid or the base, and each port must sit in its window."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build123d import import_step  # noqa: E402
import case  # noqa: E402

CASE_SOLIDS = {27, 28, 29}   # the MotorBottle case itself, not board parts
MSD_CARD = 32                # the card sticks out through the notch, ignore its tip

solids = import_step(str(Path(case.__file__).parent / "reference" / "motorbottle-case.stp")).solids()
parts = {"lid": case.make_lid(), "base": case.make_base()}
bad = 0
for i, s in enumerate(solids):
    if i in CASE_SOLIDS or s.volume <= 0:
        continue
    for name, p in parts.items():
        common = s & p
        v = common.volume if common is not None else 0.0
        if v > 0.01 and i != MSD_CARD:
            print(f"OVERLAP solid {i} with {name}: {v:.2f} mm3")
            bad += 1
print(f"outer {case.X_OUT[1] - case.X_OUT[0]:.1f} x {case.Y_OUT[1] - case.Y_OUT[0]:.1f} x {case.HEIGHT:.1f} mm")
assert bad == 0, f"{bad} overlaps"

# Fan: nuts clear the plate and the roof, and the fan stays inside the case outline
low, high = case.FAN_ZC - case.FAN_HOLE_PITCH / 2, case.FAN_ZC + case.FAN_HOLE_PITCH / 2
assert low - case.NUT_R >= case.PLATE_TOP_Z - 1e-6, "low fan nuts hit the base plate"
assert high + case.NUT_R <= case.ROOF_IN + 1e-6, "high fan nuts hit the roof"
assert case.FAN_ZC - case.FAN / 2 >= case.Z_BOT and case.FAN_ZC + case.FAN / 2 <= case.Z_TOP, "fan sticks out"

# Bosses: the screw head counterbore keeps >= 1 mm of plate to the plate edge
for x, y in case.BOSSES:
    edge = min(x - case.X_IN[0], case.X_IN[1] - x, y - case.Y_IN[0], case.Y_IN[1] - y) - case.FIT
    assert edge - case.HEAD_D / 2 >= 1.0 - 1e-6, f"screw head too close to the wall at ({x:.1f}, {y:.1f})"

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
