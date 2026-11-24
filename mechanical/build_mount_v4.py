"""Generate the user's open 4 mm cross-frame, STLs, OpenSCAD and layout data."""
from pathlib import Path
import json,sys,math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.cad-deps'))
import numpy as np
import trimesh
from shapely.geometry import box,Point,LineString
from shapely.ops import unary_union
from shapely.affinity import rotate
from csg import rounded,extrude,cyl,union
P=json.loads((ROOT/'rev4-parameters.json').read_text())
OUT=ROOT/'output/rev4';OUT.mkdir(parents=True,exist_ok=True)
S=P['panel_size'];C=S/2;T=P['frame_thickness'];EPS=.02
corners=[(C+i*P['corner_hole_dx'],C+j*P['corner_hole_dy']) for i in [-1,1] for j in [-1,1]]
mid=[(C,C-83),(C,C+83),(C-86,C),(C+86,C)]
outer=rounded(0,0,S,S,3)
for x,y in corners:outer=outer.difference(Point(x,y).buffer(P['corner_clear_radius'],quad_segs=32))
# Small corner cutouts leave detached tips outside their arcs. Discard those
# tips so the corners stay open and the printed frame remains one piece.
if outer.geom_type=='MultiPolygon':outer=max(outer.geoms,key=lambda g:g.area)
# Offset the actual scalloped perimeter, so the border stays continuous around
# all four corner clearances instead of becoming four disconnected edge bars.
border=outer.difference(outer.buffer(-P['border_width'],join_style=1))
w=P['main_cross_width']
bx=P['inner_frame_edge_from_outer']+P['board_inset_from_left_inner_frame']
by=C-7.62
bw,bh=44.45,63.5
def bxy(x,y):return (bx+44.45-y,by+x)
bhole=[bxy(x,y) for x in [7.62,48.26] for y in [15.875,35.56]]
branch_y=C+40.64
main_h=box(0,C-w/2,S,C+w/2)
main_v=box(C-w/2,0,C+w/2,S)
branch=box(0,branch_y-P['pcb_branch_width']/2,C+w/2,branch_y+P['pcb_branch_width']/2)
plan=unary_union([border,main_h,main_v,branch]).intersection(outer)
# Only blend beam junctions; clipping preserves the 25 mm corner keep-outs.
plan=plan.buffer(1.8,quad_segs=8).buffer(-1.8,quad_segs=8).intersection(outer)
nx,ny=P['nut_center_x'],C+P['nut_ear_offset_from_body_center']
nhole=[(nx+i*P['nut_hole_spacing']/2,C) for i in [-1,1]]
top=P['board_seat_z']
assert top==T==P['nut_seat_z']==4.0
base=extrude(plan,T)
frame=base

def pocket(x,y,pilot=None):
    pilot=P['insert_pilot_diameter'] if pilot is None else pilot
    c=P['insert_entrance_chamfer']
    return cyl(x,y,-EPS,T+2*EPS,pilot)+cyl(x,y,top-c,c+EPS,pilot,pilot+2*c)
for x,y in bhole+nhole:frame-=pocket(x,y)
for x,y in mid:
    frame-=cyl(x,y,-EPS,T+2*EPS,3.4)
    frame-=cyl(x,y,T-1.5,1.5+EPS,3.4,6.4)

# A pair of tie slots on the bottom border for the long supply cable. These do
# not add tabs, solid panels, or restrictions to the main matrix cable opening.
ties=[rounded(x,7.5,2.4,6,1.1) for x in [119,133]]
for shape in ties:frame-=extrude(shape,T+2*EPS,-EPS)

