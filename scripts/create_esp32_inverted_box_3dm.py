"""Create an editable Rhino 3DM concept for an inverted ESP32-C6 enclosure.

The body, snap-on upper retaining frame, screw-fastened bottom and decorative
overlay reference are laid out side by side. Units are millimetres. Physical
parts remain named meshes so their fit and boolean operations can be inspected
and adjusted in Rhino.
"""

import math
import os
import sys

sys.path.insert(0, "/tmp/codex_rhino3dm")
import rhino3dm


OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models", "current", "esp32_inverted_box_102mm_snap_lid.3dm"
)

# Main assembled envelope.
SIZE_X = 102.0
SIZE_Y = 102.0
BODY_HEIGHT = 32.0
CORNER_R = 5.0
WALL = 3.0
ROOF = 3.0
CEILING_Z = BODY_HEIGHT - ROOF
UNION_OVERLAP = 0.30

# The upper 12 mm of the body is inset by 3 mm on every side. A 1 mm seating
# shoulder is followed by a 2 x 2 mm support-free 45-degree transition; the
# remaining 10 mm are straight.
NECK_HEIGHT = 12.0
NECK_INSET = 3.0
BODY_TAPER_START_INSET = 1.0
NECK_TAPER_HEIGHT = NECK_INSET - BODY_TAPER_START_INSET
NECK_STRAIGHT_HEIGHT = NECK_HEIGHT - NECK_TAPER_HEIGHT
SHOULDER_Z = BODY_HEIGHT - NECK_HEIGHT
TAPER_TOP_Z = SHOULDER_Z + NECK_TAPER_HEIGHT
NECK_X0 = NECK_INSET
NECK_Y0 = NECK_INSET
NECK_X1 = SIZE_X - NECK_INSET
NECK_Y1 = SIZE_Y - NECK_INSET
NECK_OUTER_R = max(0.5, CORNER_R - NECK_INSET)
NECK_INNER_R = 0.5

# Decorative overlay and snap-on retaining frame.
OVERLAY_SIZE = 95.0
OVERLAY_THICK = 4.0
OVERLAY_X0 = (SIZE_X - OVERLAY_SIZE) / 2.0
OVERLAY_Y0 = (SIZE_Y - OVERLAY_SIZE) / 2.0
OVERLAY_CORNER_R = 4.0       # reference only; measure the real overlay
LID_OVERLAP = 4.0
LID_OPENING = OVERLAY_SIZE - 2.0 * LID_OVERLAP  # 87 x 87 mm
LID_OPENING_R = 5.0
LID_TOP = 3.0
LID_TOP_EDGE_CHAMFER = 1.0
LID_NECK_CLEARANCE = 0.20    # per side
LID_OVERLAY_CLEARANCE = 0.20 # per side
LID_POCKET_HEIGHT = 4.10
LID_LOWER_INNER = (NECK_X1 - NECK_X0) + 2.0 * LID_NECK_CLEARANCE
LID_UPPER_INNER = OVERLAY_SIZE + 2.0 * LID_OVERLAY_CLEARANCE
LID_LOWER_WALL = (SIZE_X - LID_LOWER_INNER) / 2.0  # 2.8 mm
LID_UPPER_WALL = (SIZE_X - LID_UPPER_INNER) / 2.0  # 3.3 mm
LID_SEAT_ABOVE_SHOULDER = 0.0
LID_MATING_CHAMFER = NECK_TAPER_HEIGHT
LID_BOTTOM_INNER_WALL = LID_LOWER_WALL - LID_MATING_CHAMFER
LID_BOTTOM_INNER_R = (CORNER_R-BODY_TAPER_START_INSET
                      + LID_NECK_CLEARANCE)
LID_SKIRT_HEIGHT = NECK_STRAIGHT_HEIGHT + LID_MATING_CHAMFER
LID_TOTAL_HEIGHT = LID_SKIRT_HEIGHT + LID_POCKET_HEIGHT + LID_TOP
PART_GAP = 20.0
TOP_LID_X = 0.0
TOP_LID_Z = SHOULDER_Z + LID_SEAT_ABOVE_SHOULDER

# One shallow latch recess and mating printable ramp on every side.
SNAP_LENGTH = 18.0
SNAP_RECESS_HEIGHT = 5.0
SNAP_RECESS_DEPTH = 0.8
SNAP_CHAMFER = 1.0
SNAP_Z0 = TAPER_TOP_Z + 2.0
SNAP_LUG_LENGTH = 16.0
SNAP_LUG_PROJECTION = 0.65
SNAP_LUG_Z0 = SNAP_Z0 - (SHOULDER_Z + LID_SEAT_ABOVE_SHOULDER)
SNAP_LUG_Z1 = SNAP_LUG_Z0 + SNAP_RECESS_HEIGHT
SNAP_WALL_OVERLAP = 1.0

# Bottom plate and its locating lip.
BOTTOM_THICK = 3.0
BOTTOM_LIP_HEIGHT = 6.0
BOTTOM_LIP_WALL = 2.5
BOTTOM_CLEARANCE = 0.30
SCREW_BOTTOM_X = 0.0
SCREW_BOTTOM_Z = -BOTTOM_THICK

