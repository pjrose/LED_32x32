"""Small dual-output CSG: the same primitives generate manifold STL and OpenSCAD."""
import sys,json
from pathlib import Path
DEP=Path(__file__).resolve().parent/'.cad-deps'
if DEP.is_dir():sys.path.insert(0,str(DEP))
import manifold3d as mf
from shapely.geometry import box

def rounded(x,y,w,h,r=2):
    return box(x+r,y+r,x+w-r,y+h-r).buffer(r,quad_segs=8)

class Solid:
    def __init__(self,m,src):self.mesh,self.source=m,src
    def __add__(self,b):return Solid(self.mesh+b.mesh,'union(){\n'+self.source+b.source+'}\n')
    def __sub__(self,b):return Solid(self.mesh-b.mesh,'difference(){\n'+self.source+b.source+'}\n')
    def move(self,p):return Solid(self.mesh.translate(p),f'translate({list(p)}){{\n{self.source}}}\n')
    def rotate(self,z):return Solid(self.mesh.rotate([0,0,z]),f'rotate([0,0,{z}]){{\n{self.source}}}\n')

def union(parts):
    parts=list(parts)
    return Solid(mf.Manifold.batch_boolean([p.mesh for p in parts],mf.OpType.Add),'union(){\n'+''.join(p.source for p in parts)+'}\n')

def extrude(g,h,z=0):
    if g.geom_type=='MultiPolygon':return union(extrude(p,h,z) for p in g.geoms)
    rings=[list(g.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in g.interiors]
    cs=mf.CrossSection(rings,mf.FillRule.EvenOdd)
    pts=[];paths=[]
    for r in rings:
        paths.append(list(range(len(pts),len(pts)+len(r))))
        pts.extend([[round(x,6),round(y,6)] for x,y in r])
    return Solid(cs.extrude(h),f'linear_extrude(height={h}) polygon(points={json.dumps(pts)},paths={json.dumps(paths)});\n').move((0,0,z))

def cyl(x,y,z,h,d,d2=None,segments=64):
    d2=d if d2 is None else d2
    return Solid(mf.Manifold.cylinder(h,d/2,d2/2,circular_segments=segments),f'cylinder(h={h},d1={d},d2={d2},$fn={segments});\n').move((x,y,z))
