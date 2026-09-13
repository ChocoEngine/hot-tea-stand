"""Validate the final ESP32 enclosure and the agreed boolean feature set."""

import os
import sys

sys.path.insert(0, "/tmp/codex_rhino3dm")
sys.path.insert(0, "/tmp/codex_meshlibs")

import numpy as np
import rhino3dm
import trimesh


HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "current")
FINAL_PATH = os.path.join(HERE, "esp32_inverted_box_102mm_final.3dm")
SOURCE_PATH = os.path.join(HERE, "esp32_inverted_box_102mm_snap_lid.3dm")

EXPECTED = {
    "01 Корпус — финальный manifold mesh": ((0, 0, 0), (102, 102, 32)),
    "02 Верхняя крышка — финальный manifold mesh": ((0, 0, 20), (102, 102, 39.1)),
    "03 Винтовое дно — финальный manifold mesh": ((0, 0, -3), (102, 102, 6)),
}


def as_trimesh(mesh):
    vertices = np.array([(v.X, v.Y, v.Z) for v in mesh.Vertices], dtype=float)
    faces = []
    for face in mesh.Faces:
        if face[2] == face[3]:
            faces.append((face[0], face[1], face[2]))
        else:
            faces.extend(((face[0], face[1], face[2]),
                          (face[0], face[2], face[3])))
    return trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces), process=True)


def component_count(mesh):
    parents = list(range(len(mesh.faces)))
    owners = {}

    def find(value):
        while parents[value] != value:
            parents[value] = parents[parents[value]]
            value = parents[value]
        return value

    def merge(a, b):
        a, b = find(a), find(b)
        if a != b:
            parents[b] = a

    for index, face in enumerate(mesh.faces):
        for a, b in ((face[0], face[1]), (face[1], face[2]),
                     (face[2], face[0])):
            edge = tuple(sorted((int(a), int(b))))
            if edge in owners:
                merge(index, owners[edge])
            else:
                owners[edge] = index
    return len({find(i) for i in range(len(mesh.faces))})


def intersection_volume(meshes):
    overlap = trimesh.boolean.intersection(meshes, engine="manifold")
    if overlap is None or overlap.is_empty:
        return 0.0
    # Seating faces can produce a zero-thickness intersection mesh.  Suppress
    # its harmless divide-by-zero centroid warning and treat it as zero volume.
    with np.errstate(divide="ignore", invalid="ignore"):
        volume = abs(float(overlap.volume))
    return volume if np.isfinite(volume) else 0.0


def vertical_test_cylinder(x, y, z0, z1, radius):
    cylinder = trimesh.creation.cylinder(radius=radius, height=z1-z0,
                                         sections=48)
    cylinder.apply_translation((x, y, (z0+z1)/2.0))
    return cylinder


final = rhino3dm.File3dm.Read(FINAL_PATH)
source = rhino3dm.File3dm.Read(SOURCE_PATH)
if final is None or source is None:
    raise RuntimeError("Could not read final or source model")

failures = []
print_objects = {}
for obj in final.Objects:
    layer_name = final.Layers[obj.Attributes.LayerIndex].Name
    if layer_name in EXPECTED:
        print_objects.setdefault(layer_name, []).append(obj)

for layer_name, expected_bounds in EXPECTED.items():
    objects = print_objects.get(layer_name, [])
    if len(objects) != 1:
        failures.append("{} has {} printable objects, expected 1".format(
            layer_name, len(objects)))
        continue
    geometry = objects[0].Geometry
    manifold, oriented, boundary = geometry.IsManifold(True)
    mesh = as_trimesh(geometry)
    bounds = np.round(mesh.bounds, 3)
    expected = np.asarray(expected_bounds, dtype=float)
    shells = component_count(mesh)
    checks = {
        "valid": geometry.IsValid,
        "closed": geometry.IsClosed,
        "manifold": manifold,
        "oriented": oriented,
        "no_boundary": not boundary,
        "watertight": mesh.is_watertight,
        "winding": mesh.is_winding_consistent,
        "positive_volume": mesh.volume > 0,
        "one_shell": shells == 1,
        "bounds": np.allclose(bounds, expected, atol=0.01),
    }
    for check, passed in checks.items():
        if not passed:
            failures.append("{}: {} failed".format(layer_name, check))
    print("{}: {} volume={:.3f} shells={} bounds={}".format(
        layer_name, checks, mesh.volume, shells, bounds.tolist()))

