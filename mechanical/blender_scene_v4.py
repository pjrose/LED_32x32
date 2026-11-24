"""Create a separate V4 open-frame review scene in the running Blender."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'D:/LED_32x32/mechanical');OUT=ROOT/'output/rev4'
D=json.loads((OUT/'scene-data.json').read_text());P=D['parameters'];S=P['panel_size'];C=S/2
scene=bpy.data.scenes.new('LED Matrix - Open Frame V4')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
scene.unit_settings.length_unit='MILLIMETERS'
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1500;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world=bpy.data.worlds.new('V4 Review World');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.21,.26,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
scene.view_settings.view_transform='AgX'
def material(name,color,metal=0,rough=.45):
    m=bpy.data.materials.new('V4 '+name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    m.diffuse_color=(*color,1);return m
frame_mat=material('Printed PETG - sage',(.19,.39,.32),0,.5)
black=material('Matrix plastic',(.022,.028,.034),0,.62)
pcbmat=material('Reference PCB',(.025,.075,.057),0,.5)
metal=material('Steel',(.56,.59,.61),.7,.32)
connector=material('Connectors',(.035,.04,.05),0,.55)
bodymat=material('Lever body',(.66,.71,.73),0,.38)
orange=material('Orange',(.98,.29,.035));blue=material('Blue',(.025,.40,.70))
gold=material('Brass',(.57,.40,.13),.65,.3)
red=material('Power red',(.55,.025,.02));wireblack=material('Power return',(.015,.018,.023))
ribbonmat=material('Ribbon',(.16,.19,.24))
def collection(name):
    co=bpy.data.collections.new('V4 '+name);scene.collection.children.link(co);return co
printed=collection('PRINT - frame only')
hardware=collection('REFERENCE - panel electronics fasteners - do not print')
routes=collection('REFERENCE - schematic cable paths')
def move(obj,co):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    co.objects.link(obj)
def imported(path,name,mat,co):
    bpy.ops.wm.stl_import(filepath=str(path),global_scale=1,use_scene_unit=False,forward_axis='Y',up_axis='Z')
    o=bpy.context.object;o.name='V4 '+name;o.data.materials.clear();o.data.materials.append(mat);move(o,co);return o
frame=imported(OUT/'rear-frame-v4.stl','PRINT Open frame - 4 mm base',frame_mat,printed)
frame['printable']=True;frame['base_thickness_mm']=4;frame['raised_post_height_mm']=0
frame['hardware']='Four M3 panel screws; six M2.5 heat-set inserts; corners open'
board=imported(ROOT/'reference/matrixportal-s3-official.stl','REFERENCE MatrixPortal S3',pcbmat,hardware)
board.location=D['board_origin'];board.rotation_euler.z=math.radians(D['board_rotation_deg'])
board['source']='https://github.com/adafruit/Adafruit_CAD_Parts/tree/main/5778%20Matrix%20Portal%20S3'
board['left_inset_mm']=23
board.data.materials.append(metal);board.data.materials.append(connector)
for f in board.data.polygons:
    p=f.center
    if p.z>5 or p.x>51:f.material_index=2
    elif p.z>2.2 and 19<p.x<42 and 15<p.y<39:f.material_index=1
for fn,name,mat in [('reference-lever-body-NOT-FOR-PRINT.stl','REFERENCE approximate lever connector',bodymat),
    ('reference-levers-orange-NOT-FOR-PRINT.stl','REFERENCE orange levers',orange),
    ('reference-levers-blue-NOT-FOR-PRINT.stl','REFERENCE blue levers',blue)]:
    imported(OUT/fn,name,mat,hardware)
def cube(name,loc,size,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='V4 REFERENCE '+name
    o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat);move(o,hardware);return o
def cylinder(name,loc,r,depth,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc)
    o=bpy.context.object;o.name='V4 REFERENCE '+name;o.data.materials.append(mat);move(o,hardware);return o
cube('Matrix PCB',(C,C,-7.5),(S-2,S-2,1.6),pcbmat)
for name,loc,size in [('top rim',(C,S-6.3,-3.6),(S,12.6,7.2)),
    ('bottom rim',(C,6.3,-3.6),(S,12.6,7.2)),('left rim',(6.3,C,-3.6),(12.6,S,7.2)),
    ('right rim',(S-6.3,C,-3.6),(12.6,S,7.2)),('center rib',(C,C,-3.6),(8.8,S-20,7.2))]:
    cube('Matrix '+name,loc,size,black)
for i,(x,y) in enumerate(D['corner_centers']):
    cylinder('Exposed factory corner insert '+str(i+1),(x,y,.15),2.8,.5,gold)
    cylinder('Corner thread '+str(i+1),(x,y,.43),1.5,.1,black)
for i,(x,y) in enumerate(D['midpoint_centers']):
    cylinder('M3 frame screw '+str(i+1),(x,y,3.6),2.85,.6,metal)
for i,(x,y) in enumerate(D['board_holes']):
    cylinder('M2.5 PCB screw '+str(i+1),(x,y,6.5),2.25,1.8,metal)
for i,(x,y) in enumerate(D['nut_holes']):
    cylinder('M2.5 lever washer '+str(i+1),(x,y,6.4),3,.4,metal)
    cylinder('M2.5 lever screw '+str(i+1),(x,y,7.3),2.25,1.5,metal)
def cable(name,points,mat,radius):
    cu=bpy.data.curves.new('V4 '+name,'CURVE');cu.dimensions='3D';cu.resolution_u=16
    cu.bevel_depth=radius;cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for pt,xyz in zip(sp.bezier_points,points):
        pt.co=xyz;pt.handle_left_type='AUTO';pt.handle_right_type='AUTO'
    o=bpy.data.objects.new('V4 REFERENCE '+name,cu);routes.objects.link(o);cu.materials.append(mat)
for name,key,z in [('Matrix power','matrix',13),('Controller power','controller',14)]:
    for offset,mat,suffix in [(0,red,'positive'),(2,wireblack,'return')]:
        cable(name+' '+suffix,[(x,y+offset,z) for x,y in D['routes'][key]],mat,.8)
for i in range(16):
    shift=(i-7.5)*1.27
    cable('Ribbon '+str(i+1),[(x,y+shift,16) for x,y in D['routes']['ribbon']],ribbonmat,.52)
routes.hide_render=True;routes.hide_viewport=True
def camera(name,loc,target,ortho):
    data=bpy.data.cameras.new('V4 '+name);o=bpy.data.objects.new('V4 '+name,data);scene.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=ortho;data.clip_end=2000;return o
cam=camera('Camera Assembly',(260,-210,350),(C,C,0),270)
camera('Camera Rear Plan',(C,C,420),(C,C,0),217);scene.camera=cam
for name,loc,power,size in [('Key',(100,-50,300),1600000,220),('Fill',(-90,180,160),900000,170),('Rim',(280,230,250),1500000,160)]:
    ld=bpy.data.lights.new('V4 '+name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size
    o=bpy.data.objects.new('V4 '+name,ld);scene.collection.objects.link(o);o.location=loc
    o.rotation_euler=(Vector((C,C,0))-o.location).to_track_quat('-Z','Y').to_euler()
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        v=area.spaces.active;v.region_3d.view_location=(C,C,3);v.region_3d.view_distance=260
        v.region_3d.view_rotation=cam.rotation_euler.to_quaternion();v.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT');frame.select_set(True);bpy.context.view_layer.objects.active=frame
scene.render.filepath=str(OUT/'assembly-v4.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'matrix-rear-frame-v4.blend'),check_existing=False,copy=True)
result={'scene':scene.name,'frame_mm':list(frame.dimensions),'objects':len(scene.objects),'saved':str(OUT/'matrix-rear-frame-v4.blend')}
