import bpy
from pathlib import Path
OUT=Path(r'D:/LED_32x32/mechanical/output/rev2')
s=bpy.data.scenes['LED Matrix - Corner Clear V2']
if bpy.context.window:bpy.context.window.scene=s
s.render.resolution_x=1500;s.render.resolution_y=1400;s.render.resolution_percentage=100
s.camera=bpy.data.objects['Camera - Assembly']
s.render.filepath=str(OUT/'assembly-v2.png')
bpy.ops.render.render(write_still=True,scene=s.name)
s.camera=bpy.data.objects['Camera - Rear Plan']
s.render.filepath=str(OUT/'rear-plan-v2.png')
bpy.ops.render.render(write_still=True,scene=s.name)
bpy.data.collections['REFERENCE - electronics and panel - do not print'].hide_render=True
s.camera=bpy.data.objects['Camera - Assembly']
s.render.filepath=str(OUT/'printed-plate-v2.png')
bpy.ops.render.render(write_still=True,scene=s.name)
