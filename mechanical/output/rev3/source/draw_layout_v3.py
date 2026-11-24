"""Dimensioned review PNG and actual-size SVG, with separate reference overlays."""
from pathlib import Path
import json,sys,html
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.cad-deps'))
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Polygon,Point,box
OUT=ROOT/'output/rev3';D=json.loads((OUT/'scene-data.json').read_text());P=D['parameters']
S=P['panel_size'];C=S/2;R=D['report']['layout']
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">',
 '<rect width="210" height="297" fill="white"/>',
 '<style>text{font-family:Arial,sans-serif;fill:#263e4b}</style>',
 '<text x="9.1" y="12" font-size="5.5">Matrix open frame / revision 3</text>',
 '<text x="9.1" y="20" font-size="3.1">Rear view / dimensions in mm / physical fit not yet tested</text>',
 '<text x="9.1" y="27" font-size="3.1">Actual size: print at 100%. Verify the 100 mm scale.</text>',
 '<g transform="translate(9.1,36)">']
W,H=1680,2200;scale=7.8;ox=92;oy=240
im=Image.new('RGB',(W,H),'white');draw=ImageDraw.Draw(im)
def font(sz):return ImageFont.truetype(r'C:/Windows/Fonts/segoeui.ttf',sz)
def xy(p):return (ox+p[0]*scale,oy+(S-p[1])*scale)
def poly(g,fill,stroke='#47765c',sw=.3):
    for gg in (list(g.geoms) if g.geom_type=='MultiPolygon' else [g]):
        rings=[gg.exterior]+list(gg.interiors)
        path=' '.join('M '+' L '.join(f'{x:.4f},{S-y:.4f}' for x,y in r.coords)+' Z' for r in rings)
        svg.append(f'<path d="{path}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" fill-rule="evenodd"/>')
        draw.polygon([xy(p) for p in gg.exterior.coords],fill=fill,outline=stroke,width=max(1,int(sw*scale)))
        for r in gg.interiors:draw.polygon([xy(p) for p in r.coords],fill='white',outline=stroke,width=max(1,int(sw*scale)))
def line(points,color='#536b79',width=.3,dash=False):
    pts=' '.join(f'{x:.4f},{S-y:.4f}' for x,y in points)
    ds='stroke-dasharray="1.5 1.5"' if dash else ''
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" {ds}/>')
    draw.line([xy(p) for p in points],fill=color,width=max(1,int(width*scale)),joint='curve')
def label(t,p,size=3,color='#263e4b',anchor='start'):
    svg.append(f'<text x="{p[0]}" y="{S-p[1]}" font-size="{size}" text-anchor="{anchor}" style="fill:{color}">{html.escape(t)}</text>')
    draw.text(xy(p),t,font=font(round(size*scale)),fill=color,anchor={'start':'ls','middle':'ms','end':'rs'}[anchor])
def dimh(x1,x2,y,t):
    line([(x1,y),(x2,y)])
    for x in [x1,x2]:line([(x,y-1.3),(x,y+1.3)])
    label(t,((x1+x2)/2,y+2),2.9,anchor='middle')
def dimv(y1,y2,x,t):
    line([(x,y1),(x,y2)])
    for y in [y1,y2]:line([(x-1.2,y),(x+1.2,y)])
    label(t,(x-2,(y1+y2)/2),2.8,anchor='end')
# White holes in the printable frame expose the reference panel beneath.
poly(box(0,0,S,S),'#f2f3f4','#a9b1b5')
for item in D['plan_polygons']:
    poly(Polygon(item['exterior'],item['holes']),'#c7dfce','#47765c',.55)
for x,y in D['corner_centers']:
    poly(Point(x,y).buffer(3),'#d2b568','#8a743e',.25)
    poly(Point(x,y).buffer(1.5),'white','#8a743e',.2)
for x,y in D['midpoint_centers']:
    poly(Point(x,y).buffer(3.2),'#ffe4b5','#9a7843',.3)
    poly(Point(x,y).buffer(1.7),'white','#9a7843',.2)
