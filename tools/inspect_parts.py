"""List the labeled parts of a STEP assembly with their bounding boxes (mm)."""
import sys
from build123d import import_step


def walk(node, depth=0):
    b = node.bounding_box()
    print(f"{'  ' * depth}{node.label or '?'}: x[{b.min.X:7.2f},{b.max.X:7.2f}] "
          f"y[{b.min.Y:7.2f},{b.max.Y:7.2f}] z[{b.min.Z:7.2f},{b.max.Z:7.2f}]")
    if depth < int(sys.argv[2] if len(sys.argv) > 2 else 2):
        for child in getattr(node, "children", ()):
            walk(child, depth + 1)


walk(import_step(sys.argv[1]))
