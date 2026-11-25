"""Orange Pi Zero 3 + USB expansion board desk case, PETG, 4010 side fan, outside Wi-Fi antenna.

Two parts:
- lid: 5-sided box (walls + roof), printed roof down.
- base: flat plate with board standoffs, fits inside the lid, screwed from below.

Coordinates are the ones of the reference STEP (reference/motorbottle-case.stp), mm.
Run: .venv/Scripts/python case.py  ->  out/lid.stl, out/base.stl, out/case.step
"""
import math
from pathlib import Path
from build123d import (Align, Axis, Box, Compound, Cylinder, Plane, Pos, RegularPolygon, Rot, Sketch,
                       export_step, export_stl, extrude, fillet)

# --- Board geometry, read from the reference STEP (tools/inspect_step.py, tools/find_holes.py) ---
PCB_X = (-23.06, 31.94)            # main board 55 x 50.2 x 1.2
PCB_Y = (-26.30, 23.90)
PCB_BOTTOM_Z = 5.15
BOARD_HOLES = [(29.39, -23.75), (29.39, 21.35), (-20.51, 21.35), (-20.51, -23.75)]  # d = 3.0
SHIELD_TOP_Z = 19.32
SHIELD_HOLES = [(-4.31, -5.60), (23.72, 16.70)]                                      # d = 3.0
TALLEST_Z = 35.01                  # stacked USB on the shield
# Port bounding boxes (x0, x1, z0, z1). -Y: main board edge. +Y: shield edge.
PORTS_MINUS_Y = {
    "micro_hdmi": (-16.86, -10.36, 6.53, 9.47),
    "usb_c": (-5.01, -1.81, 7.05, 15.97),
    "usb_a": (2.94, 8.74, 6.85, 20.05),
    "rj45": (10.94, 25.94, 6.35, 19.85),
}
PORTS_PLUS_Y = {
    "usb_x2": (-7.01, 8.59, 16.27, 35.01),
    "audio": (11.50, 18.50, 19.17, 25.17),
}
MICROSD = (14.73, 25.74, 3.29, 4.29)   # card under the board, sticks out on +Y

# --- Case parameters ---
WALL = 2.0
ROOF = 2.0
PLATE = 3.5
PLATE_TOP_Z = PCB_BOTTOM_Z - 4.0
FIT = 0.25                         # plate-to-lid gap per side
HEAD_D, HEAD_H = 6.5, 1.8          # counterbore for an M3 button head (5.7 x 1.65)
BOSS_D = 7.0
# Boss inset from the inner wall: the counterbore keeps 1 mm of plate to the plate edge.
BOSS_INSET = FIT + HEAD_D / 2 + 1.0
SIDE_MARGIN = BOSS_INSET + BOSS_D / 2 + 0.5   # boss stays 0.5 mm off the board edge
PORT_CLEAR = 1.0                   # extra around each port window
MIN_RIB = 2.0                      # thinner wall strips between windows are cut away
NUT_R = 3.3                        # M3 nut corner radius + margin
FAN = 40.0                         # 4010 fan
FAN_HOLE_PITCH = 32.0
GRILLE_D = 38.0                    # fan opening
GRILLE_CELL, GRILLE_RIB = 6.0, 1.4 # hexagon flat-to-flat width, wall between cells
CORNER_R = 3.0                     # outside vertical corners of the lid
SCREW_TAP = 2.9                    # M3 self-tapping into PETG
SCREW_PASS = 3.4
ANT_L, ANT_W = 45.0, 10.0          # stock FPC antenna; check with calipers

X_IN = (PCB_X[0] - SIDE_MARGIN, PCB_X[1] + SIDE_MARGIN)
Y_IN = (-27.40 - 0.4, 26.80 + 0.4)   # port tips + clearance
Z_BOT = PLATE_TOP_Z - PLATE
# Fan nuts sit inside: the low ones must clear the plate, the high ones the roof.
FAN_ZC = PLATE_TOP_Z + NUT_R + FAN_HOLE_PITCH / 2
HEIGHT = max(TALLEST_Z + 1.0 + ROOF, FAN_ZC + FAN_HOLE_PITCH / 2 + NUT_R + ROOF) - Z_BOT
Z_TOP = Z_BOT + HEIGHT
ROOF_IN = Z_TOP - ROOF
X_OUT = (X_IN[0] - WALL, X_IN[1] + WALL)
Y_OUT = (Y_IN[0] - WALL, Y_IN[1] + WALL)
YC = sum(Y_IN) / 2
I = BOSS_INSET
BOSSES = [(X_IN[0] + I, Y_IN[0] + I), (X_IN[0] + I, Y_IN[1] - I),
          (X_IN[1] - I, Y_IN[0] + I), (X_IN[1] - I, Y_IN[1] - I)]
MIN = (Align.MIN, Align.MIN, Align.MIN)


def box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)


