"""Write out/preview_<view>.svg line drawings of the assembled case (lid + base)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build123d import Compound, ExportSVG, LineType  # noqa: E402
import case  # noqa: E402

VIEWS = {"iso_fan": (-150, -110, 90), "iso_antenna": (150, 110, 90), "front_ports": (0, -200, 20)}
model = Compound([case.make_lid(), case.make_base()])
out = Path(case.__file__).parent / "out"
for name, origin in VIEWS.items():
    visible, hidden = model.project_to_viewport(origin, viewport_up=(0, 0, 1))
    svg = ExportSVG(scale=4)
    svg.add_layer("v", line_weight=0.3)
    svg.add_layer("h", line_weight=0.15, line_type=LineType.ISO_DOT)
    svg.add_shape(visible, layer="v")
    svg.add_shape(hidden, layer="h")
    svg.write(str(out / f"preview_{name}.svg"))
    print(out / f"preview_{name}.svg")