for x,y in D['board_holes']+D['nut_holes']:
    poly(Point(x,y).buffer(4),'#9bc6ab','#47765c',.25)
    poly(Point(x,y).buffer(2),'white','#47765c',.25)
line([(5,C),(S-5,C)],'#8b9aab',.25,True)
line([(C,5),(C,S-5)],'#8b9aab',.25,True)
bx,by,bw,bh=D['board_footprint']
poly(box(bx,by,bx+bw,by+bh),'#edf4f0','#284f43',.5)
poly(Polygon(D['nut_outline']),'#e8f0f6','#496e8a',.5)
for x,y in D['nut_holes']:
    poly(Point(x,y).buffer(3.5),'#e8f0f6','#496e8a',.25)
    poly(Point(x,y).buffer(1.5),'white','#496e8a',.2)
for x,y in D['board_holes']:
    poly(Point(x,y).buffer(2.2),'#d7c08a','#8a743e',.25)
    poly(Point(x,y).buffer(1.25),'white','#8a743e',.2)
# Planar wire paths are schematic; length estimates exclude real plug takeoffs.
line(D['routes']['ribbon'],'#b6c2d0',1.4)
line(D['routes']['matrix'],'#c86a57',.65)
line(D['routes']['controller'],'#c86a57',.65)
label('MatrixPortal S3',(bx+bw/2,117),3.1,anchor='middle')
label('4 x M2.5 inserts',(bx+bw/2,111),2.5,anchor='middle')
label('Lever nut',(127.4,109),3,anchor='middle')
label('2 x M2.5',(127.4,103),2.5,anchor='middle')
dimh(117.9,136.9,86,'19')
dimh(44.59,64.275,156,'19.685')
dimv(95.9,136.54,32,'40.64')
line([(12.7,150),(12.7,169)],'#8a9792',.25,True)
line([(bx,151.78),(bx,169)])
dimh(12.7,bx,166,'23 nominal')
label('Inset from inner plastic edge',(12,173),2.5)
label('Centerline: PCB pair + lever holes',(109,72),2.7)
line([(123,75),(123,82)])
label('4 midpoint M3 panel screws',(C,180),2.8,anchor='middle')
label('All four corners clear',(C,7),2.8,anchor='middle')
label('HUB75 IN',(58.39,21),2.5,anchor='middle')
label('Matrix power',(158,134),2.5,anchor='middle')
dimh(0,S,-5,'191.8 overall')
svg.append('</g>')
draw.text((ox,48),'Matrix open frame / revision 3',font=font(47),fill='#263e4b')
draw.text((ox,119),'Rear view matching your latest sketch',font=font(28),fill='#536b79')
notes=[
 '4 mm border and crossmembers; six local insert posts reach 8 mm overall.',
 'M2.5 inserts: 4.6 mm OD x 5.7 mm long; pilot 4.0 x 6.7 mm deep.',
 'Main cross: 10 mm wide. Upper PCB branch: 8 mm. Border: 12 mm.',
 f"Planar routes: matrix {R['matrix_route_mm']} / 50.8; controller {R['controller_route_mm']} / 100; ribbon {R['ribbon_route_mm']} / 254 mm.",
 '19 mm lever pitch and approximate body envelope: verify using fit check.',
 'Print sizing coupon first. No physical insert or connected-cable test yet.'
]
for i,t in enumerate(notes):
    svg.append(f'<text x="9.1" y="{244+i*5.5}" font-size="2.75">{html.escape(t)}</text>')
    draw.text((ox,1835+i*45),t,font=font(23),fill='#344b60')
svg.extend(['<path d="M9.1,282 V286 M9.1,284 H109.1 M109.1,282 V286" fill="none" stroke="#263e4b" stroke-width=".5"/>',
 '<text x="59.1" y="292" font-size="3" text-anchor="middle">100 mm calibration</text>','</svg>'])
(OUT/'layout-v3-actual-size.svg').write_text('\n'.join(svg),encoding='utf-8')
im.save(OUT/'layout-v3-dimensioned.png')
print(OUT/'layout-v3-dimensioned.png')