# Prototype board reference. ESP32-C6 and components face downward; NTC side
# faces upward. The five NTC holes are centred on a straight line.
PLATE_X = 70.0
PLATE_Y = 50.0
PLATE_THICK = 1.0
PLATE_X0 = 16.0
PLATE_Y0 = 7.0
STANDOFF = 6.0
PLATE_TOP_Z = CEILING_Z - STANDOFF
PLATE_BOTTOM_Z = PLATE_TOP_Z - PLATE_THICK
MOUNT_HOLE_D = 3.0
MOUNT_EDGE_CLEARANCE = 1.0
MOUNT_INSET = MOUNT_EDGE_CLEARANCE + MOUNT_HOLE_D / 2.0
PCB_BOSS_R = 4.5
PCB_INSERT_HOLE_R = 2.05
PCB_INSERT_HOLE_DEPTH = 4.5
PCB_INSERT_ENTRY_R = 2.55
PCB_INSERT_ENTRY_DEPTH = 0.5
PCB_SCREW_HEAD_R = 3.0
PCB_SCREW_HEAD_HEIGHT = 2.5
HEADER_STACK_DOWN = 8.0
ESP_BOARD_AND_COMPONENTS_DOWN = 6.0
COMPONENT_ENVELOPE_DOWN = HEADER_STACK_DOWN + ESP_BOARD_AND_COMPONENTS_DOWN
# Preliminary 2.54 mm grid placement; confirm against the real perfboard.
ESP_HEADER_ROW_XS = (51.56, 76.96)
ESP_HEADER_FIRST_Y = 12.08
ESP_HEADER_LAST_Y = 47.64
ESP_HEADER_HALF_WIDTH = 1.30
ESP_X0 = 50.0
ESP_X1 = 78.0
ESP_USB_FACE_Y = 0.0
ESP_PCB_Y0 = 7.0
ESP_ANTENNA_Y1 = 53.0
NTC_Y = SIZE_Y / 2.0
NTC_XS = (27.0, 39.0, 51.0, 63.0, 75.0)
NTC_HOLE_R = 2.0

# Universal dual-USB opening. It remains completely below the body shoulder,
# so the upper lid cannot cover it.
USB_OPENING_WIDTH = 30.0
USB_OPENING_HEIGHT = 6.0
USB_CENTER_X = 64.0
USB_X0 = USB_CENTER_X - USB_OPENING_WIDTH / 2.0
USB_X1 = USB_CENTER_X + USB_OPENING_WIDTH / 2.0
USB_Z0 = 8.5
USB_Z1 = USB_Z0 + USB_OPENING_HEIGHT

# Bottom fastening: M3 heat-set inserts D4.5 x L4 in the body, and M3 x 8
# DIN 7991 / ISO 10642 countersunk machine screws through the bottom.
BOTTOM_SCREW_XY = [(11.0, 11.0), (91.0, 11.0),
                   (11.0, 91.0), (91.0, 91.0)]
BOTTOM_BOSS_R = 4.5
INSERT_HOLE_R = 2.05        # nominal printed Ø4.1
INSERT_HOLE_DEPTH = 5.0
INSERT_ENTRY_R = 2.55       # Ø5.1 mouth, 0.5 mm x 45° lead-in
INSERT_ENTRY_DEPTH = 0.5
LID_THROUGH_R = 1.75        # Ø3.5 clearance
LID_RECESS_R = 3.50         # Ø7.0 for typical M3 countersunk head
LID_RECESS_DEPTH = 1.75     # 90° included countersink

# Load ribs below the 3 mm roof and along the lower walls.
RIB = 3.0
RIB_DEPTH = 6.0
RIB_DROP = 4.0


def box(x0, y0, z0, x1, y1, z1):
    return prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)


def rounded_loop(x0, y0, x1, y1, radius, segments=10):
    radius = min(radius, (x1-x0)/2.0, (y1-y0)/2.0)
    corners = [(x1-radius, y0+radius, -90.0),
               (x1-radius, y1-radius, 0.0),
               (x0+radius, y1-radius, 90.0),
               (x0+radius, y0+radius, 180.0)]
    result = []
    for cx, cy, start in corners:
        for i in range(segments):
            a = math.radians(start + 90.0*i/segments)
            result.append((cx + radius*math.cos(a), cy + radius*math.sin(a)))
    return result


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


def ring(outer, inner, z0, z1):
    """Closed horizontal ring; outer and inner loops need equal point counts."""
    mesh = rhino3dm.Mesh()
    n = len(outer)
    if len(inner) != n:
        raise ValueError("ring loops must have equal point counts")
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


def tapered_ring(outer0, inner0, outer1, inner1, z0, z1):
    """Closed ring loft between two rounded profiles."""
    n = len(outer0)
    if not (len(inner0) == len(outer1) == len(inner1) == n):
        raise ValueError("tapered ring loops must have equal point counts")
    mesh = rhino3dm.Mesh()
    for loop, z in ((outer0, z0), (inner0, z0),
                    (outer1, z1), (inner1, z1)):
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


