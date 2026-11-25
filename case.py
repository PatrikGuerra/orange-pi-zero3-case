"""Orange Pi Zero 3 + USB expansion board desk case, PETG, 4010 side fan, outside Wi-Fi antenna.

Two parts:
- lid: 5-sided box (walls + roof), printed roof down.
- base: flat plate with board standoffs, fits inside the lid, screwed from below.

Coordinates are the ones of the reference STEP (reference/motorbottle-case.stp), mm.
Run: .venv/Scripts/python case.py  ->  out/lid.stl, out/base.stl, out/case.step
"""
import math
from pathlib import Path
from build123d import (Align, Axis, Box, Compound, Cone, Cylinder, Plane, Pos, RegularPolygon, Rot, Sketch,
                       export_step, export_stl, extrude, fillet)

# --- Board geometry ---
# Main board: official Orange Pi file (oficial/pcb-assy_asm.stp), placed by tools/official_board.py.
# Shield: community model (reference/motorbottle-case.stp), raised 0.1 mm because the
# official PCB is 1.3 mm thick and the reference one 1.2 mm.
PCB_X = (-23.08, 31.92)            # main board 55 x 50 x 1.3
PCB_Y = (-26.24, 23.76)
PCB_BOTTOM_Z = 5.15
BOARD_HOLES = [(29.41, -23.73), (29.41, 21.33), (-20.53, 21.33), (-20.53, -23.73)]  # d = 3.0
SHIELD_DZ = 0.1
SHIELD_TOP_Z = 19.32 + SHIELD_DZ
SHIELD_HOLES = [(-4.31, -5.60), (23.72, 16.70)]                                      # d = 3.0
SHIELD_PCB = 1.4
SHIELD_POST_D = 7.0
SHIELD_SCREW_L = 5.0               # M3 x 5 from under the shield, self-tapping into the post
SHIELD_HEAD_D, SHIELD_HEAD_H = 6.0, 3.0   # room kept under the shield for the screw head
SHIELD_KEEPOUT = (20.43, 25.77, 19.31, 24.65, 21.32 + SHIELD_DZ)  # x0, x1, y0, y1, z1 of a part beside post 2
TALLEST_Z = 35.01 + SHIELD_DZ      # stacked USB on the shield
# -Y: main board (official). Faces = connector fronts where they pass the wall; bodies = whole parts.
PORTS_MINUS_Y = {
    "micro_hdmi": (-17.26, -10.76, 6.63, 9.53),
    "usb_c": (-4.88, -1.72, 7.09, 16.03),
    "usb_a": (3.07, 8.77, 7.05, 20.25),
    "rj45": (10.09, 26.09, 6.96, 20.26),
}
PORT_BODIES_MINUS_Y = {
    "micro_hdmi": (-18.46, -9.56, 5.78, 9.53),
    "usb_c": (-5.56, -1.04, 4.90, 16.33),
    "usb_a": (3.07, 8.77, 3.22, 20.25),
    "rj45": (9.87, 26.31, 3.16, 20.26),
}
PORTS_PLUS_Y = {   # connector faces where they pass the wall (not the whole part)
    "usb_x2": (-6.76, 8.34, 19.32 + SHIELD_DZ, 34.91 + SHIELD_DZ),
    "audio": (12.00, 18.00, 19.17 + SHIELD_DZ, 25.17 + SHIELD_DZ),
}
MICROSD = (14.41, 25.94, 3.29, 4.29)   # card under the board, sticks out on +Y (socket: official)

