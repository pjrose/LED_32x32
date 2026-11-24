"""Build revision 2: corner-clear plate, four direct PCB posts, M2.5 nut traps.

Run with Python and packages manifold3d, trimesh, shapely, numpy, pillow.
Edit rev2-parameters.json and regenerate. Millimeters throughout.
No Blender modifiers affect the STL; generated watertight CSG is authoritative.
"""
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.cad-deps'))
import numpy as np
import trimesh
from shapely.geometry import box,Point,Polygon,LineString
from shapely.ops import unary_union
from csg import Solid,rounded,union,extrude,cyl
P=json.loads((ROOT/'rev2-parameters.json').read_text())
OUT=ROOT/'output'/'rev2';OUT.mkdir(parents=True,exist_ok=True)
S,T=P['panel_size'],P['plate_thickness'];C=S/2;EPS=.02
corner=[(C+i*P['corner_hole_dx'],C+j*P['corner_hole_dy']) for i in [-1,1] for j in [-1,1]]
mid=[(C,9.9),(C,S-9.9),(9.9,C),(S-9.9,C)]
bx=S-P['inner_frame_edge_from_outer']-P['board_right_inset_from_inner_frame']-63.5
by=P['board_bottom'];bw,bh=63.5,44.45
board_holes=[(bx+x,by+y) for x in [7.62,48.26] for y in [15.875,35.56]]
board_power=(bx+48.895,by+4.3815)
board_idc=(bx+57.15,by+22.225)
board_usb=(bx+5.08,by+8.255)
nx,ny=P['nut_body_center_x'],P['nut_body_center_y']
nut_left,nut_right=nx-P['nut_body_length']/2,nx+P['nut_body_length']/2
flipped=P.get('nut_rotation_deg',0)==180
nut_axis=nut_left+P['nut_ear_axis_from_two_port_end'] if flipped else nut_right-P['nut_ear_axis_from_two_port_end']
nut_holes=[(nut_axis,ny+i*P['nut_hole_spacing']/2) for i in [-1,1]]
outer=rounded(0,0,S,S,3)
for x,y in corner:outer=outer.difference(Point(x,y).buffer(P['corner_clear_radius'],quad_segs=32))

# Genuine connector/access reliefs; the rotated photo positions are approximate.
power=P['matrix_power_connector'];inp=P['matrix_hub75_input'];outp=P['matrix_hub75_output']
access=[rounded(power[0]-13,power[1]-10,26,20,3)]
access.extend(rounded(p[0]-9,p[1]-19,18,38,2) for p in [inp,outp])
access.extend(Point(x,y).buffer(6.0,quad_segs=24) for x,y in P['matrix_capacitors'])
# Underside female socket extends 5.55 mm below PCB: provide a dedicated window.
underside_socket=rounded(bx+52.25,by+5.215,9.8,34.02,1)
access.append(underside_socket)
vents=[]
for yy in [23,32,41,50]:
    vents.append(rounded(40,yy,67,4,1.9))
for yy in [109,119,129,139,149,159]:
    vents.append(rounded(42,yy,30,4,1.9))
for yy in [21,30,39,48]:
    vents.append(rounded(148,yy,16,4,1.9))
voids=unary_union(access+vents)
plan=outer.difference(voids)
base=extrude(plan,T)

def hexagon(x,y,af):
    # Flat sides parallel to X at +/-af/2; circumradius af/sqrt(3).
    r=af/math.sqrt(3)
    return Polygon([(x+r*math.cos(math.radians(a)),y+r*math.sin(math.radians(a))) for a in range(0,360,60)])

def nut_pocket(x,y,direction):
    af=P['m2_5_nut_across_flats'];hh=P['m2_5_nut_pocket_height'];z=P['m2_5_nut_pocket_bottom']
    hp=hexagon(x,y,af)
    # Open only towards the nearest accessible side. Nut can be inserted before
    # mounting the electronics; hex pocket prevents rotation under screw load.
    if direction<0:mouth=box(x-8,y-af/2,x,y+af/2)
    else:mouth=box(x,y-af/2,x+8,y+af/2)
    return extrude(hp.union(mouth),hh,z)

def post(x,y,top,dirn,bore,foot=10.0,tip=6.4):
    shape=cyl(x,y,0,top,foot,tip)
    shape-=cyl(x,y,P['screw_tip_floor'],top-P['screw_tip_floor']+EPS,bore)
    shape-=nut_pocket(x,y,dirn)
    return shape