def cylinder(cx, cy, z0, z1, radius, segments=40):
    loop = []
    for i in range(segments):
        a = 2.0*math.pi*i/segments
        loop.append((cx+radius*math.cos(a), cy+radius*math.sin(a)))
    return prism(loop, z0, z1)


def frustum(cx, cy, z0, z1, radius0, radius1, segments=40):
    """Closed conical frustum, used as a printable countersink cutter."""
    mesh = rhino3dm.Mesh()
    for radius, z in ((radius0, z0), (radius1, z1)):
        for i in range(segments):
            a = 2.0*math.pi*i/segments
            mesh.Vertices.Add(cx+radius*math.cos(a),
                              cy+radius*math.sin(a), z)
    cb = mesh.Vertices.Add(cx, cy, z0)
    ct = mesh.Vertices.Add(cx, cy, z1)
    for i in range(segments):
        j = (i+1) % segments
        mesh.Faces.AddFace(i, j, segments+j, segments+i)
        mesh.Faces.AddFace(cb, j, i)
        mesh.Faces.AddFace(ct, segments+i, segments+j)
    mesh.Normals.ComputeNormals()
    return mesh


def reverse_faces(mesh):
    """Reverse every face while preserving triangles and quads."""
    for index in range(mesh.Faces.Count):
        a, b, c, d = mesh.Faces[index]
        if c == d:
            mesh.Faces.SetFace(index, c, b, a)
        else:
            mesh.Faces.SetFace(index, d, c, b, a)


def polygon_area(profile):
    area2 = 0.0
    for index, (u0, v0) in enumerate(profile):
        u1, v1 = profile[(index+1) % len(profile)]
        area2 += u0*v1-u1*v0
    return area2/2.0


def extrude_xz(profile, y0, y1):
    """Extrude a closed x/z polygon along Y; useful for snap ramps."""
    mesh = rhino3dm.Mesh()
    n = len(profile)
    for y in (y0, y1):
        for x, z in profile:
            mesh.Vertices.Add(x, y, z)
    c0 = mesh.Vertices.Add(
        sum(x for x, _ in profile)/n, y0, sum(z for _, z in profile)/n
    )
    c1 = mesh.Vertices.Add(
        sum(x for x, _ in profile)/n, y1, sum(z for _, z in profile)/n
    )
    for i in range(n):
        j = (i+1) % n
        mesh.Faces.AddFace(i, n+i, n+j, j)
        mesh.Faces.AddFace(c0, i, j)
        mesh.Faces.AddFace(c1, n+j, n+i)
    if polygon_area(profile) < 0:
        reverse_faces(mesh)
    mesh.Normals.ComputeNormals()
    return mesh


def extrude_yz(profile, x0, x1):
    """Extrude a closed y/z polygon along X; useful for snap ramps."""
    mesh = rhino3dm.Mesh()
    n = len(profile)
    for x in (x0, x1):
        for y, z in profile:
            mesh.Vertices.Add(x, y, z)
    c0 = mesh.Vertices.Add(
        x0, sum(y for y, _ in profile)/n, sum(z for _, z in profile)/n
    )
    c1 = mesh.Vertices.Add(
        x1, sum(y for y, _ in profile)/n, sum(z for _, z in profile)/n
    )
    for i in range(n):
        j = (i+1) % n
        mesh.Faces.AddFace(i, j, n+j, n+i)
        mesh.Faces.AddFace(c0, j, i)
        mesh.Faces.AddFace(c1, n+i, n+j)
    if polygon_area(profile) < 0:
        reverse_faces(mesh)
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


def add_rounded_ring(model, layer, name, outer_bounds, outer_r,
                     inner_bounds, inner_r, z0, z1):
    outer = rounded_loop(*outer_bounds, outer_r)
    inner = rounded_loop(*inner_bounds, inner_r)
    add(model, ring(outer, inner, z0, z1), layer, name)


def add_tapered_rounded_ring(model, layer, name,
                             outer0_bounds, outer0_r,
                             inner0_bounds, inner0_r,
                             outer1_bounds, outer1_r,
                             inner1_bounds, inner1_r,
                             z0, z1):
    outer0 = rounded_loop(*outer0_bounds, outer0_r)
    inner0 = rounded_loop(*inner0_bounds, inner0_r)
    outer1 = rounded_loop(*outer1_bounds, outer1_r)
    inner1 = rounded_loop(*inner1_bounds, inner1_r)
    add(model, tapered_ring(outer0, inner0, outer1, inner1, z0, z1),
        layer, name)


