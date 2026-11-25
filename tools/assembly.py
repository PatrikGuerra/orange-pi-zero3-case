"""Write out/assembly.step: lid, base, official board, community shield and a 4010 fan, in place."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build123d import Align, Box, Color, Compound, Cylinder, Pos, Rot, export_step  # noqa: E402
import case  # noqa: E402
import official_board  # noqa: E402

UP_X = (Align.CENTER, Align.CENTER, Align.MIN)


def fan_4010():
    """Simple 4010 fan: frame with a 38 mm bore, hub, 4 screw holes. Mounted on the outside of the -X wall."""
    x0 = case.X_OUT[0] - 10.0

    def along_x(d, y, z):
        return Pos(x0, y, z) * Rot(0, 90, 0) * Cylinder(d / 2, 10, align=UP_X)

    frame = Pos(x0 + 5, case.YC, case.FAN_ZC) * Box(10, case.FAN, case.FAN)
    frame -= along_x(38, case.YC, case.FAN_ZC)
    p = case.FAN_HOLE_PITCH / 2
    for dy in (-p, p):
        for dz in (-p, p):
            frame -= along_x(3.4, case.YC + dy, case.FAN_ZC + dz)
    return frame + along_x(16, case.YC, case.FAN_ZC)


board = official_board.board_and_shield()
shield, heatsink = board.pop("shield"), board.pop("heatsink")
parts = [
    (case.make_lid(), "lid", Color(0.9, 0.5, 0.1, 0.5)),
    (case.make_base(), "base", Color(0.9, 0.5, 0.1)),
    (fan_4010(), "fan_4010", Color(0.15, 0.15, 0.15)),
    (Compound(list(board.values())), "board_official", Color(0.1, 0.5, 0.2)),
    (shield, "usb_shield", Color(0.1, 0.3, 0.7)),
    (heatsink, "heatsink_standin", Color(0.7, 0.7, 0.7)),
]
for shape, label, color in parts:
    shape.label, shape.color = label, color
out = Path(case.__file__).parent / "out" / "assembly.step"
export_step(Compound([p[0] for p in parts], label="opi_zero3_case_assembly"), str(out))
print(out)
