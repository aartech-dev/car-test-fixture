"""
AART setup block lid + box, metric, v2.
Fixes the rebate so it runs around ALL four sides of the lid (the previous
wire/translate/extrude pattern produced a partial cut), and rebuilds the box:
same external length/width as the lid, 30 mm tall, rim rebated to take the lid.
All parameters in mm.
"""
import cadquery as cq

def box_at(l, w, h, x, y, z):
    """Axis-aligned solid box with min corner at (x, y, z)."""
    return cq.Workplane("XY").box(l, w, h, centered=False).translate((x, y, z))

# ---------------- Lid (setup block) parameters ----------------
BLOCK_L, BLOCK_W, BLOCK_T = 203.2, 101.6, 9.525

SLOT_W, SLOT_LEN          = 3.505, 60.96
BRAID_W, BRAID_LEN        = 8.636, 60.96
BRAID_DEPTH               = 1.778

TIRE_HOLE_L, TIRE_HOLE_W  = 50.8, 25.4
TIRE_EDGE_FROM_REAR       = 38.1
TIRE_Y_CENTERS            = [25.4, 76.2]
TIRE_CORNER_R             = 3.175

CROSS_SLOT_W   = 0.75              # braid feed-through slots, through the lid
CROSS_SLOT_END = 5.0               # distance of slot centres from each channel end
REBATE_IN    = 1.0                 # rebate 1 mm in from every edge
REBATE_DEPTH = BLOCK_T / 2.0       # 4.7625 mm, tongue on the bottom face

# ---------------- Box parameters ----------------
BOX_H         = 30.0               # external height
FIT_CLEARANCE = 0.2                # per side, tongue-to-opening (PETG-friendly)
BOX_WALL      = 3.0                # wall thickness below the rim rebate
BOX_FLOOR     = 2.5                # floor thickness

SOCKET_HOLE_D   = 12.0             # panel hole for 4 mm banana sockets
SOCKET_SPACING  = 20.0             # centre-to-centre, symmetric about width centre
SOCKET_Z        = 15.0             # hole centre height above box bottom
SOCKET_END_X    = 0.0              # which short side: 0.0 = guide-slot end, BLOCK_L = rear

SOCKET3_COUNT   = 3                # holes on the opposite (rear) short wall
SOCKET3_SPACING = 20.0            # centre-to-centre, symmetric about width centre

# ================= Lid =================
yc = BLOCK_W / 2.0
lid = box_at(BLOCK_L, BLOCK_W, BLOCK_T, 0, 0, 0)

def open_ended_slot(width, length, y_center):
    r = width / 2.0
    return (cq.Workplane("XY")
            .moveTo(-1.0, y_center - r)
            .lineTo(length - r, y_center - r)
            .threePointArc((length, y_center), (length - r, y_center + r))
            .lineTo(-1.0, y_center + r)
            .close())

lid = lid.cut(open_ended_slot(SLOT_W, SLOT_LEN, yc)
              .extrude(BLOCK_T + 2).translate((0, 0, -1)))

for sign in (+1, -1):
    y_off = yc + sign * (SLOT_W + BRAID_W) / 2.0
    lid = lid.cut(open_ended_slot(BRAID_W, BRAID_LEN, y_off)
                  .extrude(BRAID_DEPTH + 1)
                  .translate((0, 0, BLOCK_T - BRAID_DEPTH)))

# braid feed-through slots: 0.75 mm wide, through the lid, across each
# braid channel, 5 mm from each end of the channel (4 slots total)
for sign in (+1, -1):
    y_off = yc + sign * (SLOT_W + BRAID_W) / 2.0
    for x_c in (CROSS_SLOT_END, BRAID_LEN - CROSS_SLOT_END):
        lid = lid.cut(box_at(CROSS_SLOT_W, BRAID_W, BLOCK_T + 2,
                             x_c - CROSS_SLOT_W/2.0, y_off - BRAID_W/2.0, -1))

x0 = BLOCK_L - TIRE_EDGE_FROM_REAR - TIRE_HOLE_L
for y in TIRE_Y_CENTERS:
    lid = lid.cut(cq.Workplane("XY")
                  .center(x0 + TIRE_HOLE_L/2.0, y)
                  .rect(TIRE_HOLE_L, TIRE_HOLE_W)
                  .extrude(BLOCK_T + 2).translate((0, 0, -1))
                  .edges("|Z").fillet(TIRE_CORNER_R))

# rebate ring around ALL FOUR sides of the bottom half (solid boolean)
ring = box_at(BLOCK_L + 2, BLOCK_W + 2, REBATE_DEPTH, -1, -1, 0).cut(
       box_at(BLOCK_L - 2*REBATE_IN, BLOCK_W - 2*REBATE_IN, REBATE_DEPTH + 2,
              REBATE_IN, REBATE_IN, -1))
lid = lid.cut(ring)

# ================= Box =================
open_l = BLOCK_L - 2*REBATE_IN + 2*FIT_CLEARANCE   # 201.4
open_w = BLOCK_W - 2*REBATE_IN + 2*FIT_CLEARANCE   #  99.8
cav_l  = BLOCK_L - 2*BOX_WALL                      # 197.2
cav_w  = BLOCK_W - 2*BOX_WALL                      #  95.6

box = box_at(BLOCK_L, BLOCK_W, BOX_H, 0, 0, 0)
# rim rebate (recess) around all four sides, takes the lid tongue
box = box.cut(box_at(open_l, open_w, REBATE_DEPTH + 1,
                     (BLOCK_L - open_l)/2.0, (BLOCK_W - open_w)/2.0,
                     BOX_H - REBATE_DEPTH))
# main cavity: from the floor up through the top (inside the rim opening)
box = box.cut(box_at(cav_l, cav_w, BOX_H,
                     BOX_WALL, BOX_WALL, BOX_FLOOR))

