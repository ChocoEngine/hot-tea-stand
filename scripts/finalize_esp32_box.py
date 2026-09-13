"""Create the final three-part ESP32 enclosure with manifold booleans."""

import os
import sys

sys.path.insert(0, "/tmp/codex_rhino3dm")
sys.path.insert(0, "/tmp/codex_meshlibs")

import numpy as np
import rhino3dm
import trimesh


HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "current")
SOURCE = os.path.join(HERE, "esp32_inverted_box_102mm_snap_lid.3dm")
OUT = os.path.join(HERE, "esp32_inverted_box_102mm_final.3dm")

BODY_LAYER = "01 Корпус — суженный верх 12 мм, скос 45°"
TOP_LAYER = "02 Верхняя крышка-рамка — защёлки"
BOTTOM_LAYER = "03 Нижнее дно — винты M3"
CUTTER_LAYER = "04 Отверстия и впадины для вычитания"
REFERENCE_LAYER = "05 Электроника — справочно"
OVERLAY_LAYER = "06 Накладка 95x95x4 — справочно"


def rhino_to_trimesh(mesh):
    vertices = np.array([(v.X, v.Y, v.Z) for v in mesh.Vertices], dtype=float)
    faces = []
    for face in mesh.Faces:
        if face[2] == face[3]:
            faces.append((face[0], face[1], face[2]))
        else:
            faces.extend(((face[0], face[1], face[2]),
                          (face[0], face[2], face[3])))
    return positive_volume(trimesh.Trimesh(
        vertices=vertices, faces=np.asarray(faces), process=True))


def trimesh_to_rhino(source):
    mesh = rhino3dm.Mesh()
    for vertex in source.vertices:
        mesh.Vertices.Add(float(vertex[0]), float(vertex[1]), float(vertex[2]))
    for face in source.faces:
        mesh.Faces.AddFace(int(face[0]), int(face[1]), int(face[2]))
    mesh.Normals.ComputeNormals()
    mesh.Compact()
    return mesh


def positive_volume(mesh):
    result = mesh.copy()
    result.merge_vertices()
    result.remove_unreferenced_vertices()
    if result.volume < 0:
        result.invert()
    if not result.is_watertight or not result.is_winding_consistent:
        raise RuntimeError("Input is not a consistently oriented closed volume")
    return result


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


def boolean_union(meshes, label):
    result = trimesh.boolean.union(meshes, engine="manifold")
    if result is None or result.is_empty:
        raise RuntimeError(label + " union failed")
    return require_final(result, label)


def boolean_difference(source, cutters, label):
    result = trimesh.boolean.difference([source] + cutters, engine="manifold")
    if result is None or result.is_empty:
        raise RuntimeError(label + " difference failed")
    return require_final(result, label)


def require_final(mesh, label):
    result = positive_volume(mesh)
    shells = component_count(result)
    if shells != 1:
        raise RuntimeError("{} has {} connected shells".format(label, shells))
    return result


def is_body_cutter(name):
    return (name.startswith("Вычесть Ø4.1") or
            name.startswith("Входной скос Ø5.1") or
            name.startswith("Плата: вычесть Ø4.1") or
            name.startswith("Плата: входной скос") or
            name.startswith("Верх: сквозное отверстие NTC") or
            name.startswith("Корпус: вычесть универсальное окно USB") or
            name.startswith("Впадина защёлки"))


def is_bottom_cutter(name):
    return name.startswith("Дно: сквозное") or name.startswith("Дно: потай")


def add_layer(model, name, color):
    layer = rhino3dm.Layer()
    layer.Name = name
    layer.Color = color
    return model.Layers.Add(layer)


def add_mesh(model, mesh, layer, name):
    attributes = rhino3dm.ObjectAttributes()
    attributes.LayerIndex = layer
    attributes.Name = name
    model.Objects.AddMesh(mesh, attributes)


model = rhino3dm.File3dm.Read(SOURCE)
if model is None:
    raise RuntimeError("Cannot read " + SOURCE)

grouped = {}
references = []
for obj in model.Objects:
    layer_name = model.Layers[obj.Attributes.LayerIndex].Name
    name = obj.Attributes.Name or ""
    if not isinstance(obj.Geometry, rhino3dm.Mesh):
        continue
    grouped.setdefault(layer_name, []).append((name, obj.Geometry))
    if layer_name in (REFERENCE_LAYER, OVERLAY_LAYER):
        references.append((layer_name, name, obj.Geometry))

body_parts = [rhino_to_trimesh(mesh) for _, mesh in grouped[BODY_LAYER]]
top_parts = [rhino_to_trimesh(mesh) for _, mesh in grouped[TOP_LAYER]]
bottom_parts = [rhino_to_trimesh(mesh) for _, mesh in grouped[BOTTOM_LAYER]]
body_cutters = [rhino_to_trimesh(mesh) for name, mesh in grouped[CUTTER_LAYER]
                if is_body_cutter(name)]
bottom_cutters = [rhino_to_trimesh(mesh) for name, mesh in grouped[CUTTER_LAYER]
                  if is_bottom_cutter(name)]

body = boolean_difference(boolean_union(body_parts, "body"),
                          body_cutters, "body after cutters")
top = boolean_union(top_parts, "top lid")
bottom = boolean_difference(boolean_union(bottom_parts, "bottom lid"),
                            bottom_cutters, "bottom lid after cutters")

final = rhino3dm.File3dm()
final.Settings.ModelUnitSystem = rhino3dm.UnitSystem.Millimeters
final.Settings.ModelAbsoluteTolerance = 0.01
body_layer = add_layer(final, "01 Корпус — финальный manifold mesh",
                       (190, 205, 220, 255))
top_layer = add_layer(final, "02 Верхняя крышка — финальный manifold mesh",
                      (235, 175, 90, 255))
bottom_layer = add_layer(final, "03 Винтовое дно — финальный manifold mesh",
                         (100, 175, 125, 255))
reference_layer = add_layer(final, REFERENCE_LAYER, (90, 150, 220, 255))
overlay_layer = add_layer(final, OVERLAY_LAYER, (175, 120, 70, 255))

add_mesh(final, trimesh_to_rhino(body), body_layer,
         "Корпус — отверстия и впадины вычтены")
add_mesh(final, trimesh_to_rhino(top), top_layer,
         "Верхняя крышка-рамка — единая деталь")
add_mesh(final, trimesh_to_rhino(bottom), bottom_layer,
         "Винтовое дно — отверстия и потаи вычтены")
for layer_name, name, mesh in references:
    layer = reference_layer if layer_name == REFERENCE_LAYER else overlay_layer
    add_mesh(final, mesh, layer, name)

if not final.Write(OUT, 8):
    raise RuntimeError("Cannot write " + OUT)

for label, mesh in (("body", body), ("top_lid", top), ("bottom", bottom)):
    print("{}: watertight={} winding={} shells={} volume={:.3f} bounds={}".format(
        label, mesh.is_watertight, mesh.is_winding_consistent,
        component_count(mesh), mesh.volume, np.round(mesh.bounds, 3).tolist()))
print("body_cutters={} bottom_cutters={} references={}".format(
    len(body_cutters), len(bottom_cutters), len(references)))
print(OUT)