def dump(name,solid):
    # Collapse sub-micron CSG slivers before binary STL's float32 conversion.
    # Check the exported file itself, since that is what the slicer will read.
    raw=solid.mesh.simplify(.0001).to_mesh64()
    m=trimesh.Trimesh(np.asarray(raw.vert_properties)[:,:3],np.asarray(raw.tri_verts),process=True)
    assert m.is_watertight and m.is_winding_consistent and m.volume>0
    assert len(solid.mesh.decompose())==1
    m.export(OUT/(name+'.stl'))
    exported=trimesh.load(OUT/(name+'.stl'))
    exported.update_faces(exported.nondegenerate_faces(height=1e-8))
    exported.update_faces(exported.unique_faces())
    exported.remove_unreferenced_vertices()
    exported.export(OUT/(name+'.stl'))
    exported=trimesh.load(OUT/(name+'.stl'))
    assert exported.is_watertight and exported.is_winding_consistent and exported.is_volume
    (OUT/(name+'.scad')).write_text('// mm / generated from rev4-parameters.json\n'+solid.source)
    return {'watertight':bool(m.is_watertight),'consistent_winding':bool(m.is_winding_consistent),
            'exported_stl_watertight':bool(exported.is_watertight),
            'connected_bodies':1,'size_mm':exported.extents.tolist(),'volume_cm3':float(exported.volume/1000),'triangles':len(exported.faces)}

report={'rear-frame-v4':dump('rear-frame-v4',frame)}
# Same through bore and frame thickness as the final part.
sample=extrude(rounded(0,0,44,18,2),top)
font={'0':['111','101','101','101','111'],'1':['010','110','010','010','111'],
      '2':['111','001','111','100','111'],'3':['111','001','111','001','111'],
      '4':['101','101','111','001','001'],'8':['111','101','111','101','111'],'.':['0','0','0','0','1']}
for i,pilot in enumerate([3.8,4.0,4.2]):
    x=8+14*i;sample-=pocket(x,11,pilot)
    xx=x-3.2;bits=[]
    for ch in f'{pilot:.1f}':
        for yy,row in enumerate(font[ch]):
            for j,b in enumerate(row):
                if b=='1':bits.append(box(xx+j*.55,1+(4-yy)*.55,xx+(j+1)*.55,1+(5-yy)*.55))
        xx+=(2 if ch=='.' else 4)*.55
    sample+=extrude(unary_union(bits),.4,top-EPS)
report['m2-5-heat-set-sizing-coupon']=dump('m2-5-heat-set-sizing-coupon',sample)

# An entirely open electronics fit check: two horizontal rails, one vertical
# connector, all six actual insert centers. No plate underneath either device.
checkplan=unary_union([box(34,C-5,142,C+5),box(C-5,85,C+5,142),
                       box(34,branch_y-4,C+5,branch_y+4)])
check=extrude(checkplan,T)
for x,y in bhole+nhole:check-=pocket(x,y)
report['electronics-fit-check-v4']=dump('electronics-fit-check-v4',check.move((-34,-85,0)))

power=P['matrix_power_connector'];inp=P['matrix_hub75_input']
bp=bxy(48.895,4.3815);bi=bxy(57.15,22.225);bu=bxy(5.08,8.255)
nut_four_y=ny+P['nut_body_length']/2
matrix_route=[power,[143,129],[133,130],[121,127],[nx+3,nut_four_y]]
controller_route=[list(bp),[86,139],[100,135],[106,128],[nx-3,nut_four_y]]
ribbon_route=[inp,[58.39,60],[24,70],[24,165],[bi[0],165],list(bi)]
def length(r):return sum(math.dist(a,b) for a,b in zip(r,r[1:]))
assert length(matrix_route)<P['matrix_power_lead_length']
assert length(controller_route)<P['controller_power_lead_length']
assert length(ribbon_route)<P['ribbon_length']
# The entire underside female header is clear of the 4 mm frame. Its lower
# face now reaches Z=-1.55, into the open rear-panel cavity.
socket=box(bx+44.45-(22.225+16.51),by+57.15-4.4,
           bx+44.45-(22.225-16.51),by+57.15+4.4)
socket_solid=extrude(socket,5.55,top-5.55)
assert (frame.mesh ^ socket_solid.mesh).volume()<1e-6,'Underside header clearance failed'
for x,y in corners:
    assert (frame.mesh ^ cyl(x,y,-1,12,2*P['corner_clear_radius']-.02).mesh).volume()<1e-6
assert all(abs(y-C)<1e-7 for x,y in nhole+bhole[:2])
assert abs(top-P['insert_pocket_depth'])<1e-7
assert abs(nx-12-(C+w/2))<1e-7
for x,y in bhole+nhole:
    assert (frame.mesh ^ cyl(x,y,-EPS,T+2*EPS,P['insert_pilot_diameter']-.02).mesh).volume()<1e-6
