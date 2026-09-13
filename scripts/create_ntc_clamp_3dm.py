"""Create a Rhino 3DM example of a printable clamp for one epoxy-bead NTC.

The clamp presses the bead directly against a wide washer through a thin film
of thermal paste. Units are millimetres; objects remain separate and named.
"""

import math
import os
import sys

sys.path.insert(0, "/tmp/codex_rhino3dm")
import rhino3dm

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "models", "examples", "ntc_washer_clamp_example.3dm")


def prism(loop, z0, z1):
    mesh = rhino3dm.Mesh()
    n = len(loop)
    for x, y in loop:
        mesh.Vertices.Add(x, y, z0)
    for x, y in loop:
        mesh.Vertices.Add(x, y, z1)
    cb = mesh.Vertices.Add(sum(x for x, _ in loop)/n,
                           sum(y for _, y in loop)/n, z0)
    ct = mesh.Vertices.Add(sum(x for x, _ in loop)/n,
                           sum(y for _, y in loop)/n, z1)
    for i in range(n):
        j = (i+1) % n
        mesh.Faces.AddFace(i, j, n+j, n+i)
        mesh.Faces.AddFace(cb, j, i)
        mesh.Faces.AddFace(ct, n+i, n+j)
    mesh.Normals.ComputeNormals()
    return mesh


def box(x0, y0, z0, x1, y1, z1):
    return prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)


def circle_loop(cx, cy, radius, segments=32):
    return [(cx+radius*math.cos(2*math.pi*i/segments),
             cy+radius*math.sin(2*math.pi*i/segments))
            for i in range(segments)]


def cylinder(cx, cy, z0, z1, radius):
    return prism(circle_loop(cx, cy, radius), z0, z1)


def ring(cx, cy, z0, z1, outer_r, inner_r, segments=32):
    outer = circle_loop(cx, cy, outer_r, segments)
    inner = circle_loop(cx, cy, inner_r, segments)
    mesh = rhino3dm.Mesh()
    n = segments
    for z in (z0, z1):
        for loop in (outer, inner):
            for x, y in loop:
                mesh.Vertices.Add(x, y, z)
    ob, ib, ot, it = 0, n, 2*n, 3*n
    for i in range(n):
        j = (i+1) % n
        mesh.Faces.AddFace(ob+i, ob+j, ot+j, ot+i)
        mesh.Faces.AddFace(ib+j, ib+i, it+i, it+j)
        mesh.Faces.AddFace(ot+i, ot+j, it+j, it+i)
        mesh.Faces.AddFace(ob+j, ob+i, ib+i, ib+j)
    mesh.Normals.ComputeNormals()
    return mesh


def add_layer(model, name, color):
    layer = rhino3dm.Layer()
    layer.Name = name
    layer.Color = color
    return model.Layers.Add(layer)


def add(model, geometry, layer, name):
    attr = rhino3dm.ObjectAttributes()
    attr.LayerIndex = layer
    attr.Name = name
    model.Objects.AddMesh(geometry, attr)


model = rhino3dm.File3dm()
model.Settings.ModelUnitSystem = rhino3dm.UnitSystem.Millimeters
model.Settings.ModelAbsoluteTolerance = 0.01

clamp_layer = add_layer(model, "01 Прижим — печатная деталь", (95, 175, 120, 255))
body_layer = add_layer(model, "02 Стойки корпуса — объединить с верхом", (190, 205, 220, 255))
sensor_layer = add_layer(model, "03 Шайба и NTC — справочно", (220, 165, 70, 255))
cut_layer = add_layer(model, "04 Отверстия M2 — вычесть", (225, 80, 80, 255))

# Reference geometry: M4 wide washer 12 x 4.3 x 1 mm and a typical epoxy bead.
add(model, ring(0, 0, 7.0, 8.0, 6.0, 2.15), sensor_layer,
    "Широкая шайба M4 Ø12, отверстие Ø4.3")
add(model, cylinder(0, 0, 3.5, 7.0, 2.0), sensor_layer,
    "NTC эпоксидная капля Ø4x3.5 — касается шайбы")

# Two Ø5 bosses descend from the underside of the top panel.
for i, x in enumerate((-8.0, 8.0), 1):
    add(model, cylinder(x, 0, 1.5, 7.0, 2.5), body_layer,
        "Стойка прижима M2 №{}".format(i))
    add(model, cylinder(x, 0, 0.8, 6.2, 0.8), cut_layer,
        "Вычесть пилот Ø1.6 под M2 №{}".format(i))

# Printable bridge: 1.5 mm end pads, a slightly thinner flexible middle, and a
# Ø5 pressure button touching the underside of the NTC bead.
add(model, box(-11.0, -4.0, 0, -5.0, 4.0, 1.5), clamp_layer,
    "Левая площадка прижима")
add(model, box(5.0, -4.0, 0, 11.0, 4.0, 1.5), clamp_layer,
    "Правая площадка прижима")
add(model, box(-5.5, -3.0, 0.3, 5.5, 3.0, 1.3), clamp_layer,
    "Гибкая перемычка 1 мм")
add(model, cylinder(0, 0, 1.3, 3.5, 2.5), clamp_layer,
    "Нажимная площадка Ø5")

# M2 clearance cutters through the two clamp pads.
for i, x in enumerate((-8.0, 8.0), 1):
    add(model, cylinder(x, 0, -0.1, 1.7, 1.1), cut_layer,
        "Вычесть проход Ø2.2 в прижиме №{}".format(i))

if not model.Write(OUT, 8):
    raise RuntimeError("Failed to write " + OUT)
print(OUT)
print("objects={}".format(len(model.Objects)))
