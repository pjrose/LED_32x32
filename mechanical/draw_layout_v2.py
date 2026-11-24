"""Produce a dimensioned 1:1 vector template and a readable layout PNG."""
import json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.cad-deps'))
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Point,Polygon,box
from shapely.affinity import rotate
from csg import rounded
D=json.loads((ROOT/'output/rev2/scene-data.json').read_text());P=D['parameters']
OUT=ROOT/'output/rev2';S=P['panel_size'];T=P['plate_thickness']
bx,by,z=D['board_origin'];nx,ny=P['nut_body_center_x'],P['nut_body_center_y']
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">',
     '<rect width="210" height="297" fill="white"/>',
     '<style>text{font-family:Arial,sans-serif;fill:#24384a} .s{font-size:2.7px}.m{font-size:3.1px}</style>',
     '<text x="9.1" y="12" font-size="5.5">Matrix rear plate - revision 2</text>',
     '<text x="9.1" y="20" class="m">REAR VIEW / all dimensions mm / fit-check prototype</text>',
     '<text x="9.1" y="27" class="m">Print at actual size (100%). Check the 100 mm scale below.</text>',
     '<g transform="translate(9.1,36)">']
W,H=1680,2200;scale=7.8;ox=92;oy=240
im=Image.new('RGB',(W,H),'white');draw=ImageDraw.Draw(im)
fp=Path(r'C:\Windows\Fonts\segoeui.ttf')
def font(sz):return ImageFont.truetype(str(fp),sz)
def xy(p):return (ox+p[0]*scale,oy+(S-p[1])*scale)
def poly(g,fill,stroke='#587666',sw=.4):
    shapes=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
    for gg in shapes:
        rings=[gg.exterior]+list(gg.interiors)
        path=' '.join('M '+' L '.join(f'{x:.3f},{S-y:.3f}' for x,y in r.coords)+' Z' for r in rings)
        svg.append(f'<path d="{path}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" fill-rule="evenodd"/>')
        draw.polygon([xy(p) for p in gg.exterior.coords],fill=fill,outline=stroke,width=max(1,int(sw*scale)))
        for r in gg.interiors:draw.polygon([xy(p) for p in r.coords],fill='white',outline=stroke,width=max(1,int(sw*scale)))
def line(points,color,width,dash=False):
    pts=' '.join(f'{x},{S-y}' for x,y in points)
    ds='stroke-dasharray="1.5 1.5"' if dash else ''
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" {ds}/>')
    draw.line([xy(p) for p in points],fill=color,width=max(1,int(width*scale)),joint='curve')
def label(text,p,size=3.0,color='#24384a',anchor='start'):
    svg.append(f'<text x="{p[0]}" y="{S-p[1]}" font-size="{size}" fill="{color}" text-anchor="{anchor}" style="fill:{color}">{text}</text>')
    draw.text(xy(p),text,font=font(round(size*scale)),fill=color,anchor={'start':'ls','middle':'ms','end':'rs'}[anchor])

poly(box(0,0,S,S),'#e6e9e9','#9aa5ae',.35)
for x,y in D['corner_centers']:
    poly(Point(x,y).buffer(3),'#d5b468','#78623c',.2)
    poly(Point(x,y).buffer(1.5),'#6b7175','#6b7175',.1)
outline=Polygon(D['plan_outline'])
poly(outline,'#d9e8df','#3d7459',.7)
for pts in D['voids']:
    visible=Polygon(pts).intersection(outline)
    if not visible.is_empty:poly(visible,'white','#a9bbb0',.2)
for x,y in D['midpoint_centers']:
    poly(Point(x,y).buffer(4),'#ffe2a6','#d0a659',.3)
    poly(Point(x,y).buffer(1.7),'white','#717c7c',.25)
poly(rounded(bx,by,63.5,44.45,2),'#2f5c51','#1f4239',.45)
for x,y in D['board_holes']:
    poly(Point(x,y).buffer(2.4),'#d2ba80','#d2ba80',.1)
    poly(Point(x,y).buffer(1.25),'#e8eeee','#55626a',.15)
np=rounded(nx-21,ny-12,26,24,1).union(rounded(nx+4,ny-7,17,14,1))
np=rotate(np,180,origin=(nx,ny))
poly(np,'#c9dfee','#4a7794',.4)
for x,y in D['nut_holes']:
    poly(Point(x,y).buffer(3.5),'#d4e1e9','#4a7794',.25)
    poly(Point(x,y).buffer(1.5),'white','#4a7794',.2)

line(D['routes']['ribbon'],'#c5ced9',2.4)
line(D['routes']['matrix'],'#cb6456',1.0)
line(D['routes']['controller'],'#cb6456',.8)
label('MatrixPortal S3',(bx+31.75,by+22),3.3,'white','middle')
label('4 x M2.5',(bx+31.75,by+15),2.7,'white','middle')
label('Lever nut',(nx,ny+1),3.1,'#244f6b','middle')
label('19 mm pitch',(nx,ny-5),2.6,'#244f6b','middle')

edge=S-P['inner_frame_edge_from_outer'];right=bx+63.5
line([(edge,106),(edge,159)],'#95a19c',.3,True)
line([(right,148.45),(right,156)],'#334b63',.25)
line([(right,153),(edge,153)],'#334b63',.35)
for x in [right,edge]:line([(x,151.5),(x,154.5)],'#334b63',.35)
label('23 mm',((right+edge)/2,155.5),3.1,'#24384a','middle')
label('Inner frame edge',(edge-1,160),2.4,'#586978','end')
label('4 midpoint M3 panel screws',(95.9,174),3.0,'#24384a','middle')
label('Corners clear for your magnetic standoffs',(95.9,3),2.8,'#24384a','middle')
label('HUB75 input',(35,140),2.6,'#536779')
label('Supply',(48,47),2.8,'#536779')
svg.append('</g>')
draw.text((ox,50),'Matrix rear plate - revision 2',font=font(47),fill='#24384a')
draw.text((ox,120),'Rear view matching your sketch / fit-check prototype',font=font(26),fill='#536779')
lines=[
    'Plate: 191.8 x 191.8 x 3.2 mm / direct mounting posts: 8 mm high',
    'Four corner cutouts: 25 mm radius around existing corner inserts',
    'M2.5 screws and captured nuts at all six electronics mounting points',
    'Planned leads: matrix 46.7 / 50.8 mm; controller 69.8 / 100 mm',
    'Ribbon: 220.4 / 254 mm. Route lines are schematic; dry-fit actual cables.',
    '23 mm inset uses an inner frame edge estimated from the drawing.'
]
for i,t in enumerate(lines):
    y=240+i*6.2
    svg.append(f'<text x="9.1" y="{y}" class="m">{t.replace("&","&amp;")}</text>')
    draw.text((ox,1810+i*42),t,font=font(23),fill='#344b60')
svg += ['<line x1="9.1" y1="284" x2="109.1" y2="284" stroke="#24384a" stroke-width=".5"/>',
        '<path d="M9.1,282 V286 M109.1,282 V286" stroke="#24384a" stroke-width=".5"/>',
        '<text x="59.1" y="292" class="m" text-anchor="middle">100 mm calibration</text>','</svg>']
(OUT/'layout-v2-actual-size.svg').write_text('\n'.join(svg))
im.save(OUT/'layout-v2-dimensioned.png')