plate=base
posts=[]
for x,y in board_holes:
    dirn=-1 if x<bx+bw/2 else 1
    po=post(x,y,P['board_seat_z'],dirn,P['board_bore']);posts.append(po)
    plate+=po
for x,y in nut_holes:
    po=post(x,y,P['nut_ear_seat_z'],1,P['nut_bore'],9.0,6.8);posts.append(po)
    plate+=po

# Cut bores/nut channels through the plate as well as the raised post solids.
for x,y in board_holes+nut_holes:
    dirn=(-1 if x<bx+bw/2 else 1) if (x,y) in board_holes else 1
    top=P['board_seat_z'] if (x,y) in board_holes else P['nut_ear_seat_z']
    plate-=nut_pocket(x,y,dirn)
    plate-=cyl(x,y,P['screw_tip_floor'],top-P['screw_tip_floor']+EPS,2.8)
for x,y in mid:
    plate-=cyl(x,y,-EPS,T+2*EPS,3.4)
    plate-=cyl(x,y,T-1.5,1.5+EPS,3.4,6.4)

# Supply strain relief, paired tie slots in a clear region below lever connector.
ties=[]
for xx in [63,76]:ties.append(rounded(xx,51,2.6,7,1.2))
# Ribbon retention near top, with slots aligned so a loose tie crosses its width.
for yy in [150,174]:ties.append(rounded(122,yy,8,2.6,1.2))
for g in ties:plate-=extrude(g,T+2*EPS,-EPS)

def dump(name,solid):
    mm=solid.mesh.to_mesh()
    mesh=trimesh.Trimesh(vertices=np.asarray(mm.vert_properties)[:,:3],faces=np.asarray(mm.tri_verts),process=True)
    components=len(solid.mesh.decompose())
    assert mesh.is_watertight and mesh.is_winding_consistent and components==1,(name,components)
    assert mesh.volume>0 and mesh.bounds[0,2]>=-1e-5
    mesh.export(OUT/(name+'.stl'))
    (OUT/(name+'.scad')).write_text('// Revision 2 / mm / generated from ../../rev2-parameters.json\n'+solid.source)
    return {'watertight':bool(mesh.is_watertight),'consistent_winding':bool(mesh.is_winding_consistent),'bodies':components,
            'triangles':len(mesh.faces),'size_mm':mesh.extents.tolist(),'volume_cm3':float(mesh.volume/1000)}

report={'rear-plate-v2':dump('rear-plate-v2',plate)}
# Crop a small representative nut-trap and bore sample before committing to plate.
samplebase=extrude(rounded(0,0,36,25,2),T)
sample=samplebase+post(10,12.5,8,-1,2.8)+post(26,12.5,8,1,2.8)
for x,d in [(10,-1),(26,1)]:
    sample-=nut_pocket(x,12.5,d)
    sample-=cyl(x,12.5,P['screw_tip_floor'],8-P['screw_tip_floor']+EPS,2.8)
report['m2-5-nut-trap-fit-test']=dump('m2-5-nut-trap-fit-test',sample)
# The cropped footprint check reproduces all six production mounting positions.
checkbase=extrude(rounded(64,54,95,95,3).difference(underside_socket),T)
check=checkbase+union(posts)
for x,y in board_holes+nut_holes:
    d=(-1 if x<bx+bw/2 else 1) if (x,y) in board_holes else 1
    check-=nut_pocket(x,y,d)
    check-=cyl(x,y,P['screw_tip_floor'],8-P['screw_tip_floor']+EPS,2.8)
check=check.move((-64,-54,0))
report['electronics-fit-check-v2']=dump('electronics-fit-check-v2',check)

