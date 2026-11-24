"""Print the round holes (center, diameter) in the given solids of the reference STEP."""
import sys
from build123d import import_step, GeomType

shape = import_step(sys.argv[1])
solids = shape.solids()
for idx in map(int, sys.argv[2:]):
    seen = set()
    for f in solids[idx].faces().filter_by(GeomType.CYLINDER):
        c = f.center()
        r = f.radius
        key = (round(c.X, 1), round(c.Y, 1), round(r, 2))
        if r < 3 and key not in seen:
            seen.add(key)
            print(f"solid {idx}: center=({c.X:7.2f},{c.Y:7.2f}) d={2 * r:5.2f}")