# --- Case parameters ---
WALL = 2.0
ROOF = 2.0
PLATE = 3.5
PLATE_TOP_Z = PCB_BOTTOM_Z - 4.0
FIT = 0.25                         # plate-to-lid gap per side
HEAD_D, HEAD_H = 6.5, 1.8          # counterbore for an M3 button head (5.7 x 1.65)
# Towers from the roof down to the board holes. 4 x M3 x 16 from below go through the base
# standoffs and the board into the towers, so the same 4 screws hold base + board.
TOWER_D = [6.0, 5.0, 6.0, 6.0]     # per BOARD_HOLES; hole 2 sits in the shield's corner notch
TOWER_RIB = 2.0                    # ribs from each tower to its 2 nearest walls
TOWER_RIB_Z0 = 9.0                 # ribs start above the parts on the board (top at 8.45)
TOWER_FLARE = 3.0                  # cone where each tower meets the roof
BOARD_SCREW_L = 16.0
STANDOFF_D = 6.0
PORT_CLEAR = 1.0                   # margin around each main board port window
MERGED_PORTS = [("usb_a", "rj45")] # ports cut as one window, no wall strip between them
SHIELD_PORT_CLEAR = 1.0            # margin around the shield USB and audio windows (1 to 2 mm)
ROUND_PORTS = {"audio"}            # round connector fronts: cut as a circle, d = front + 2 x margin
MIN_RIB = 1.5                      # thinner wall strips between windows are cut away
FAN = 40.0                         # 4010 fan, inside the case against the -X wall
FAN_T = 10.0
FAN_GAP = 0.3                      # play around the fan
FAN_HOLE_PITCH = 32.0              # fan screws from outside, M3 x 10 into the fan frame holes
GRILLE_D = 38.0                    # fan opening
GRILLE_CELL, GRILLE_RIB = 6.0, 1.4 # hexagon flat-to-flat width, wall between cells
CORNER_R = 3.0                     # outside vertical corners of the lid
SCREW_TAP = 2.9                    # M3 self-tapping into PETG
SCREW_PASS = 3.4
ANT_L, ANT_W = 45.0, 10.0          # stock FPC antenna; check with calipers

# -X: room for the fan + play, kept 0.3 mm off the board edge and the base standoffs (d 6).
BAY_DEPTH = FAN_T + FAN_GAP
BAY_END_X = min(PCB_X[0], min(x for x, _ in BOARD_HOLES) - STANDOFF_D / 2) - 0.3
X_IN = (BAY_END_X - BAY_DEPTH, PCB_X[1] + 0.5)
SHIELD_EDGE_Y = 24.70              # shield PCB edge; its USB and audio tips are at y = 26.80
# -Y: port tips + clearance. +Y: wall right at the shield edge, so the shield ports sit
# 0.3 mm behind the outside face (near flush) instead of 2.4 mm deep.
Y_IN = (-27.40 - 0.4, SHIELD_EDGE_Y + 0.4)
Z_BOT = PLATE_TOP_Z - PLATE
# The fan stands on the base plate; the roof clears its top.
FAN_ZC = PLATE_TOP_Z + FAN_GAP + FAN / 2
HEIGHT = max(TALLEST_Z + 1.0 + ROOF, FAN_ZC + FAN / 2 + FAN_GAP + ROOF) - Z_BOT
Z_TOP = Z_BOT + HEIGHT
ROOF_IN = Z_TOP - ROOF
X_OUT = (X_IN[0] - WALL, X_IN[1] + WALL)
Y_OUT = (Y_IN[0] - WALL, Y_IN[1] + WALL)
YC = sum(Y_IN) / 2
PCB_TOP_Z = PCB_BOTTOM_Z + 1.3
MIN = (Align.MIN, Align.MIN, Align.MIN)


def box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)


