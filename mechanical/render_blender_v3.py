import bpy
from pathlib import Path
OUT=Path(r'D:/LED_32x32/mechanical/output/rev3')
s=bpy.data.scenes['LED Matrix - Open Frame V3']
if bpy.context.window:bpy.context.window.scene=s
for camera,name in [('V3 Camera Assembly','assembly-v3.png'),('V3 Camera Rear Plan','rear-plan-v3.png')]:
    s.camera=bpy.data.objects[camera];s.render.filepath=str(OUT/name)
    bpy.ops.render.render(write_still=True,scene=s.name)
bpy.data.collections['V3 REFERENCE - panel electronics fasteners - do not print'].hide_render=True
s.camera=bpy.data.objects['V3 Camera Assembly'];s.render.filepath=str(OUT/'printed-frame-v3.png')
bpy.ops.render.render(write_still=True,scene=s.name)