matrix_route=[power,[127.4,46],[122,54],[111,65],[103,ny+3],[nut_right,ny+3]]
controller_route=[list(board_power),[board_power[0],99],[128,88],[119,72],[106,ny-9],[nut_right,ny-9]]
ribbon_route=[inp,[65,133.41],[76,163],[169,163],[169,board_idc[1]],list(board_idc)]
def length(path):return sum(math.dist(a,b) for a,b in zip(path,path[1:]))
report['layout']={
    'orientation':'Rear view matching marked drawing, X right, Y up; 191.8 mm panel.',
    'panel_mount_holes_mm':mid,'corner_keepouts_mm':corner,'corner_clear_radius_mm':P['corner_clear_radius'],
    'board_lower_left_mm':[bx,by],'board_right_edge_mm':bx+bw,
    'frame_inner_right_edge_assumed_mm':S-P['inner_frame_edge_from_outer'],
    'board_to_right_inner_frame_edge_mm':P['board_right_inset_from_inner_frame'],
    'board_hole_centers_mm':board_holes,'board_hole_pitch_mm':[40.64,19.685],
    'nut_hole_centers_mm':nut_holes,'nut_hole_spacing_mm':P['nut_hole_spacing'],
    'matrix_power_path_mm':round(length(matrix_route),1),'matrix_power_available_mm':P['matrix_power_lead_length'],
    'controller_power_path_mm':round(length(controller_route),1),'controller_power_available_mm':100.0,
    'ribbon_path_mm':round(length(ribbon_route),1),'ribbon_available_mm':P['ribbon_length'],
    'ribbon_reserve_mm':round(P['ribbon_length']-length(ribbon_route),1),
    'estimated_connector_top_z_mm':P['board_seat_z']+12.2135,
    'estimated_nut_top_z_mm':P['nut_ear_seat_z']+P['nut_body_height']-P['nut_ear_bottom_above_body_bottom'],
    'nut_trap_mm':{'across_flats':P['m2_5_nut_across_flats'],'height':P['m2_5_nut_pocket_height'],'bottom_z':P['m2_5_nut_pocket_bottom']},
    'status':'Fit-check prototype. Nut body footprint/ear height, frame inner edge, connected plug height and actual cable takeoffs need physical verification.'}
assert length(matrix_route)<P['matrix_power_lead_length']
assert length(controller_route)<100.0
assert length(ribbon_route)<P['ribbon_length']
for x,y in corner:assert plate.mesh.min_gap(cyl(x,y,-1,12,2*P['corner_clear_radius']-0.2).mesh,.2)>.05
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
(OUT/'parameters-used.json').write_text(json.dumps(P,indent=2))

# Raw triangle assets for Blender scene creation via its live MCP bridge.
def export_mesh(name,solid):
    mm=solid.mesh.to_mesh()
    mesh=trimesh.Trimesh(vertices=np.asarray(mm.vert_properties)[:,:3],faces=np.asarray(mm.tri_verts),process=True)
    mesh.export(OUT/(name+'.stl'))
nutbottom=P['nut_ear_seat_z']-P['nut_ear_bottom_above_body_bottom']
body_plan=rounded(nut_left,ny-12,26,24,1).union(rounded(nut_left+25,ny-7,17,14,1))
if flipped:
    from shapely.affinity import rotate
    body_plan=rotate(body_plan,180,origin=(nx,ny))
body=extrude(body_plan,P['nut_body_height'],nutbottom)
for x,y in nut_holes:
    ear=cyl(x,y,nutbottom,2.2,7)-cyl(x,y,nutbottom-EPS,2.2+2*EPS,3)
    body+=ear
export_mesh('reference-lever-nut-body-NOT-FOR-PRINT',body)
levers_orange=[];levers_blue=[]
for xx,ys in [(nut_left+3,[ny-9,ny-3,ny+3,ny+9]),(nut_left+29,[ny-4,ny+4])]:
    for i,yy in enumerate(ys):
        lever=extrude(rounded(xx,yy-1.7,10,3.4,.6),1.4,nutbottom+P['nut_body_height']-.2)
        if flipped:lever=lever.move((-nx,-ny,0)).rotate(180).move((nx,ny,0))
        (levers_orange if i%2 else levers_blue).append(lever)
export_mesh('reference-levers-orange-NOT-FOR-PRINT',union(levers_orange))
export_mesh('reference-levers-blue-NOT-FOR-PRINT',union(levers_blue))
# Save layout information for diagram, assembly scene, and documented estimates.
scene={'parameters':P,'report':report,'routes':{'matrix':matrix_route,'controller':controller_route,'ribbon':ribbon_route},
       'board_origin':[bx,by,P['board_seat_z']],'corner_centers':corner,'midpoint_centers':mid,'board_holes':board_holes,'nut_holes':nut_holes,
       'plan_outline':list(outer.exterior.coords),'voids':[list(g.exterior.coords) for g in access+vents+ties]}
(OUT/'scene-data.json').write_text(json.dumps(scene,indent=2))
print(json.dumps(report,indent=2))
