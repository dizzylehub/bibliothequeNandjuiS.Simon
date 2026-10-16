"""V8 D : mobilier original et scène de présentation, en mètres.
Architecture issue de scene_v8.npz. Mobilier D de conception, non EXE.
Usage : python design.py --mode interior|axo|section|studio --view P1 --res 1600.
"""
from pathlib import Path
import sys, math, argparse, json
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import rendu_blender as RB
OUT=ROOT/'indice_d'

def box(name,loc,dim,mat,r=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if r:
        b=o.modifiers.new('Arêtes adoucies','BEVEL');b.width=min(r,min(dim)*.48);b.segments=5
        o.modifiers.new('Normales pondérées','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,mat,r2=None):
    a,b=Vector(a),Vector(b);d=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(a+b)/2)
    o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

def curve(name,points,r,mat):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=4;c.resolution_u=20;c.use_fill_caps=True
    s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o

def pill(name,loc,w,d,h,mat):
    # Exact capsule outline: two semicircles, straight long edges.
    rad=min(w,d)/2; span=w/2-rad
    pts=[]
    for cx,angle in ((span,-math.pi/2),(-span,math.pi/2)):
        for i in range(33):
            a=angle+i*math.pi/32;pts.append((cx+rad*math.cos(a),rad*math.sin(a)))
    n=len(pts);verts=[(x,y,z) for z in (-h/2,h/2) for x,y in pts]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(mat)
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.location=loc
    mod=o.modifiers.new('Chant doux','BEVEL');mod.width=.007;mod.segments=3;o.modifiers.new('Normales','WEIGHTED_NORMAL')
    return o

def lounge(M,terrace=False):
    wood=M['Noyer'];fabric=M['Crème'] if terrace else M['Velours olive'];leather=M['Velours cognac']
    for x in (-.29,.29):
        rod('Pied fuselé avant',(x*1.08,-.29,0),(x,-.20,.35),.021,wood,.029)
        rod('Pied fuselé arrière',(x*1.08,.34,0),(x,.19,.35),.021,wood,.029)
        curve('Accoudoir sculpté',[(x,-.32,.57),(x,-.17,.63),(x,.15,.65),(x,.31,.73)],.028,wood)
        rod('Support accoudoir',(x,-.20,.34),(x,-.22,.61),.015,wood)
    box('Cadre assise',(0,.01,.315),(.60,.64,.075),wood,.03)
    box('Coussin assise déhoussable',(0,-.015,.405),(.60,.61,.13),fabric,.065)
    back=box('Dossier incliné',(0,.265,.67),(.60,.145,.43),fabric,.065);back.rotation_euler.x=math.radians(-12)
    # Piping follows the visible cushion edge, not a generic rectangular block.
    curve('Passepoil assise',[(-.25,-.30,.42),(.25,-.30,.42),(.29,-.23,.42),(.29,.21,.42)],.0015,fabric)
    for x in (-.25,.25):rod('Traverse dossier',(x,.21,.38),(x,.35,.85),.018,wood)
    if terrace:
        for i in range(15):
            x=-.25+i*.5/14
            curve('Tressage extérieur',[(x,.32,.45),(x,.37,.65),(x,.40,.82)],.005,M['Canne'])

def table(M,w=1.60,d=.90,h=.75):
    pill('Plateau galet',(0,0,h-.02),w,d,.04,M['Noyer'])
    for x in (-w*.27,w*.27):
        pill('Socle oblong',(x,0,(h-.06)/2),.23,d*.62,h-.06,M['Noyer'])
        pill('Patin bronze',(x,0,.012),.25,d*.64,.024,M['Laiton'])

def dining(M):
    for x in (-.20,.20):
        for y in (-.18,.18):rod('Pied chaise',(x*1.1,y*1.18,0),(x,y,.44),.015,M['Noyer'],.023)
    pill('Assise chaise',(0,0,.4275),.49,.44,.085,M['Velours cognac'])
    for x in (-.20,.20):rod('Montant dossier',(x,.17,.38),(x,.24,.80),.017,M['Noyer'])
    curve('Dossier enveloppant',[(-.23,.12,.77),(-.17,.25,.80),(0,.29,.81),(.17,.25,.80),(.23,.12,.77)],.048,M['Noyer'])

def console(M):
    pill('Comptoir courbe',(0,0,1.03),1.8,.62,.05,M['Noyer'])
    pill('Corps accueil',(0,0,.54),1.72,.55,.94,M['Crème'])
    for x in np.linspace(-.55,.55,23):box('Lattis fin',(float(x),-.282,.54),(.018,.018,.83),M['Noyer'],.006)
    pill('Socle en retrait',(0,0,.06),1.55,.44,.12,M['Noyer'])

def materials():
    M=RB.materiaux()
    # Fine noise-dominant grain: avoids broad repeating zebra bands.
    for key in ['Noyer','Noyer clair','Contreplaqué']:
        nt=M[key].node_tree
        for n in nt.nodes:
            if n.type=='TEX_WAVE':n.inputs['Scale'].default_value=38;n.inputs['Distortion'].default_value=7
            if n.type=='MIX':n.inputs['Factor'].default_value=.96
            if n.type=='BSDF_PRINCIPLED':n.inputs['Coat Weight'].default_value=.08;n.inputs['Roughness'].default_value=.48
    M['Velours olive']=RB.uni('Lin olive profond','#39422d',.86,0,.025,190,.001)
    M['Velours cognac']=RB.uni('Cuir cognac patiné','#74442b',.62,0,.025,130,.001)
    M['Crème']=RB.uni('Lin écru','#dfd9c9',.84,0,.035,180,.001)
    M['Cloison neuve']=RB.uni('Chaux coquille','#e6e3dc',.95,0,.025,7,0)
    M['Maçonnerie existante']=M['Cloison neuve']
    M['Moutarde']=RB.velours('Tabac doux','#6f593d','#9d8564')
    return M

def place(fn,M,center,angle=0,**kw):
    before=set(bpy.data.objects);fn(M,**kw)
    parent=bpy.data.objects.new('Mobilier D',None);bpy.context.collection.objects.link(parent)
    for o in set(bpy.data.objects)-before-{parent}:o.parent=parent
    parent.location=center;parent.rotation_euler.z=angle

def scene(M):
    RB.construire(M)
    for o in list(bpy.data.objects):
        if o.type!='MESH':continue
        name=o.name
        pts=np.array([tuple(o.matrix_world@Vector(c)) for c in o.bound_box]);lo,hi=pts.min(0),pts.max(0);c=(lo+hi)/2
        replacement=None;kw={};angle=0
        if name.startswith('Fauteuil de lecture'):replacement=lounge;angle=math.pi if c[1]>5.5 else 0
        elif name.startswith('Chaise ÖVERALLT'):replacement=lounge;kw={'terrace':True};angle=math.pi/5 if c[0]<3 else -math.pi/5
        elif name.startswith(('Chaise table','Chaise poste','Chaise salle')):replacement=dining;angle=math.pi if c[1]<2 else 0
        elif name.startswith("Table d'hôtes"):replacement=table
        elif name.startswith('Table basse du salon'):replacement=table;kw={'w':.72,'d':.56,'h':.40}
        elif name.startswith('Table basse extérieure'):replacement=table;kw={'w':float(hi[0]-lo[0]),'d':float(hi[1]-lo[1]),'h':.38}
        if replacement:
            bpy.data.objects.remove(o,do_unlink=True);place(replacement,M,(float(c[0]),float(c[1]),float(lo[2])),angle,**kw)
        elif name.startswith('Plafond en lames'):
            o.data.materials.clear();o.data.materials.append(M['Cloison neuve'])
    # Small tactile objects placed on the communal table: original accessories.
    for x in (4.45,5.1):
        box('Livre posé',(x,2.1,.775),(.18,.26,.035),M['Crème'],.003)
        rod('Tasse céramique',(x+.13,2.08,.75),(x+.13,2.08,.84),.035,M['Claustra terre cuite'])

def prepare_cut():
    """Freeze evaluated meshes/curves in world space before geometric section."""
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    frozen=[]
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ('MESH','CURVE'):continue
        ev=obj.evaluated_get(dg)
        mesh=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
        mesh.transform(obj.matrix_world)
        frozen.append((obj,mesh,obj.name))
    for obj,mesh,name in frozen:
        bpy.data.objects.remove(obj,do_unlink=True)
        new=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(new)

def export_scene():
    """Export evaluated D furniture and architectural meshes for measured drawings."""
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];objects=[]
    for obj in bpy.context.scene.objects:
        if obj.type not in ('MESH','CURVE'):continue
        ev=obj.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
        v=[tuple(ev.matrix_world@x.co) for x in me.vertices];t=[tuple(x.vertices) for x in me.loop_triangles]
        if v and t:objects.append({'nom':obj.name,'n_v':len(v),'n_t':len(t)});verts.extend(v);faces.extend(t)
        ev.to_mesh_clear()
    np.savez_compressed(OUT/'scene_d.npz',V=np.array(verts),T=np.array(faces),objets=json.dumps(objects))