def cyl_z(x, y, d, z0, z1):
    return Pos(x, y, z0) * Cylinder(d / 2, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def cyl_x(x0, x1, y, z, d):
    return Pos(x0, y, z) * Rot(0, 90, 0) * Cylinder(d / 2, x1 - x0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def round_window(port, c):
    """Circle through the +Y wall around a round connector front (x0, x1, z0, z1)."""
    x0, x1, z0, z1 = port
    d = max(x1 - x0, z1 - z0) + 2 * c
    length = Y_OUT[1] - Y_IN[1] + 2
    return Pos((x0 + x1) / 2, Y_IN[1] - 1 + length / 2, (z0 + z1) / 2) * Rot(90, 0, 0) * Cylinder(d / 2, length)


def port_windows(ports, c=None, merge=()):
    """Port windows (x0, x1, z0, z1) with margin c. Each group in merge becomes one window
    around all its ports. A rib thinner than MIN_RIB between two neighbours breaks off,
    so that gap is opened too (over the z range both windows share)."""
    c = PORT_CLEAR if c is None else c
    grown = {k: (x0 - c, x1 + c, z0 - c, z1 + c) for k, (x0, x1, z0, z1) in ports.items()}
    for group in merge:
        ws = [grown.pop(k) for k in group]
        grown["+".join(group)] = (min(w[0] for w in ws), max(w[1] for w in ws),
                                  min(w[2] for w in ws), max(w[3] for w in ws))
    wins = sorted(grown.values())
    gaps = [(a[1], b[0], max(a[2], b[2]), min(a[3], b[3]))
            for a, b in zip(wins, wins[1:]) if 0 < b[0] - a[1] < MIN_RIB]
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


def microsd_notch():
    x0, x1, _, z1 = MICROSD
    return box(x0 - 1.5, x1 + 1.5, Y_IN[1] - 1, Y_OUT[1] + 1, Z_BOT - 1, z1 + 1.5)


def make_lid():
    lid = box(*X_OUT, *Y_OUT, Z_BOT, Z_TOP)
    lid = fillet(lid.edges().filter_by(Axis.Z), CORNER_R) - box(*X_IN, *Y_IN, Z_BOT - 1, ROOF_IN)
    for w in port_windows(PORTS_MINUS_Y, PORT_CLEAR, MERGED_PORTS):
        lid -= box(w[0], w[1], Y_OUT[0] - 1, Y_IN[0] + 1, w[2], w[3])
    # +Y: the shield ports reach into the wall. The windows stay closed below; the PETG
    # wall flexes out over the ports when the lid goes on.
    square = {k: v for k, v in PORTS_PLUS_Y.items() if k not in ROUND_PORTS}
    for w in port_windows(square, SHIELD_PORT_CLEAR):
        lid -= box(w[0], w[1], Y_IN[1] - 1, Y_OUT[1] + 1, w[2], w[3])
    for k in ROUND_PORTS:
        lid -= round_window(PORTS_PLUS_Y[k], SHIELD_PORT_CLEAR)
    # microSD: notch open to the bottom edge, so the lid slides down past the card
    lid -= microsd_notch()

    # -X wall: fan intake. Honeycomb of point-up hexagons: prints on a vertical wall
    # without supports, and a 2-pin Dupont plug (5.1 x 2.5) passes through any cell.
    wall = (X_OUT[0] - 1, X_IN[0] + 1)
    lid -= fan_grille(wall[0], wall[1] - wall[0])
    # Fan screws from outside through the wall into the fan frame
    p = FAN_HOLE_PITCH / 2
    for dy in (-p, p):
        for dz in (-p, p):
            lid -= cyl_x(*wall, YC + dy, FAN_ZC + dz, SCREW_PASS)

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
    lid -= box(*wall, ant_y0 + 10, ant_y0 + 16, ant_z0 + 2, ant_z0 + 5)   # cable slot

    # Towers from the roof down to the board top at its 4 holes, cut flat where a
    # -Y port (HDMI, RJ45) comes within reach. The base screws thread into them.
    bite = BOARD_SCREW_L - (PCB_TOP_Z - Z_BOT)
    for (x, y), d in zip(BOARD_HOLES, TOWER_D):
        tower = cyl_z(x, y, d, PCB_TOP_Z, ROOF_IN)
        # Ribs to the nearest X and Y walls, above the parts on the board
        xw = X_IN[0] if x < 0 else X_IN[1]
        yw = Y_IN[0] if y < 0 else Y_IN[1]
        h = TOWER_RIB / 2
        tower += box(min(x, xw), max(x, xw), y - h, y + h, TOWER_RIB_Z0, ROOF_IN)
        tower += box(x - h, x + h, min(y, yw), max(y, yw), TOWER_RIB_Z0, ROOF_IN)
        # Flare where the tower meets the roof
        tower += Pos(x, y, ROOF_IN - TOWER_FLARE) * Cone(d / 2, d / 2 + TOWER_FLARE, TOWER_FLARE,
                                                       align=(Align.CENTER, Align.CENTER, Align.MIN))
        tower -= box(X_IN[0], X_IN[0] + FAN_T + 2 * FAN_GAP, YC - FAN / 2 - FAN_GAP, YC + FAN / 2 + FAN_GAP,
                     PLATE_TOP_Z, ROOF_IN)   # keep the fan's space clear
        for x0, x1, _, z1 in PORT_BODIES_MINUS_Y.values():
            tower -= box(x0 - 0.3, x1 + 0.3, Y_IN[0] - 1, 0, PCB_TOP_Z - 1, z1 + 0.3)
        lid += tower
        lid -= cyl_z(x, y, SCREW_TAP, PCB_TOP_Z - 1, PCB_TOP_Z + bite + 1.5)
    # Shield posts: the shield is screwed to the lid with M3 x 5 from below (blind hole,
    # roof stays closed), so lid + shield go on together and plug onto the 13-pin header.
    keep = box(SHIELD_KEEPOUT[0] - 0.3, SHIELD_KEEPOUT[1] + 0.3, SHIELD_KEEPOUT[2] - 0.3,
               SHIELD_KEEPOUT[3] + 0.3, SHIELD_TOP_Z, SHIELD_KEEPOUT[4] + 0.3)
    depth = SHIELD_SCREW_L - SHIELD_PCB + 1.5
    for x, y in SHIELD_HOLES:
        lid += cyl_z(x, y, SHIELD_POST_D, SHIELD_TOP_Z + 0.05, ROOF_IN) - keep   # 0.05: model rounding
        lid -= cyl_z(x, y, SCREW_TAP, SHIELD_TOP_Z - 1, SHIELD_TOP_Z + depth)
    return lid


def make_fan():
    """Simple 4010 fan (frame, 38 mm bore, hub, 4 holes) screwed to the inside of the -X wall."""
    x0 = X_IN[0] + 0.05
    frame = box(x0, x0 + FAN_T, YC - FAN / 2, YC + FAN / 2, FAN_ZC - FAN / 2, FAN_ZC + FAN / 2)
    frame -= cyl_x(x0, x0 + FAN_T, YC, FAN_ZC, 38.0)
    for dy in (-FAN_HOLE_PITCH / 2, FAN_HOLE_PITCH / 2):
        for dz in (-FAN_HOLE_PITCH / 2, FAN_HOLE_PITCH / 2):
            frame -= cyl_x(x0, x0 + FAN_T, YC + dy, FAN_ZC + dz, 3.4)
    return frame + cyl_x(x0, x0 + FAN_T, YC, FAN_ZC, 16.0)


def make_base():
    base = box(X_IN[0] + FIT, X_IN[1] - FIT, Y_IN[0] + FIT, Y_IN[1] - FIT, Z_BOT, PLATE_TOP_Z)
    for x, y in BOARD_HOLES:
        # Standoff with a through hole: the M3 x 16 goes base -> board -> tower. No head
        # counterbore: the holes sit too close to the plate edge; feet lift the heads.
        base += cyl_z(x, y, STANDOFF_D, PLATE_TOP_Z, PCB_BOTTOM_Z)
        base -= cyl_z(x, y, SCREW_PASS, Z_BOT - 1, PCB_BOTTOM_Z + 1)
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
