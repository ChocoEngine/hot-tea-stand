"""Validate the generated ESP32 enclosure 3DM without changing it."""

import os
import sys

sys.path.insert(0, "/tmp/codex_rhino3dm")
import rhino3dm


PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "current",
                    "esp32_inverted_box_102mm_snap_lid.3dm")
model = rhino3dm.File3dm.Read(PATH)
if model is None:
    raise RuntimeError("Cannot read " + PATH)

failures = []
layer_bounds = {}
layer_counts = {}

for obj in model.Objects:
    geometry = obj.Geometry
    name = obj.Attributes.Name
    layer_index = obj.Attributes.LayerIndex
    layer_name = model.Layers[layer_index].Name
    layer_counts[layer_name] = layer_counts.get(layer_name, 0) + 1

    if not isinstance(geometry, rhino3dm.Mesh):
        failures.append(name + ": not a mesh")
        continue
    manifold, oriented, has_boundary = geometry.IsManifold(True)
    if not geometry.IsValid:
        failures.append(name + ": invalid")
    if not geometry.IsClosed:
        failures.append(name + ": open")
    if not manifold or not oriented or has_boundary:
        failures.append(
            name + ": manifold={}, oriented={}, boundary={}".format(
                manifold, oriented, has_boundary
            )
        )

    bbox = geometry.GetBoundingBox()
    values = (bbox.Min.X, bbox.Min.Y, bbox.Min.Z,
              bbox.Max.X, bbox.Max.Y, bbox.Max.Z)
    if layer_name not in layer_bounds:
        layer_bounds[layer_name] = list(values)
    else:
        current = layer_bounds[layer_name]
        current[0] = min(current[0], values[0])
        current[1] = min(current[1], values[1])
        current[2] = min(current[2], values[2])
        current[3] = max(current[3], values[3])
        current[4] = max(current[4], values[4])
        current[5] = max(current[5], values[5])

print("file:", PATH)
print("objects:", len(model.Objects), "layers:", len(model.Layers))
for layer in model.Layers:
    name = layer.Name
    bounds = layer_bounds.get(name)
    print("{}: objects={}, bounds={}".format(
        name, layer_counts.get(name, 0),
        tuple(round(value, 3) for value in bounds) if bounds else None
    ))

if failures:
    for failure in failures:
        print("FAIL:", failure)
    raise SystemExit(1)

print("PASS: every object is valid, closed, manifold and consistently oriented")
