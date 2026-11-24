"""Run on the saved V4 copy in background, preserving the user's live scenes."""
import bpy
from pathlib import Path
OUT=Path(r'D:/LED_32x32/mechanical/output/rev4')
s=bpy.data.scenes['LED Matrix - Open Frame V4']
bpy.context.window.scene=s
bpy.data.collections['V4 REFERENCE - panel electronics fasteners - do not print'].hide_render=False
s.camera=bpy.data.objects['V4 Camera Assembly'];s.render.filepath=str(OUT/'assembly-v4.png')
for other in list(bpy.data.scenes):
    if other!=s:bpy.data.scenes.remove(other)
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'matrix-rear-frame-v4.blend'),check_existing=False)
