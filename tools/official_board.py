"""Official Orange Pi Zero 3 board (oficial/pcb-assy_asm.stp), moved into the case coordinates.

The official file has the board centered at (0, 0), PCB top at z = 0, ports on +X.
The case uses the reference STEP frame: ports on -Y, PCB bottom at z = 5.15.
The offsets come from matching the 4 mounting holes of both files (within 0.05 mm).
Run it to print the port boxes in case coordinates.
"""
from pathlib import Path
from build123d import Compound, Pos, Rot, import_step

FILE = Path(__file__).resolve().parents[1] / "oficial" / "pcb-assy_asm.stp"
PCB_THICK = 1.3
PLACE = Pos(4.42, -1.24, 5.15 + PCB_THICK) * Rot(0, 0, -90)


def load():
    """Return {label: shape} for every top-level part of the official board, in case coordinates."""
    return {c.label: PLACE * c for c in import_step(str(FILE)).children}


REFERENCE = Path(__file__).resolve().parents[1] / "reference" / "motorbottle-case.stp"
SHIELD_SOLIDS = range(0, 27)   # reference STEP: shield PCB, its ports and header sockets
HEATSINK_SOLID = 30            # reference STEP: stand-in for the glued heatsink


def board_and_shield():
    """Official main board + community shield and heatsink, all in case coordinates."""
    import case  # noqa: PLC0415
    ref = import_step(str(REFERENCE)).solids()
    lift = Pos(0, 0, case.SHIELD_DZ)
    parts = load()
    parts["shield"] = lift * Compound([ref[i] for i in SHIELD_SOLIDS if ref[i].volume > 0])
    parts["heatsink"] = lift * ref[HEATSINK_SOLID]
    return parts


if __name__ == "__main__":
    for label, part in load().items():
        b = part.bounding_box()
        print(f"{label:24s} x[{b.min.X:7.2f},{b.max.X:7.2f}] y[{b.min.Y:7.2f},{b.max.Y:7.2f}] z[{b.min.Z:6.2f},{b.max.Z:6.2f}]")
