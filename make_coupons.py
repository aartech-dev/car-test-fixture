"""
Corner test coupons for the AART box/lid joint.
Prints a small L-corner of the LID (with tongue) and the matching corner of the
BOX (with rim rebate), so you can check the drop-on fit before the full print.

One LID corner is produced (its tongue is fixed), plus one BOX corner per
clearance value in CLEARANCES. Mix and match: print the lid corner once, print
the box corners, and see which clearance drops on with a light friction hold.
All mm.
"""
import cadquery as cq

def box_at(l, w, h, x, y, z):
    return cq.Workplane("XY").box(l, w, h, centered=False).translate((x, y, z))

# ---- joint geometry (must match the full model) ----
BLOCK_T      = 9.525
REBATE_IN    = 1.0
REBATE_DEPTH = BLOCK_T / 2.0      # 4.7625
BOX_H_LOCAL  = 12.0              # short stub wall, enough to grip; not full 30 mm
BOX_WALL     = 3.0
BOX_FLOOR    = 2.5

CO = 35.0                        # coupon arm length along each edge
CLEARANCES = [0.15, 0.20, 0.25]  # per-side, box opening relative to tongue

# Corner taken at the (x=0, y=0) outside corner. Outer faces lie on X=0 and Y=0.

def lid_corner():
    # full-thickness top, tongue stepped REBATE_IN in from the two outer edges
    top = box_at(CO, CO, BLOCK_T - REBATE_DEPTH, 0, 0, REBATE_DEPTH)
    tongue = box_at(CO - REBATE_IN, CO - REBATE_IN, REBATE_DEPTH,
                    REBATE_IN, REBATE_IN, 0)
    part = top.union(tongue)
    # engrave nothing; keep simple. Outer corner at origin.
    return part

def box_corner(clear):
    open_off = REBATE_IN - clear          # inner edge of the rim lip from outer face
    # solid corner block
    part = box_at(CO, CO, BOX_H_LOCAL, 0, 0, 0)
    # rim rebate recess (top REBATE_DEPTH), inset by open_off from the two outer faces
    part = part.cut(box_at(CO - open_off, CO - open_off, REBATE_DEPTH + 1,
                           open_off, open_off, BOX_H_LOCAL - REBATE_DEPTH))
    # inner cavity below the ledge, walls BOX_WALL thick from the two outer faces
    part = part.cut(box_at(CO - BOX_WALL, CO - BOX_WALL, BOX_H_LOCAL,
                           BOX_WALL, BOX_WALL, BOX_FLOOR))
    return part

lid = lid_corner()
cq.exporters.export(lid, "/home/claude/AART_coupon_LID_corner.step")
print(f"lid coupon: tongue inset {REBATE_IN} mm/side, outer {CO} x {CO} mm")

for c in CLEARANCES:
    b = box_corner(c)
    tag = f"{int(round(c*100)):02d}"   # 015 -> '15'
    fn = f"/home/claude/AART_coupon_BOX_corner_clr{tag}.step"
    cq.exporters.export(b, fn)
    # verify lip width at the rim
    lip = REBATE_IN - c
    print(f"box coupon clr {c:.2f} mm/side -> rim lip {lip:.2f} mm, file {fn.split('/')[-1]}")
