"""Write out/assembly.step: lid, base, official board, community shield and a 4010 fan, in place."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build123d import Color, Compound, export_step  # noqa: E402
import case  # noqa: E402
import official_board  # noqa: E402


def fan_4010():
    return case.make_fan()


board = official_board.board_and_shield()
shield, heatsink = board.pop("shield"), board.pop("heatsink")
parts = [
    (case.make_lid(), "lid", Color(0.9, 0.5, 0.1, 0.5)),
    (case.make_base(), "base", Color(0.9, 0.5, 0.1)),
    (fan_4010(), "fan_4010", Color(0.15, 0.15, 0.15)),
    (Compound(list(board.values())), "board_official", Color(0.1, 0.5, 0.2)),
    (shield, "usb_shield", Color(0.1, 0.3, 0.7)),
    (heatsink, "heatsink_standin", Color(0.7, 0.7, 0.7)),
    (case.make_antenna(), "antenna_whip", Color(0.05, 0.05, 0.05)),
]
for shape, label, color in parts:
    shape.label, shape.color = label, color
out = Path(case.__file__).parent / "out" / "assembly.step"
export_step(Compound([p[0] for p in parts], label="opi_zero3_case_assembly"), str(out))
print(out)