def add_bottom(model, layer, xoff, zoff, name):
    """Add one rounded plate and its inset rounded locating lip."""
    plate = rounded_loop(xoff, 0, xoff+SIZE_X, SIZE_Y, CORNER_R)
    add(model, prism(plate, zoff, zoff+BOTTOM_THICK), layer,
        name + " — пластина 102x102x3")
    ox0 = xoff + WALL + BOTTOM_CLEARANCE
    oy0 = WALL + BOTTOM_CLEARANCE
    ox1 = xoff + SIZE_X - WALL - BOTTOM_CLEARANCE
    oy1 = SIZE_Y - WALL - BOTTOM_CLEARANCE
    outer_r = max(0.5, CORNER_R - WALL - BOTTOM_CLEARANCE)
    ix0, iy0 = ox0+BOTTOM_LIP_WALL, oy0+BOTTOM_LIP_WALL
    ix1, iy1 = ox1-BOTTOM_LIP_WALL, oy1-BOTTOM_LIP_WALL
    inner_r = max(0.5, outer_r-BOTTOM_LIP_WALL)
    outer = rounded_loop(ox0, oy0, ox1, oy1, outer_r)
    inner = rounded_loop(ix0, iy0, ix1, iy1, inner_r)
    add(model, ring(outer, inner,
                    zoff+BOTTOM_THICK-UNION_OVERLAP,
                    zoff+BOTTOM_THICK+BOTTOM_LIP_HEIGHT), layer,
        name + " — вставной бортик")


model = rhino3dm.File3dm()
model.Settings.ModelUnitSystem = rhino3dm.UnitSystem.Millimeters
model.Settings.ModelAbsoluteTolerance = 0.01

body = add_layer(model, "01 Корпус — суженный верх 12 мм, скос 45°",
                 (190, 205, 220, 255))
top_lid = add_layer(model, "02 Верхняя крышка-рамка — защёлки",
                    (235, 175, 90, 255))
screw_bottom = add_layer(model, "03 Нижнее дно — винты M3",
                         (100, 175, 125, 255))
cutters = add_layer(model, "04 Отверстия и впадины для вычитания",
                    (225, 90, 90, 255))
reference = add_layer(model, "05 Электроника — справочно",
                      (90, 150, 220, 255))
overlay_ref = add_layer(model, "06 Накладка 95x95x4 — справочно",
                        (175, 120, 70, 255))

# Lower 102 x 102 wall, a 3 mm high 45-degree taper, and the inset 96 x 96
# straight upper neck.
add_rounded_ring(
    model, body, "Нижняя оболочка 102x102, стенка 3",
    (0, 0, SIZE_X, SIZE_Y), CORNER_R,
    (WALL, WALL, SIZE_X-WALL, SIZE_Y-WALL), CORNER_R-WALL,
    0, SHOULDER_Z,
)
add_tapered_rounded_ring(
    model, body, "Скос корпуса 45° после опорной полки: 100→96",
    (BODY_TAPER_START_INSET, BODY_TAPER_START_INSET,
     SIZE_X-BODY_TAPER_START_INSET,
     SIZE_Y-BODY_TAPER_START_INSET),
    CORNER_R-BODY_TAPER_START_INSET,
    (BODY_TAPER_START_INSET+WALL, BODY_TAPER_START_INSET+WALL,
     SIZE_X-BODY_TAPER_START_INSET-WALL,
     SIZE_Y-BODY_TAPER_START_INSET-WALL),
    max(0.5, CORNER_R-BODY_TAPER_START_INSET-WALL),
    (NECK_X0, NECK_Y0, NECK_X1, NECK_Y1), NECK_OUTER_R,
    (NECK_X0+WALL, NECK_Y0+WALL,
     NECK_X1-WALL, NECK_Y1-WALL), NECK_INNER_R,
    SHOULDER_Z, TAPER_TOP_Z,
)
add_rounded_ring(
    model, body, "Прямой суженный верх 96x96, высота 9",
    (NECK_X0, NECK_Y0, NECK_X1, NECK_Y1), NECK_OUTER_R,
    (NECK_X0+WALL, NECK_Y0+WALL,
     NECK_X1-WALL, NECK_Y1-WALL), NECK_INNER_R,
    TAPER_TOP_Z, CEILING_Z+UNION_OVERLAP,
)
add(model, prism(rounded_loop(NECK_X0, NECK_Y0, NECK_X1, NECK_Y1,
                              NECK_OUTER_R),
                 CEILING_Z-UNION_OVERLAP, BODY_HEIGHT),
    body, "Верх корпуса 96x96x3")

# Roof ribs leave a clear strip around the straight line of five NTC openings.
rz0 = CEILING_Z-RIB_DROP
for name, coords in [
    ("Верхнее ребро переднее — левый участок",
     (6, 6, rz0, 14, 9, CEILING_Z+UNION_OVERLAP)),
    ("Верхнее ребро переднее — правый участок",
     (88, 6, rz0, 96, 9, CEILING_Z+UNION_OVERLAP)),
    ("Верхнее ребро заднее", (6, 93, rz0, 96, 96, CEILING_Z+UNION_OVERLAP)),
    ("Верхнее ребро левое", (6, 9, rz0, 9, 93, CEILING_Z+UNION_OVERLAP)),
    ("Верхнее ребро правое", (93, 9, rz0, 96, 93, CEILING_Z+UNION_OVERLAP)),
    ("Продольное ребро 1B", (33, 59, rz0, 36, 93, CEILING_Z+UNION_OVERLAP)),
    ("Продольное ребро 2B", (66, 59, rz0, 69, 93, CEILING_Z+UNION_OVERLAP)),
    ("Поперечное ребро 2 — ближе к заднему краю",
     (9, 66, rz0, 93, 69, CEILING_Z+UNION_OVERLAP)),
]:
    add(model, box(*coords), body, name)

