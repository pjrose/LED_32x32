import bpy
from pathlib import Path
OUT=Path(r'D:/LED_32x32/mechanical/output/rev4')
s=bpy.data.scenes['LED Matrix - Open Frame V4']
if bpy.context.window:bpy.context.window.scene=s
for camera,name in [('V4 Camera Assembly','assembly-v4.png'),('V4 Camera Rear Plan','rear-plan-v4.png')]:
    s.camera=bpy.data.objects[camera];s.render.filepath=str(OUT/name)
    bpy.ops.render.render(write_still=True,scene=s.name)
bpy.data.collections['V4 REFERENCE - panel electronics fasteners - do not print'].hide_render=True
s.camera=bpy.data.objects['V4 Camera Assembly'];s.render.filepath=str(OUT/'printed-frame-v4.png')
bpy.ops.render.render(write_still=True,scene=s.name)