# In the assembled position the two lids may touch their seating faces, but
# must not occupy the same volume as the body.
print_meshes = {
    layer: as_trimesh(objects[0].Geometry)
    for layer, objects in print_objects.items() if len(objects) == 1
}
body_mesh = print_meshes.get("01 Корпус — финальный manifold mesh")
for other_layer in ("02 Верхняя крышка — финальный manifold mesh",
                    "03 Винтовое дно — финальный manifold mesh"):
    other = print_meshes.get(other_layer)
    if body_mesh is None or other is None:
        continue
    overlap_volume = intersection_volume([body_mesh, other])
    print("assembled overlap body / {}: {:.6f} mm3".format(
        other_layer, overlap_volume))
    if overlap_volume > 0.001:
        failures.append("assembled body/lid overlap is {:.6f} mm3".format(
            overlap_volume))

# The finished body must also leave the complete reference electronics
# envelope unobstructed (plate, screw heads, headers, ESP, USB and NTC probes).
if body_mesh is not None:
    for obj in final.Objects:
        layer_name = final.Layers[obj.Attributes.LayerIndex].Name
        if layer_name != "05 Электроника — справочно":
            continue
        reference_mesh = as_trimesh(obj.Geometry)
        overlap_volume = intersection_volume([body_mesh, reference_mesh])
        if overlap_volume > 0.001:
            failures.append("body obstructs {} by {:.6f} mm3".format(
                obj.Attributes.Name, overlap_volume))

    # A Ø3.6 mm gauge must pass completely through every nominal Ø4 mm NTC
    # opening, including the roof's internal union-overlap zone.
    for index, x in enumerate((27.0, 39.0, 51.0, 63.0, 75.0), 1):
        gauge = vertical_test_cylinder(x, 51.0, 28.5, 32.5, 1.8)
        blocked_volume = intersection_volume([body_mesh, gauge])
        print("NTC passage {} blocked volume: {:.6f} mm3".format(
            index, blocked_volume))
        if blocked_volume > 0.001:
            failures.append("NTC passage {} is not fully open".format(index))

# Confirm that the construction file contains every agreed cutter.  The final
# file intentionally omits the red cutter layer after applying these booleans.
cutter_names = []
for obj in source.Objects:
    layer_name = source.Layers[obj.Attributes.LayerIndex].Name
    if layer_name == "04 Отверстия и впадины для вычитания":
        cutter_names.append(obj.Attributes.Name or "")

feature_counts = {
    "NTC through holes": sum(n.startswith("Верх: сквозное отверстие NTC")
                             for n in cutter_names),
    "USB window": sum(n.startswith("Корпус: вычесть универсальное окно USB")
                      for n in cutter_names),
    "snap recesses": sum(n.startswith("Впадина защёлки") for n in cutter_names),
    "body insert bores": sum(n.startswith("Вычесть Ø4.1") for n in cutter_names),
    "body insert lead-ins": sum(n.startswith("Входной скос Ø5.1")
                                for n in cutter_names),
    "PCB insert bores": sum(n.startswith("Плата: вычесть Ø4.1")
                            for n in cutter_names),
    "PCB insert lead-ins": sum(n.startswith("Плата: входной скос")
                               for n in cutter_names),
    "bottom through holes": sum(n.startswith("Дно: сквозное")
                                for n in cutter_names),
    "bottom countersinks": sum(n.startswith("Дно: потай") for n in cutter_names),
}
expected_counts = {
    "NTC through holes": 5,
    "USB window": 1,
    "snap recesses": 4,
    "body insert bores": 4,
    "body insert lead-ins": 4,
    "PCB insert bores": 4,
    "PCB insert lead-ins": 4,
    "bottom through holes": 4,
    "bottom countersinks": 4,
}
print("boolean features:", feature_counts)
if feature_counts != expected_counts:
    failures.append("boolean feature inventory differs from the agreed set")

final_layers = {layer.Name for layer in final.Layers}
if "04 Отверстия и впадины для вычитания" in final_layers:
    failures.append("final file still contains the cutter layer")

if failures:
    for failure in failures:
        print("FAIL:", failure)
    raise SystemExit(1)

print("PASS: 3 printable parts are valid, closed, watertight, consistently "
      "oriented, positive-volume, and each has exactly one connected shell")