# Lower-wall ribs stop at the shoulder and stay clear of the bottom locating
# lip. The USB side deliberately has no rib beneath the opening.
vr_z0 = BOTTOM_LIP_HEIGHT+2.0
vr_z1 = SHOULDER_Z
for i, x in enumerate((35.0, 92.0), 1):
    add(model, box(x-RIB/2, WALL-UNION_OVERLAP, vr_z0,
                   x+RIB/2, WALL+RIB_DEPTH, vr_z1),
        body, "Ребро передней стенки вне USB {}".format(i))
for i, x in enumerate((25.5, 51.0, 76.5), 1):
    add(model, box(x-RIB/2, SIZE_Y-WALL-RIB_DEPTH, vr_z0,
                   x+RIB/2, SIZE_Y-WALL+UNION_OVERLAP, vr_z1),
        body, "Ребро задней стенки {}".format(i))
for i, y in enumerate((25.5, 51.0, 76.5), 1):
    add(model, box(SIZE_X-WALL-RIB_DEPTH, y-RIB/2, vr_z0,
                   SIZE_X-WALL+UNION_OVERLAP, y+RIB/2, vr_z1),
        body, "Ребро правой стенки {}".format(i))
for i, y in enumerate((25.5, 51.0, 76.5), 1):
    add(model, box(WALL-UNION_OVERLAP, y-RIB/2, vr_z0,
                   WALL+RIB_DEPTH, y+RIB/2, vr_z1),
        body, "Ребро левой стенки {}".format(i))

# The 30 x 6 mm USB opening needs no local reinforcement. The uninterrupted
# 5.5 mm wall band above it and the remote front-wall ribs provide support
# without obstructing the PCB screw or the USB plugs.

# M3 heat-set insert receivers merge into the corner ribs and roof. The red
# cutters create a Ø4.1 x 5 mm blind hole and a 0.5 mm 45° entry chamfer.
for i, (x, y) in enumerate(BOTTOM_SCREW_XY, 1):
    add(model, cylinder(x, y, 0, CEILING_Z+UNION_OVERLAP, BOTTOM_BOSS_R),
        body, "Угловая стойка под вплавляемую гайку M3 №{}".format(i))
    add(model, cylinder(x, y, -0.1, INSERT_HOLE_DEPTH, INSERT_HOLE_R),
        cutters, "Вычесть Ø4.1, глубина 5, стойка №{}".format(i))
    add(model, frustum(x, y, -0.1, INSERT_ENTRY_DEPTH,
                       INSERT_ENTRY_R, INSERT_HOLE_R),
        cutters, "Входной скос Ø5.1→4.1 стойка №{}".format(i))

# PCB bosses for M3 D4.5 x L4 heat-set inserts. The insert enters from below;
# a 4.5 mm pocket leaves 1.5 mm of plastic before the inner roof surface.
pcb_xy = [(PLATE_X0+MOUNT_INSET, PLATE_Y0+MOUNT_INSET),
          (PLATE_X0+PLATE_X-MOUNT_INSET, PLATE_Y0+MOUNT_INSET),
          (PLATE_X0+MOUNT_INSET, PLATE_Y0+PLATE_Y-MOUNT_INSET),
          (PLATE_X0+PLATE_X-MOUNT_INSET, PLATE_Y0+PLATE_Y-MOUNT_INSET)]
for i, (x, y) in enumerate(pcb_xy, 1):
    add(model, cylinder(x, y, PLATE_TOP_Z, CEILING_Z+UNION_OVERLAP,
                        PCB_BOSS_R),
        body, "Стойка prototype plate Ø9 под втулку M3 №{}".format(i))
    add(model, cylinder(x, y, PLATE_TOP_Z-0.1,
                        PLATE_TOP_Z+PCB_INSERT_HOLE_DEPTH,
                        PCB_INSERT_HOLE_R),
        cutters,
        "Плата: вычесть Ø4.1, глубина 4.5, стойка №{}".format(i))
    add(model, frustum(x, y, PLATE_TOP_Z-0.1,
                       PLATE_TOP_Z+PCB_INSERT_ENTRY_DEPTH,
                       PCB_INSERT_ENTRY_R, PCB_INSERT_HOLE_R),
        cutters,
        "Плата: входной скос Ø5.1→4.1 стойка №{}".format(i))

