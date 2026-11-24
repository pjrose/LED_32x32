"""Run on the saved V3 copy in background, preserving the user's live scenes."""
import bpy
from pathlib import Path
OUT=Path(r'D:/LED_32x32/mechanical/output/rev3')
s=bpy.data.scenes['LED Matrix - Open Frame V3']
bpy.context.window.scene=s
bpy.data.collections['V3 REFERENCE - panel electronics fasteners - do not print'].hide_render=False
s.camera=bpy.data.objects['V3 Camera Assembly'];s.render.filepath=str(OUT/'assembly-v3.png')
for other in list(bpy.data.scenes):
    if other!=s:bpy.data.scenes.remove(other)
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'matrix-rear-frame-v3.blend'),check_existing=False)
