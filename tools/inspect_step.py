"""List every solid in the reference STEP with its bounding box (mm)."""
import sys
from build123d import import_step

shape = import_step(sys.argv[1])
for i, s in enumerate(shape.solids()):
    b = s.bounding_box()
    print(f"{i:3d} vol={s.volume:10.1f} "
          f"x[{b.min.X:7.2f},{b.max.X:7.2f}] y[{b.min.Y:7.2f},{b.max.Y:7.2f}] z[{b.min.Z:7.2f},{b.max.Z:7.2f}] "
          f"size=({b.size.X:6.2f},{b.size.Y:6.2f},{b.size.Z:6.2f})")