# Body cutters: five sensor passages, the dual-USB front opening, and one
# 5 mm high chamfered snap recess centred on every face of the 96 x 96 neck.
for i, x in enumerate(NTC_XS, 1):
    # Start below the roof's 0.30 mm union overlap; otherwise a 0.20 mm
    # membrane remains on the inside even though the nominal 3 mm roof is cut.
    add(model, cylinder(x, NTC_Y, CEILING_Z-UNION_OVERLAP-0.1,
                        BODY_HEIGHT+0.1, NTC_HOLE_R),
        cutters, "Верх: сквозное отверстие NTC Ø4 №{}".format(i))
add(model, box(USB_X0, -0.1, USB_Z0, USB_X1, WALL+0.1, USB_Z1),
    cutters, "Корпус: вычесть универсальное окно USB 30x6")

snap_a = SIZE_X/2.0-SNAP_LENGTH/2.0
snap_b = SIZE_X/2.0+SNAP_LENGTH/2.0
snap_z1 = SNAP_Z0 + SNAP_RECESS_HEIGHT
left_recess = [(NECK_X0-0.1, SNAP_Z0),
               (NECK_X0+SNAP_RECESS_DEPTH, SNAP_Z0+SNAP_CHAMFER),
               (NECK_X0+SNAP_RECESS_DEPTH, snap_z1-SNAP_CHAMFER),
               (NECK_X0-0.1, snap_z1)]
right_recess = [(NECK_X1+0.1, SNAP_Z0),
                (NECK_X1-SNAP_RECESS_DEPTH, SNAP_Z0+SNAP_CHAMFER),
                (NECK_X1-SNAP_RECESS_DEPTH, snap_z1-SNAP_CHAMFER),
                (NECK_X1+0.1, snap_z1)]
front_recess = [(NECK_Y0-0.1, SNAP_Z0),
                (NECK_Y0+SNAP_RECESS_DEPTH, SNAP_Z0+SNAP_CHAMFER),
                (NECK_Y0+SNAP_RECESS_DEPTH, snap_z1-SNAP_CHAMFER),
                (NECK_Y0-0.1, snap_z1)]
back_recess = [(NECK_Y1+0.1, SNAP_Z0),
               (NECK_Y1-SNAP_RECESS_DEPTH, SNAP_Z0+SNAP_CHAMFER),
               (NECK_Y1-SNAP_RECESS_DEPTH, snap_z1-SNAP_CHAMFER),
               (NECK_Y1+0.1, snap_z1)]
add(model, extrude_xz(left_recess, snap_a, snap_b),
    cutters, "Впадина защёлки — левая")
add(model, extrude_xz(right_recess, snap_a, snap_b),
    cutters, "Впадина защёлки — правая")
add(model, extrude_yz(front_recess, snap_a, snap_b),
    cutters, "Впадина защёлки — передняя")
add(model, extrude_yz(back_recess, snap_a, snap_b),
    cutters, "Впадина защёлки — задняя")

# Separate upper retaining frame. The outer contour stays 102 x 102. Its
# internal 45-degree chamfer follows the body's 2 mm external taper. The lid
# reaches the shoulder at Z=20 and its 0.8 mm lower wall rests on the 1 mm
# horizontal seating ledge.
lx = TOP_LID_X
lid_inner_bounds = (lx+LID_LOWER_WALL, LID_LOWER_WALL,
                    lx+SIZE_X-LID_LOWER_WALL,
                    SIZE_Y-LID_LOWER_WALL)
lid_bottom_inner_bounds = (
    lx+LID_BOTTOM_INNER_WALL, LID_BOTTOM_INNER_WALL,
    lx+SIZE_X-LID_BOTTOM_INNER_WALL,
    SIZE_Y-LID_BOTTOM_INNER_WALL,
)
add_tapered_rounded_ring(
    model, top_lid, "Крышка: внутренний ответный скос 45°",
    (lx, 0, lx+SIZE_X, SIZE_Y), CORNER_R,
    lid_bottom_inner_bounds, LID_BOTTOM_INNER_R,
    (lx, 0, lx+SIZE_X, SIZE_Y), CORNER_R,
    lid_inner_bounds, NECK_OUTER_R+LID_NECK_CLEARANCE,
    TOP_LID_Z, TOP_LID_Z+LID_MATING_CHAMFER+UNION_OVERLAP,
)
add_rounded_ring(
    model, top_lid, "Крышка: юбка вокруг прямого сужения",
    (lx, 0, lx+SIZE_X, SIZE_Y), CORNER_R,
    lid_inner_bounds,
    NECK_OUTER_R+LID_NECK_CLEARANCE,
    TOP_LID_Z+LID_MATING_CHAMFER,
    TOP_LID_Z+LID_SKIRT_HEIGHT+UNION_OVERLAP,
)
add_rounded_ring(
    model, top_lid, "Крышка: карман 95.4x95.4 под накладку",
    (lx, 0, lx+SIZE_X, SIZE_Y), CORNER_R,
    (lx+LID_UPPER_WALL, LID_UPPER_WALL,
     lx+SIZE_X-LID_UPPER_WALL, SIZE_Y-LID_UPPER_WALL),
    1.0,
    TOP_LID_Z+LID_SKIRT_HEIGHT,
    TOP_LID_Z+LID_SKIRT_HEIGHT+LID_POCKET_HEIGHT+UNION_OVERLAP,
)
opening_margin = (SIZE_X-LID_OPENING)/2.0
add_rounded_ring(
    model, top_lid, "Крышка: верхняя рамка, окно 87x87 R5",
    (lx, 0, lx+SIZE_X, SIZE_Y), CORNER_R,
    (lx+opening_margin, opening_margin,
     lx+SIZE_X-opening_margin, SIZE_Y-opening_margin), LID_OPENING_R,
    TOP_LID_Z+LID_SKIRT_HEIGHT+LID_POCKET_HEIGHT,
    TOP_LID_Z+LID_TOTAL_HEIGHT-LID_TOP_EDGE_CHAMFER,
)
add_tapered_rounded_ring(
    model, top_lid, "Крышка: внешняя верхняя фаска 1x1, 45°",
    (lx, 0, lx+SIZE_X, SIZE_Y), CORNER_R,
    (lx+opening_margin, opening_margin,
     lx+SIZE_X-opening_margin, SIZE_Y-opening_margin), LID_OPENING_R,
    (lx+LID_TOP_EDGE_CHAMFER, LID_TOP_EDGE_CHAMFER,
     lx+SIZE_X-LID_TOP_EDGE_CHAMFER,
     SIZE_Y-LID_TOP_EDGE_CHAMFER),
    CORNER_R-LID_TOP_EDGE_CHAMFER,
    (lx+opening_margin, opening_margin,
     lx+SIZE_X-opening_margin, SIZE_Y-opening_margin), LID_OPENING_R,
    TOP_LID_Z+LID_TOTAL_HEIGHT-LID_TOP_EDGE_CHAMFER,
    TOP_LID_Z+LID_TOTAL_HEIGHT,
)

