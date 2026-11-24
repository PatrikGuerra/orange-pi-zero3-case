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
print("fit check OK")