# banana socket holes: two 12 mm holes through one short side wall,
# axes along X, symmetric about the width centre, 20 mm apart
for y in (BLOCK_W/2.0 - SOCKET_SPACING/2.0, BLOCK_W/2.0 + SOCKET_SPACING/2.0):
    drill = (cq.Workplane("YZ")
             .center(y, SOCKET_Z)
             .circle(SOCKET_HOLE_D/2.0)
             .extrude(BOX_WALL + 4)
             .translate((SOCKET_END_X - 2 if SOCKET_END_X == 0.0
                         else SOCKET_END_X - BOX_WALL - 2, 0, 0)))
    box = box.cut(drill)

# three banana socket holes on the OPPOSITE short wall, centred on the wall
y_centre = BLOCK_W/2.0
y3 = [y_centre + (i - (SOCKET3_COUNT-1)/2.0)*SOCKET3_SPACING for i in range(SOCKET3_COUNT)]
for y in y3:
    drill = (cq.Workplane("YZ")
             .center(y, SOCKET_Z)
             .circle(SOCKET_HOLE_D/2.0)
             .extrude(BOX_WALL + 4)
             .translate((BLOCK_L - BOX_WALL - 2, 0, 0)))
    box = box.cut(drill)

# ---------------- Export ----------------
cq.exporters.export(lid, "/home/claude/AART_setup_block_lid_metric_v6.step")
cq.exporters.export(box, "/home/claude/AART_setup_block_box_metric_v6.step")

# ---------------- Verify ----------------
def slice_bb(part, z0, z1):
    s = part.val().intersect(box_at(1000, 1000, z1 - z0, -100, -100, z0).val())
    bb = s.BoundingBox()
    return bb.xlen, bb.ylen, s.Volume()

exp_removal = 4 * CROSS_SLOT_W * BRAID_W * (BLOCK_T - BRAID_DEPTH)
print(f"cross-slot removal expected: {exp_removal:.1f} mm^3 "
      f"(4 x {CROSS_SLOT_W} x {BRAID_W} x {BLOCK_T - BRAID_DEPTH:.3f})")
print(f"lid volume: {lid.val().Volume():.1f} mm^3")
xl, ylen, _ = slice_bb(lid, 0.5, 1.5)        # tongue region
print(f"lid tongue footprint: {xl:.3f} x {ylen:.3f} mm (expect 201.200 x 99.600)")
xl, ylen, _ = slice_bb(lid, BLOCK_T - 1, BLOCK_T)  # top half
print(f"lid top footprint:    {xl:.3f} x {ylen:.3f} mm (expect 203.200 x 101.600)")

_, _, v_top = slice_bb(box, BOX_H - 1, BOX_H)
exp_top = (BLOCK_L*BLOCK_W - open_l*open_w)
print(f"box rim ring section: {v_top:.1f} mm^3/mm (expect {exp_top:.1f}) -> lip {(BLOCK_L-open_l)/2:.2f} mm")
_, _, v_mid = slice_bb(box, 10, 11)
exp_mid = (BLOCK_L*BLOCK_W - cav_l*cav_w)
print(f"box wall section:     {v_mid:.1f} mm^3/mm (expect {exp_mid:.1f}) -> wall {BOX_WALL} mm")

# verify socket holes: slice the wall at hole height
s = box.val().intersect(box_at(BOX_WALL, 1000, SOCKET_HOLE_D, -0.5 if SOCKET_END_X==0 else BLOCK_L-BOX_WALL, -100, SOCKET_Z - SOCKET_HOLE_D/2).val())
solid_wall = BOX_WALL*BLOCK_W*SOCKET_HOLE_D if SOCKET_END_X==0 else None
import math
expected = (BOX_WALL+0.5)*BLOCK_W*SOCKET_HOLE_D - 2*math.pi*(SOCKET_HOLE_D/2)**2*(BOX_WALL+0.5)
print(f"wall slice volume with 2 holes: {s.Volume():.1f} mm^3 (expect {expected:.1f})")
print(f"socket hole centres: Y = {BLOCK_W/2-SOCKET_SPACING/2:.1f} and {BLOCK_W/2+SOCKET_SPACING/2:.1f} mm, Z = {SOCKET_Z} mm, D = {SOCKET_HOLE_D} mm")

s3 = box.val().intersect(box_at(BOX_WALL, 1000, SOCKET_HOLE_D, BLOCK_L-BOX_WALL, -100, SOCKET_Z-SOCKET_HOLE_D/2).val())
import math as _m
exp3 = BOX_WALL*BLOCK_W*SOCKET_HOLE_D - 3*_m.pi*(SOCKET_HOLE_D/2)**2*BOX_WALL
print(f"rear wall slice with 3 holes: {s3.Volume():.1f} mm^3 (expect {exp3:.1f})")
print(f"rear socket centres: Y = {', '.join(f'{v:.1f}' for v in y3)} mm, Z = {SOCKET_Z} mm")

bb = box.val().BoundingBox()
print(f"FIT_CLEARANCE = {FIT_CLEARANCE} mm/side; box opening {open_l:.1f} x {open_w:.1f}, "
      f"tongue {BLOCK_L-2*REBATE_IN:.1f} x {BLOCK_W-2*REBATE_IN:.1f}; "
      f"rim lip {(BLOCK_L-open_l)/2:.2f} mm")
print(f"box external: {bb.xlen:.3f} x {bb.ylen:.3f} x {bb.zlen:.3f} mm")
print(f"clear internal depth under lid: {BOX_H - REBATE_DEPTH - BOX_FLOOR:.4f} mm")
print(f"assembled overall height: {BOX_H + BLOCK_T - REBATE_DEPTH:.4f} mm")