# Four inward latch teeth, each 5 mm high with 1 mm ramps above and below.
lug_a = SIZE_Y/2.0-SNAP_LUG_LENGTH/2.0
lug_b = SIZE_Y/2.0+SNAP_LUG_LENGTH/2.0
inner_left = lx+LID_LOWER_WALL
inner_right = lx+SIZE_X-LID_LOWER_WALL
left_lug = [(inner_left-SNAP_WALL_OVERLAP, TOP_LID_Z+SNAP_LUG_Z0),
            (inner_left+SNAP_LUG_PROJECTION,
             TOP_LID_Z+SNAP_LUG_Z0+SNAP_CHAMFER),
            (inner_left+SNAP_LUG_PROJECTION,
             TOP_LID_Z+SNAP_LUG_Z1-SNAP_CHAMFER),
            (inner_left-SNAP_WALL_OVERLAP, TOP_LID_Z+SNAP_LUG_Z1)]
right_lug = [(inner_right+SNAP_WALL_OVERLAP, TOP_LID_Z+SNAP_LUG_Z0),
             (inner_right-SNAP_LUG_PROJECTION,
              TOP_LID_Z+SNAP_LUG_Z0+SNAP_CHAMFER),
             (inner_right-SNAP_LUG_PROJECTION,
              TOP_LID_Z+SNAP_LUG_Z1-SNAP_CHAMFER),
             (inner_right+SNAP_WALL_OVERLAP, TOP_LID_Z+SNAP_LUG_Z1)]
add(model, extrude_xz(left_lug, lug_a, lug_b), top_lid,
    "Защёлка крышки — левая")
add(model, extrude_xz(right_lug, lug_a, lug_b), top_lid,
    "Защёлка крышки — правая")

inner_front = LID_LOWER_WALL
inner_back = SIZE_Y-LID_LOWER_WALL
front_lug = [(inner_front-SNAP_WALL_OVERLAP, TOP_LID_Z+SNAP_LUG_Z0),
             (inner_front+SNAP_LUG_PROJECTION,
              TOP_LID_Z+SNAP_LUG_Z0+SNAP_CHAMFER),
             (inner_front+SNAP_LUG_PROJECTION,
              TOP_LID_Z+SNAP_LUG_Z1-SNAP_CHAMFER),
             (inner_front-SNAP_WALL_OVERLAP, TOP_LID_Z+SNAP_LUG_Z1)]
back_lug = [(inner_back+SNAP_WALL_OVERLAP, TOP_LID_Z+SNAP_LUG_Z0),
            (inner_back-SNAP_LUG_PROJECTION,
             TOP_LID_Z+SNAP_LUG_Z0+SNAP_CHAMFER),
            (inner_back-SNAP_LUG_PROJECTION,
             TOP_LID_Z+SNAP_LUG_Z1-SNAP_CHAMFER),
            (inner_back+SNAP_WALL_OVERLAP, TOP_LID_Z+SNAP_LUG_Z1)]
add(model, extrude_yz(front_lug, lx+lug_a, lx+lug_b), top_lid,
    "Защёлка крышки — передняя")
add(model, extrude_yz(back_lug, lx+lug_a, lx+lug_b), top_lid,
    "Защёлка крышки — задняя")