def camera(pos,target,res=1600,ortho=None):
    c=bpy.data.cameras.new('Caméra D');o=bpy.data.objects.new('Caméra D',c);bpy.context.collection.objects.link(o)
    o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();c.lens=35
    if ortho:c.type='ORTHO';c.ortho_scale=ortho
    sc=bpy.context.scene;sc.camera=o;sc.render.resolution_x=res;sc.render.resolution_y=round(res*.67)

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['interior','axo','section','studio','plan'],default='interior');p.add_argument('--view',default='P1');p.add_argument('--res',type=int,default=1600);p.add_argument('--samples',type=int,default=48);a=p.parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True);M=materials();sc=bpy.context.scene
    if a.mode=='studio':
        {'FAUTEUIL':lounge,'TABLE':table,'CHAISE':dining,'ACCUEIL':console,'TERRASSE':lambda m:lounge(m,True)}[a.view](M)
        box('Cyclorama',(0,0,-.06),(200,200,.10),M['Cloison neuve'],0)
        camera((2.4,-3.6,2.1),(0,0,.48),a.res,2.5 if a.view in ['TABLE','ACCUEIL'] else 1.75)
    else:
        scene(M)
        if a.mode=='interior':
            export_scene()
        if a.mode in ('axo','section','plan'):prepare_cut()
        if a.mode=='axo':
            for o in list(bpy.data.objects):
                if o.name.startswith(('Plafond','Dalle haute','Imposte','Plancher de la réserve')):bpy.data.objects.remove(o,do_unlink=True)
            RB.trancher((0,0,2.5),(0,0,1),False)
            camera((17,-21,23) if a.view=='01' else (-17,-19,23),(3.4,1.1,.7),a.res,22)
        elif a.mode=='plan':
            RB.trancher((0,0,1.3),(0,0,1),False);RB.camera_ortho('PLAN')
        elif a.mode=='section':
            RB.ORTHO['COUPE_AA'].update(centre=(1.0,1.65),px=(2600,780))
            RB.ORTHO['COUPE_BB'].update(centre=(3.4,1.65),largeur=8.5,px=(2400,1200))
            d=RB.ORTHO[a.view];RB.trancher(d['plan'],d['normale'],False);RB.camera_ortho(a.view)
            sc.render.resolution_percentage=100
        else:
            RB.eclairage(False,M)
            for l in bpy.data.lights:
                if l.type=='POINT':l.color=RB.kelvin_rgb(3200)
            pos,target,fov=RB.VUES[a.view];camera(pos,target,a.res);sc.camera.data.angle=math.radians(fov-8)
            if a.view in ('P3','P6'):RB.environnement(False,M)
    w=bpy.data.worlds.new('Ciel neutre');sc.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.78,.83,.88,1);w.node_tree.nodes['Background'].inputs[1].default_value=.35
    for pos,power,size in [((2,-4,6),1000,6),((6,4,5),700,5),((-2,4,4),400,4)]:
        l=bpy.data.lights.new('Lumière douce','AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new('Lumière douce',l);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((3,2,0))-o.location).to_track_quat('-Z','Y').to_euler()
    if a.mode in ('interior','section'):
        # Broad bounce source below ceiling, balances glazing without orange wash.
        l=bpy.data.lights.new('Rebond plafond','AREA');l.energy=180;l.size=4;o=bpy.data.objects.new('Rebond plafond',l);bpy.context.collection.objects.link(o);o.location=(4.5,4,2.85)
    RB.regler(a.samples,False);sc.view_settings.exposure=-1.0 if a.mode=='studio' else -.35;sc.render.threads_mode='FIXED';sc.render.threads=4
    dest=OUT/('mobilier' if a.mode=='studio' else 'images')/f'{a.mode}_{a.view}.png'
    sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
    if a.mode=='interior':bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'SCENE_V8_D.blend'))
    if a.mode=='studio':bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mobilier'/f'{a.view}.blend'))
    print(dest)
if __name__=='__main__':main()
