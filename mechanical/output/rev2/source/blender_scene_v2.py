"""Run in Blender via its MCP bridge. Create a separate review scene, preserve others."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
ROOT=Path(r'D:/LED_32x32/mechanical')
OUT=ROOT/'output'/'rev2'
D=json.loads((OUT/'scene-data.json').read_text())
P=D['parameters'];S=P['panel_size'];C=S/2
scene=bpy.data.scenes.new('LED Matrix - Corner Clear V2')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=.001
scene.unit_settings.length_unit='MILLIMETERS'
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1600;scene.render.resolution_y=1400
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('LED Mount Review World')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.21,.26,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
scene.view_settings.view_transform='AgX'

def material(name,color,metal=0,rough=.45):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    m.diffuse_color=(*color,1);return m
plate_mat=material('Printed PETG - sage green',(.19,.39,.32),0,.5)
black=material('Matrix plastic',(.022,.028,.034),0,.62)
pcbmat=material('Reference PCB',(.025,.075,.057),0,.5)
metal=material('Reference aluminum',(.56,.59,.61),.7,.32)
connector=material('Reference connectors',(.035,.04,.05),0,.55)
bodymat=material('Lever nut reference body',(.66,.71,.73),0,.38)
orange=material('Lever orange',(.98,.29,.035),0,.4)
blue=material('Lever blue',(.025,.40,.70),0,.4)
gold=material('Fasteners - brass / steel',(.57,.40,.13),.65,.3)
ribbonmat=material('HUB75 ribbon routing reference',(.16,.19,.24),0,.6)
red=material('Power red',(.55,.025,.02),0,.4)
wireblack=material('Power return',(.015,.018,.023),0,.6)

def move_collection(obj,collection):
    for coll in list(obj.users_collection):coll.objects.unlink(obj)
    collection.objects.link(obj)
def collection(name):
    co=bpy.data.collections.new(name);scene.collection.children.link(co);return co
printed=collection('PRINT - rear plate only')
hardware=collection('REFERENCE - electronics and panel - do not print')
routes=collection('REFERENCE - cable paths - verify actual bends')
labels=collection('REFERENCE - dimensions')

def imported(path,name,mat,coll):
    bpy.ops.wm.stl_import(filepath=str(path),global_scale=1,use_scene_unit=False,forward_axis='Y',up_axis='Z')
    o=bpy.context.active_object;o.name=name
    o.data.materials.clear();o.data.materials.append(mat)
    move_collection(o,coll);return o

plate=imported(OUT/'rear-plate-v2.stl','PRINT Rear Plate V2 - 191.8 mm',plate_mat,printed)
plate['printable']=True;plate['dimensions_mm']='191.8 x 191.8 x 8';plate['mounting']='4 midpoint M3; 4 corners entirely clear'
plate['fasteners']='4 M2.5 direct PCB screws; 2 M2.5 lever screws; six captive M2.5 nuts'

board=imported(ROOT/'reference'/'matrixportal-s3-official.stl','REFERENCE Adafruit MatrixPortal S3',pcbmat,hardware)
board.location=D['board_origin']
board['source']='https://github.com/adafruit/Adafruit_CAD_Parts/tree/main/5778%20Matrix%20Portal%20S3'
board['right_inset_mm']=23
board.data.materials.append(metal);board.data.materials.append(connector)
for f in board.data.polygons:
    p=f.center
    if p.z>5 or p.x>51:f.material_index=2
    elif p.z>2.2 and 19<p.x<42 and 15<p.y<39:f.material_index=1

for filename,name,mat in [('reference-lever-nut-body-NOT-FOR-PRINT.stl','REFERENCE Lever nut body - approximate',bodymat),
                          ('reference-levers-orange-NOT-FOR-PRINT.stl','REFERENCE Orange levers',orange),
                          ('reference-levers-blue-NOT-FOR-PRINT.stl','REFERENCE Blue levers',blue)]:
    imported(OUT/filename,name,mat,hardware)

def cube(name,loc,size,mat,coll):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat);move_collection(o,coll);return o
def cylinder(name,loc,r,depth,mat,coll,verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc)
    o=bpy.context.object;o.name=name;o.data.materials.append(mat);move_collection(o,coll);return o
cube('REFERENCE Matrix PCB',(C,C,-7.5),(S-2,S-2,1.6),pcbmat,hardware)
for name,loc,size in [
    ('top rim',(C,S-6.3,-3.6),(S,12.6,7.2)),('bottom rim',(C,6.3,-3.6),(S,12.6,7.2)),
    ('left rim',(6.3,C,-3.6),(12.6,S,7.2)),('right rim',(S-6.3,C,-3.6),(12.6,S,7.2)),
    ('middle rib',(C,C,-3.6),(S-20,8.8,7.2))]:
    cube('REFERENCE Matrix '+name,loc,size,black,hardware)
for i,(x,y) in enumerate(D['corner_centers']):
    # Existing panel brass threads only. No printed enclosures or magnetic studs.
    cylinder('REFERENCE Existing exposed corner insert '+str(i+1),(x,y,.15),2.8,.5,gold,hardware)
    cylinder('REFERENCE Corner thread opening '+str(i+1),(x,y,.43),1.5,.1,black,hardware)
for i,(x,y) in enumerate(D['midpoint_centers']):
    cylinder('REFERENCE M3 plate screw '+str(i+1),(x,y,P['plate_thickness']-.5),2.85,.6,metal,hardware)
for i,(x,y) in enumerate(D['board_holes']):
    cylinder('REFERENCE M2.5 PCB screw '+str(i+1),(x,y,P['board_seat_z']+P['pcb_thickness']+.9),2.25,1.8,metal,hardware)
for i,(x,y) in enumerate(D['nut_holes']):
    cylinder('REFERENCE M2.5 lever washer '+str(i+1),(x,y,P['nut_ear_seat_z']+2.4),3,.4,metal,hardware)
    cylinder('REFERENCE M2.5 lever screw '+str(i+1),(x,y,P['nut_ear_seat_z']+3.3),2.25,1.5,metal,hardware)

def cable(name,points,mat,radius):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D'
    cu.resolution_u=16;cu.bevel_depth=radius;cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for pt,xyz in zip(sp.bezier_points,points):
        pt.co=xyz;pt.handle_left_type='AUTO';pt.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu);routes.objects.link(o);cu.materials.append(mat);return o
for name,key,z in [('Matrix power','matrix',13.0),('Controller power','controller',15.0)]:
    path=D['routes'][key]
    cable('REFERENCE '+name+' positive',[(x,y,z) for x,y in path],red,.8)
    cable('REFERENCE '+name+' return',[(x,y+2,z) for x,y in path],wireblack,.8)
# Ribbon centerline, drawn as 16 adjacent fine conductors. It is an illustrative
# routing guide, not a manufacturing cable surface or a bend-radius simulation.
rp=D['routes']['ribbon']
for i in range(16):
    shift=(i-7.5)*1.27
    cable('REFERENCE Ribbon conductor '+str(i+1),[(x,y+shift,16) for x,y in rp],ribbonmat,.52)
routes.hide_render=True  # Clean assembly render; toggle on to inspect cable routing.

def text(name,body,loc,size=4):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=0
    ob=bpy.data.objects.new(name,cu);labels.objects.link(ob);ob.location=loc;cu.materials.append(black);return ob
text('Title','REAR PLATE V2',(10,S+9,1),6)
text('Inset label','23 mm',(158,149,1),3.5)
labels.hide_render=True

def camera(name,loc,target,ortho):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);scene.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=ortho;data.clip_end=2000;return o
cam=camera('Camera - Assembly',(260,-210,350),(C,C,0),270)
top=camera('Camera - Rear Plan',(C,C,420),(C,C,0),217)
scene.camera=cam
for name,loc,power,size in [('Key',(100,-50,300),1600000,220),('Fill',(-90,180,160),900000,170),('Rim',(280,230,250),1500000,160)]:
    ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size
    ob=bpy.data.objects.new(name,ld);scene.collection.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector((C,C,0))-ob.location).to_track_quat('-Z','Y').to_euler()

for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_location=(C,C,3)
        area.spaces.active.region_3d.view_distance=260
        area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
        area.spaces.active.shading.type='MATERIAL'

bpy.ops.object.select_all(action='DESELECT')
plate.select_set(True);bpy.context.view_layer.objects.active=plate
scene.render.filepath=str(OUT/'assembly-v2.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'matrix-rear-mount-v2.blend'),check_existing=False,copy=True)
result={'scene':scene.name,'plate_mm':[round(v,3) for v in plate.dimensions],
        'board_origin':list(board.location),'objects':len(scene.objects),
        'saved':str(OUT/'matrix-rear-mount-v2.blend'),'printable_meshes':1}