def cyl_z(x, y, d, z0, z1):
    return Pos(x, y, z0) * Cylinder(d / 2, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def cyl_x(x0, x1, y, z, d):
    return Pos(x0, y, z) * Rot(0, 90, 0) * Cylinder(d / 2, x1 - x0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def port_windows(ports):
    """Port windows (x0, x1, z0, z1) with clearance. A rib thinner than MIN_RIB between two
    neighbours breaks off, so that gap is opened too (over the z range both windows share)."""
    c = PORT_CLEAR
    wins = sorted((x0 - c, x1 + c, z0 - c, z1 + c) for x0, x1, z0, z1 in ports.values())
    gaps = [(a[1], b[0], max(a[2], b[2]), min(a[3], b[3]))
            for a, b in zip(wins, wins[1:]) if b[0] - a[1] < MIN_RIB]
    return wins + gaps


def fan_grille(x0, depth):
    """Hexagon cells inside the fan circle, as one solid to cut from the -X wall."""
    r = GRILLE_CELL / math.sqrt(3)                 # circumradius from flat-to-flat width
    pitch_y = GRILLE_CELL + GRILLE_RIB
    pitch_z = pitch_y * math.sqrt(3) / 2
    plane = Plane.YZ.offset(x0)                    # local (x, y) = global (Y, Z)
    cells = []
    for row in range(-10, 11):
        shift = pitch_y / 2 if row % 2 else 0.0
        for col in range(-10, 11):
            y, z = col * pitch_y + shift, row * pitch_z
            if math.hypot(y, z) < GRILLE_D / 2 + r / 2:
                cells.append(plane * Pos(YC + y, FAN_ZC + z) * RegularPolygon(r, 6, rotation=30))
    # edge cells are cut back to the fan circle
    return extrude(Sketch() + cells, amount=depth) & cyl_x(x0, x0 + depth, YC, FAN_ZC, GRILLE_D)


def make_lid():
    lid = box(*X_OUT, *Y_OUT, Z_BOT, Z_TOP)
    lid = fillet(lid.edges().filter_by(Axis.Z), CORNER_R) - box(*X_IN, *Y_IN, Z_BOT - 1, ROOF_IN)
    for w in port_windows(PORTS_MINUS_Y):
        lid -= box(w[0], w[1], Y_OUT[0] - 1, Y_IN[0] + 1, w[2], w[3])
    for w in port_windows(PORTS_PLUS_Y):
        lid -= box(w[0], w[1], Y_IN[1] - 1, Y_OUT[1] + 1, w[2], w[3])
    # microSD: notch open to the bottom edge, so the lid slides down past the card
    x0, x1, _, z1 = MICROSD
    lid -= box(x0 - 1.5, x1 + 1.5, Y_IN[1] - 1, Y_OUT[1] + 1, Z_BOT - 1, z1 + 1.5)

    # -X wall: fan intake. Honeycomb of point-up hexagons: prints on a vertical wall
    # without supports, and a 2-pin Dupont plug (5.1 x 2.5) passes through any cell.
    wall = (X_OUT[0] - 1, X_IN[0] + 1)
    lid -= fan_grille(wall[0], wall[1] - wall[0])
    for dy in (-1, 1):
        for dz in (-1, 1):
            lid -= cyl_x(*wall, YC + dy * FAN_HOLE_PITCH / 2, FAN_ZC + dz * FAN_HOLE_PITCH / 2, SCREW_PASS)

    # +X wall: exhaust slots low (air between board and shield), antenna holder high
    wall = (X_IN[1] - 1, X_OUT[1] + 1)
    y = -20.0
    while y + 2.5 <= 20.0:
        lid -= box(*wall, y, y + 2.5, PLATE_TOP_Z + 2, 21.0)
        y += 4.5
    ant_z0 = 25.0
    ant_y0 = YC - ANT_L / 2 - 0.5
    ant_y1 = YC + ANT_L / 2 + 0.5
    rail = 1.2
    for z0 in (ant_z0 - rail, ant_z0 + ANT_W + 0.5):           # top and bottom rails
        lid += box(X_OUT[1], X_OUT[1] + 1.5, ant_y0 - rail, ant_y1 + rail, z0, z0 + rail)
    lid += box(X_OUT[1], X_OUT[1] + 1.5, ant_y1, ant_y1 + rail, ant_z0, ant_z0 + ANT_W + 0.5)  # end stop
    lid -= box(*wall, ant_y0 + 10, ant_y0 + 16, ant_z0 + 2, ant_z0 + 5)   # cable slot, clear of the boss

    # Screw bosses from the roof down to the plate, tied to the corner walls,
    # and 2 posts that keep the shield seated
    for x, y in BOSSES:
        xw = X_IN[0] if x < 0 else X_IN[1]
        yw = Y_IN[0] if y < 0 else Y_IN[1]
        lid += box(min(x, xw), max(x, xw), min(y, yw), max(y, yw), PLATE_TOP_Z, ROOF_IN)
        lid += cyl_z(x, y, BOSS_D, PLATE_TOP_Z, ROOF_IN)
        lid -= cyl_z(x, y, SCREW_TAP, PLATE_TOP_Z - 1, PLATE_TOP_Z + 10)
    for x, y in SHIELD_HOLES:
        lid += cyl_z(x, y, 5.0, SHIELD_TOP_Z + 0.3, ROOF_IN)
    return lid


def make_base():
    base = box(X_IN[0] + FIT, X_IN[1] - FIT, Y_IN[0] + FIT, Y_IN[1] - FIT, Z_BOT, PLATE_TOP_Z)
    for x, y in BOARD_HOLES:
        base += cyl_z(x, y, 6.0, PLATE_TOP_Z, PCB_BOTTOM_Z)
        base -= cyl_z(x, y, SCREW_TAP, PLATE_TOP_Z - 1.5, PCB_BOTTOM_Z + 1)
    for x, y in BOSSES:
        base -= cyl_z(x, y, SCREW_PASS, Z_BOT - 1, PLATE_TOP_Z + 1)
        base -= cyl_z(x, y, HEAD_D, Z_BOT - 1, Z_BOT + HEAD_H)   # counterbore for M3 button head
    return base


if __name__ == "__main__":
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    lid, base = make_lid(), make_base()
    assert lid.is_valid and base.is_valid
    export_stl(lid, str(out / "lid.stl"))
    export_stl(base, str(out / "base.stl"))
    export_step(Compound([lid, base]), str(out / "case.step"))
    print(f"outer {X_OUT[1] - X_OUT[0]:.1f} x {Y_OUT[1] - Y_OUT[0]:.1f} x {HEIGHT:.1f} mm")
