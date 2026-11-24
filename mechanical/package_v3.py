from pathlib import Path
import shutil,json,zipfile,hashlib
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/rev3'
src=OUT/'source';src.mkdir(exist_ok=True)
for n in ['rev3-parameters.json','build_mount_v3.py','csg.py','draw_layout_v3.py']:
    shutil.copy2(ROOT/n,src/n)
(src/'requirements.txt').write_text('manifold3d==3.5.4\ntrimesh==5.1.1\nshapely==2.2.0\nnumpy==2.5.4\nPillow>=11\n')
shutil.copy2(ROOT/'output/rev2/Adafruit-CC-BY-SA-3.0.txt',OUT/'Adafruit-CC-BY-SA-3.0.txt')
names=['PRINTING.txt','Adafruit-CC-BY-SA-3.0.txt','rear-frame-v3.stl','rear-frame-v3.scad',
 'm2-5-heat-set-sizing-coupon.stl','m2-5-heat-set-sizing-coupon.scad',
 'electronics-fit-check-v3.stl','electronics-fit-check-v3.scad',
 'matrix-rear-frame-v3.blend','layout-v3-actual-size.svg','layout-v3-dimensioned.png',
 'assembly-v3.png','printed-frame-v3.png','rear-plan-v3.png','validation.json','parameters-used.json']
paths=[OUT/n for n in names]+sorted(src.glob('*'))
manifest={str(p.relative_to(OUT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(OUT/'SHA256.json').write_text(json.dumps(manifest,indent=2));paths.append(OUT/'SHA256.json')
dest=ROOT/'output/matrix-rear-frame-v3.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:z.write(p,str(p.relative_to(OUT)))
with zipfile.ZipFile(dest) as z:assert z.testzip() is None
print(json.dumps({'archive':str(dest),'files':len(paths),'bytes':dest.stat().st_size},indent=2))
