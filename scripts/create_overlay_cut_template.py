"""Exact planar 95 mm square with R5 corners for Rhino, in millimetres."""
import math
from pathlib import Path
import sys

sys.path.insert(0, '/tmp/codex_rhino3dm')
import rhino3dm as r

p = lambda x, y: r.Point3d(x, y, 0)
k = 5 / math.sqrt(2)
curve = r.PolyCurve()
segments = [
    r.Line(p(5, 0), p(90, 0)),
    r.Arc(p(90, 0), p(90+k, 5-k), p(95, 5)),
    r.Line(p(95, 5), p(95, 90)),
    r.Arc(p(95, 90), p(90+k, 90+k), p(90, 95)),
    r.Line(p(90, 95), p(5, 95)),
    r.Arc(p(5, 95), p(5-k, 90+k), p(0, 90)),
    r.Line(p(0, 90), p(0, 5)),
    r.Arc(p(0, 5), p(5-k, 5-k), p(5, 0)),
]
for segment in segments:
    assert curve.Append(segment)
assert curve.IsValid and curve.IsClosed
model = r.File3dm()
model.Settings.ModelUnitSystem = r.UnitSystem.Millimeters
model.Settings.ModelAbsoluteTolerance = 0.001
layer = r.Layer()
layer.Name = 'Шаблон накладки 95x95 R5'
attr = r.ObjectAttributes()
attr.LayerIndex = model.Layers.Add(layer)
attr.Name = 'Контур 95x95 мм — четыре дуги R5'
model.Objects.AddCurve(curve, attr)
path = Path(__file__).resolve().parents[1] / 'models' / 'templates' / 'overlay_template_95x95_R5.3dm'
assert model.Write(str(path), 8)
check = r.File3dm.Read(str(path))
geometry = check.Objects[0].Geometry
bbox = geometry.GetBoundingBox()
assert geometry.IsClosed and geometry.IsValid
assert abs(bbox.Max.X-bbox.Min.X-95) < 1e-6
assert abs(bbox.Max.Y-bbox.Min.Y-95) < 1e-6
print(path)
print('PASS: one closed planar curve, 95 x 95 mm, four exact R5 arcs')