report['layout']={
    'frame_thickness_mm':T,'border_width_mm':P['border_width'],
    'main_cross_width_mm':w,'secondary_branch_width_mm':P['pcb_branch_width'],
    'cross_center_mm':[C,C],'secondary_branch_y_mm':branch_y,
    'panel_mount_centers':mid,'corner_centers':corners,'corner_clear_radius_mm':P['corner_clear_radius'],
    'board_origin':[bx+44.45,by,top],'board_rotation_deg':90,
    'board_footprint_lower_left':[bx,by],'board_hole_centers':bhole,
    'lever_hole_centers':nhole,'lever_body_center':[nx,ny],
    'insert_pilot_mm':P['insert_pilot_diameter'],'insert_depth_mm':P['insert_pocket_depth'],
    'pocket_floor_mm':0.0,'insert_bores_through':True,
    'insert_lead_in_depth_mm':P['insert_entrance_chamfer'],
    'insert_lead_in_top_diameter_mm':P['insert_pilot_diameter']+2*P['insert_entrance_chamfer'],
    'nut_left_body_edge_x_mm':nx-12,'vertical_cross_right_edge_x_mm':C+w/2,
    'board_under_socket_collision_volume_mm3':float((frame.mesh ^ socket_solid.mesh).volume()),
    'open_area_percent':round((1-plan.area/outer.area)*100,1),
    'matrix_route_mm':round(length(matrix_route),1),'matrix_available_mm':50.8,
    'controller_route_mm':round(length(controller_route),1),'controller_available_mm':100,
    'ribbon_route_mm':round(length(ribbon_route),1),'ribbon_available_mm':254,
    'status':'Geometry validated; no physical print/insert/harness fit test performed.'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
(OUT/'parameters-used.json').write_text(json.dumps(P,indent=2))

# Schematic lever body, rotated so the four-port end is above the centerline.
nut_plan=rounded(-21,-12,26,24,1).union(rounded(4,-7,17,14,1))
nut_plan=rotate(nut_plan,-90,origin=(0,0))
from shapely.affinity import translate
nut_plan=translate(nut_plan,nx,ny)
body=extrude(nut_plan,P['nut_body_height'],P['nut_seat_z'])
for x,y in nhole:
    body+=cyl(x,y,top,2.2,7)-cyl(x,y,top-EPS,2.2+2*EPS,3)
def mesh_only(name,solid):
    raw=solid.mesh.simplify(.0001).to_mesh64()
    trimesh.Trimesh(np.asarray(raw.vert_properties)[:,:3],np.asarray(raw.tri_verts),process=True).export(OUT/(name+'.stl'))
mesh_only('reference-lever-body-NOT-FOR-PRINT',body)
orange=[];blue=[]
for xx,ys in [(-18,[-9,-3,3,9]),(8,[-4,4])]:
    for i,yy in enumerate(ys):
        lever=extrude(rounded(xx,yy-1.7,10,3.4,.6),1.4,top+P['nut_body_height']-.2)
        lever=lever.rotate(-90).move((nx,ny,0))
        (orange if i%2 else blue).append(lever)
mesh_only('reference-levers-orange-NOT-FOR-PRINT',union(orange))
mesh_only('reference-levers-blue-NOT-FOR-PRINT',union(blue))
scene={'parameters':P,'report':report,'board_origin':[bx+44.45,by,top],'board_rotation_deg':90,
       'board_footprint':[bx,by,bw,bh],'board_holes':bhole,'nut_holes':nhole,'nut_center':[nx,ny],
       'corner_centers':corners,'midpoint_centers':mid,'routes':{'matrix':matrix_route,'controller':controller_route,'ribbon':ribbon_route},
       'outline':list(outer.exterior.coords),'border_inner':[list(g.exterior.coords) for g in [outer.buffer(-P['border_width'])]],
       'plan_polygons':[{'exterior':list(plan.exterior.coords),'holes':[list(r.coords) for r in plan.interiors]}],
       'nut_outline':list(nut_plan.exterior.coords),'socket_keepout':list(socket.exterior.coords)}
(OUT/'scene-data.json').write_text(json.dumps(scene,indent=2))
print(json.dumps(report,indent=2))