# Screw-fastened bottom shown in its assembled position under the body.
add_bottom(model, screw_bottom, SCREW_BOTTOM_X, SCREW_BOTTOM_Z,
           "Винтовое дно")
for i, (x, y) in enumerate(BOTTOM_SCREW_XY, 1):
    sx, sy = SCREW_BOTTOM_X+x, y
    add(model, cylinder(sx, sy, SCREW_BOTTOM_Z-0.1,
                        SCREW_BOTTOM_Z+BOTTOM_THICK+0.1,
                        LID_THROUGH_R),
        cutters, "Дно: сквозное Ø3.5 №{}".format(i))
    add(model, frustum(sx, sy, SCREW_BOTTOM_Z-0.1,
                       SCREW_BOTTOM_Z+LID_RECESS_DEPTH,
                       LID_RECESS_R, LID_THROUGH_R),
        cutters, "Дно: потай Ø7.0→3.5 №{}".format(i))

# Electronics and sensor references inside the body.
add(model, box(PLATE_X0, PLATE_Y0, PLATE_BOTTOM_Z,
               PLATE_X0+PLATE_X, PLATE_Y0+PLATE_Y, PLATE_TOP_Z),
    reference, "Prototype plate 70x50x1 — сторона NTC вверх")
for i, (x, y) in enumerate(pcb_xy, 1):
    add(model, cylinder(x, y, PLATE_BOTTOM_Z-PCB_SCREW_HEAD_HEIGHT,
                        PLATE_BOTTOM_Z+0.1, PCB_SCREW_HEAD_R),
        reference, "Свободный объём головки винта платы Ø6 №{}".format(i))
for i, row_x in enumerate(ESP_HEADER_ROW_XS, 1):
    add(model, box(row_x-ESP_HEADER_HALF_WIDTH,
                   ESP_HEADER_FIRST_Y-ESP_HEADER_HALF_WIDTH,
                   PLATE_BOTTOM_Z-HEADER_STACK_DOWN,
                   row_x+ESP_HEADER_HALF_WIDTH,
                   ESP_HEADER_LAST_Y+ESP_HEADER_HALF_WIDTH,
                   PLATE_BOTTOM_Z),
        reference,
        "Ряд съёмной гребёнки ESP32-C6, высота 8 №{} (сетка 2.54)".format(i))
esp_top_z = PLATE_BOTTOM_Z-HEADER_STACK_DOWN
esp_bottom_z = esp_top_z-ESP_BOARD_AND_COMPONENTS_DOWN
add(model, box(ESP_X0, ESP_PCB_Y0, esp_bottom_z,
               ESP_X1, ESP_ANTENNA_Y1, esp_top_z),
    reference, "ESP32-C6 28x46, компоненты вниз, габарит 6")
usb_pair_x0 = USB_CENTER_X-23.0/2.0
add(model, box(usb_pair_x0, ESP_USB_FACE_Y, USB_Z0,
               usb_pair_x0+10.0, ESP_PCB_Y0+2.0, USB_Z1),
    reference, "USB-C CH343 — справочный габарит")
add(model, box(usb_pair_x0+13.0, ESP_USB_FACE_Y, USB_Z0,
               usb_pair_x0+23.0, ESP_PCB_Y0+2.0, USB_Z1),
    reference, "USB-C ESP32-C6 — справочный габарит")
for i, x in enumerate(NTC_XS, 1):
    add(model, cylinder(x, NTC_Y, BODY_HEIGHT-0.8,
                        BODY_HEIGHT+1.2, 1.1),
        reference, "NTC 3950 2x2 мм №{}".format(i))
add(model, box(USB_X0, -1, USB_Z0, USB_X1, WALL+1, USB_Z1),
    reference, "Универсальное окно двух USB-C 30x6")

# Existing 95 x 95 x 4 decorative overlay remains separate for inspection.
overlay_x = SIZE_X + PART_GAP
add(model, prism(rounded_loop(overlay_x, 0,
                              overlay_x+OVERLAY_SIZE, OVERLAY_SIZE,
                              OVERLAY_CORNER_R),
                 0, OVERLAY_THICK),
    overlay_ref, "Существующая накладка 95x95x4 — пример R4")
for i, x in enumerate(NTC_XS, 1):
    pocket_x = overlay_x+(x-OVERLAY_X0)
    pocket_y = NTC_Y-OVERLAY_Y0
    add(model, box(pocket_x-1.5, pocket_y-1.5, -0.1,
                   pocket_x+1.5, pocket_y+1.5, 3.1),
        cutters, "Накладка: карман 3x3, глубина 3.1 №{} (справочно)".format(i))

if not model.Write(OUT, 8):
    raise RuntimeError("Failed to write " + OUT)

print(OUT)
print("objects={}; body=102x102x{}; neck=96x96x{}; lid opening={}x{}".format(
    len(model.Objects), BODY_HEIGHT, NECK_HEIGHT, LID_OPENING, LID_OPENING
))
print("layout: assembled body/lids X=0..102; bottom Z=-3..6; top lid Z=20..39.1; overlay X=122..217")
