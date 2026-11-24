"""Prepare versioned sources, preserving the earlier revision."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
P=json.loads((R/'rev3-parameters.json').read_text())
P.update(corner_clear_radius=13.0,board_seat_z=4.0,nut_seat_z=4.0,
         nut_center_x=112.9,insert_pocket_depth=4.0,insert_length=4.0,
         insert_family='M2.5 heat-set, 4.6 mm OD / 4.0 mm pilot; through bore, preferably 4 mm long')
P.pop('insert_boss_diameter')
P['notes'].update(
 layout='Portrait board left and lever connector right. Lever body left long edge touches the right edge of the vertical crossmember. Both lever holes and lower PCB pair remain on the horizontal centerline.',
 frame='Uniform 4 mm thickness throughout, no raised posts. 13 mm radius corner cutouts centered on factory corner inserts.',
 inserts='Six 4.0 mm through bores with top 0.35 mm deep conical lead-ins widening to 4.7 mm. Prefer 4 mm long inserts to keep both faces flush. A 5.7 mm insert seated flush on top protrudes 1.7 mm below the frame; confirm clearance.',
 lever='Body translated left by 14.5 mm from V3, without rotation. Left wide-body edge X=100.9 equals the right edge of the vertical 10 mm crossmember. 19 mm ear-hole pitch. 42 x 24 modeled body footprint from reference; actual body envelope is approximate.')
(R/'rev4-parameters.json').write_text(json.dumps(P,indent=2))
s=(R/'build_mount_v3.py').read_text().replace('rev3','rev4').replace('-v3','-v4')
s=s.replace("top=P['board_seat_z'];d=P['insert_boss_diameter']", "top=P['board_seat_z']\nassert top==T==P['nut_seat_z']==4.0")
s=s.replace("for x,y in bhole+nhole:\n    frame+=cyl(x,y,T-EPS,top-T+EPS,d)\n",'')
s=s.replace("    depth=P['insert_pocket_depth'];c=P['insert_entrance_chamfer']\n    return cyl(x,y,top-depth,depth+EPS,pilot)+cyl(x,y,top-c,c+EPS,pilot,pilot+2*c)",
 "    c=P['insert_entrance_chamfer']\n    return cyl(x,y,-EPS,T+2*EPS,pilot)+cyl(x,y,top-c,c+EPS,pilot,pilot+2*c)")
s=s.replace('# Use the same blind pocket/boss height as production to test the real insert.', '# Same through bore and frame thickness as the final part.')
s=s.replace('for x,y in bhole+nhole:check+=cyl(x,y,T-EPS,top-T+EPS,d)\n','')
s=s.replace('# face is only Z=2.45, so a branch directly under it would be a real collision.', '# face now reaches Z=-1.55, into the open rear-panel cavity.')
s=s.replace('cyl(x,y,-1,12,49.8)',"cyl(x,y,-1,12,2*P['corner_clear_radius']-.02)")
s=s.replace("assert abs(top-P['insert_pocket_depth']-1.3)<1e-7", "assert abs(top-P['insert_pocket_depth'])<1e-7\nassert abs(nx-12-(C+w/2))<1e-7\nfor x,y in bhole+nhole:\n    assert (frame.mesh ^ cyl(x,y,-EPS,T+2*EPS,P['insert_pilot_diameter']-.02).mesh).volume()<1e-6")
s=s.replace("'corner_clear_radius_mm':25", "'corner_clear_radius_mm':P['corner_clear_radius']")
s=s.replace("'pocket_floor_mm':top-P['insert_pocket_depth'],", "'pocket_floor_mm':0.0,'insert_bores_through':True,\n    'insert_lead_in_depth_mm':P['insert_entrance_chamfer'],\n    'insert_lead_in_top_diameter_mm':P['insert_pilot_diameter']+2*P['insert_entrance_chamfer'],\n    'nut_left_body_edge_x_mm':nx-12,'vertical_cross_right_edge_x_mm':C+w/2,")
(R/'build_mount_v4.py').write_text(s)
for n in ['blender_scene','render_blender','finalize_blender','draw_layout','package']:
    s=(R/(n+'_v3.py')).read_text().replace('rev3','rev4').replace('-v3','-v4').replace('_v3','_v4').replace('V3','V4').replace('revision 3','revision 4')
    if n=='blender_scene':
        s=s.replace("frame['local_post_height_mm']=8", "frame['raised_post_height_mm']=0")
        s=s.replace('(x,y,10.5)','(x,y,6.5)').replace('(x,y,10.4)','(x,y,6.4)').replace('(x,y,11.3)','(x,y,7.3)')
        s=s.replace("'matrix',17","'matrix',13").replace("'controller',18","'controller',14").replace('(x,y+shift,20)','(x,y+shift,16)')
    if n=='draw_layout':
        s=s.replace("    poly(Point(x,y).buffer(4),'#9bc6ab','#47765c',.25)\n",'')
        s=s.replace('(127.4,109)',"(P['nut_center_x'],109)").replace('(127.4,103)',"(P['nut_center_x'],103)")
        s=s.replace("dimh(117.9,136.9,86,'19')", "dimh(D['nut_holes'][0][0],D['nut_holes'][1][0],86,'19')")
        s=s.replace("label('Centerline: PCB pair + lever holes',(109,72),2.7)","label('Nut body flush with vertical cross',(104,72),2.7)")
        s=s.replace("line([(123,75),(123,82)])", "line([(103,74),(100.9,106)])")
        s=s.replace("'4 mm border and crossmembers; six local insert posts reach 8 mm overall.'", "'Uniform 4 mm frame. PCB and lever nut seat directly on the crossmembers.'")
        s=s.replace("'M2.5 inserts: 4.6 mm OD x 5.7 mm long; pilot 4.0 x 6.7 mm deep.'", "'Six 4.0 mm through bores; 0.35 mm conical lead-ins widen to 4.7 mm.'")
        s=s.replace("'Main cross: 10 mm wide. Upper PCB branch: 8 mm. Border: 12 mm.'", "'Corner cutouts: 13 mm radius / 26 mm diameter. Main cross: 10 mm wide.'")
        s=s.replace("'19 mm lever pitch and approximate body envelope: verify using fit check.'", "'19 mm lever pitch. Prefer 4 mm long inserts; longer inserts protrude below.'")
    (R/(n+'_v4.py')).write_text(s)
print('Prepared V4 source files')
