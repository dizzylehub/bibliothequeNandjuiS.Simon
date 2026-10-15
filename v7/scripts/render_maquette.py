#!/usr/bin/env python3
"""Rendus photoréalistes des vues de maquette extraites de l'IFC V7.

Usage : python3 v7/scripts/render_maquette.py [--only axo|interieur_entree|interieur_accueil|terrasse]
       [--size 2200 1467] [--ss 1]
Les paramètres caméra et SHA-256 source sont écrits à côté de chaque image.
"""
from __future__ import annotations
import argparse, hashlib, json, logging, os, sys, time
from pathlib import Path
import numpy as np
import ifcopenshell, ifcopenshell.geom
import ifcopenshell.util.element as ue

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'v7'/'DECIMO_PROPOSITION_V7.ifc'
OUT=ROOT/'v7'/'assets'/'ifc'
V5S=ROOT/'v5'/'scripts'
sys.path.insert(0,str(V5S))
from scene import role as role_v5, tag as tag_v5  # noqa: E402
from rendu_gl import render, camera_info  # noqa: E402

logging.disable(logging.WARNING)

# Same sun/material renderer as V5, with a warmer interior bounce for the iroko/sand palette.
INT=dict(shadows=True,sun_dir=(-.30,-.70,.65),sky=(.98,.95,.90),ground=(.86,.80,.72),
         sun_col=(1.0,.90,.76),fill_dir=(.15,-1.0,.25),fill_k=.24,exposure=.92,emissive=1.25,
         background=(.95,.93,.90))
AXO=dict(shadows=True,sun_dir=(-.38,-.62,.69),sky=(.78,.78,.80),ground=(.68,.68,.68),
         fill_k=.10,exposure=1.0,background=(.92,.92,.92))

CAMERAS={
 'axo':dict(position=(11.8,-12.4,12.4),target=(3.25,2.10,1.05),up=(0,0,1),ortho_h=9.15,near=.1,far=100),
 'interieur_entree':dict(position=(4.10,.24,1.58),target=(5.42,5.90,1.57),up=(0,0,1),fov_v=62.0,near=.05,far=80),
 'interieur_accueil':dict(position=(5.68,5.65,1.58),target=(1.55,1.92,1.42),up=(0,0,1),fov_v=64.0,near=.05,far=80),
 'poste_accueil':dict(position=(4.30,1.40,1.60),target=(1.40,1.30,1.30),up=(0,0,1),fov_v=70.0,near=.05,far=80),
 'terrasse':dict(position=(4.10,.52,1.58),target=(4.10,-2.85,.72),up=(0,0,1),fov_v=68.0,near=.05,far=80),
}
DESCRIPTIONS={
 'axo':'Axonométrie coupée à z=+2,40 m : intérieur complet et terrasse, projet V7 visible.',
 'interieur_entree':'Depuis le seuil d’entrée vers la bibliothèque : comptoir unique, rayonnages nord/est et coworking.',
 'interieur_accueil':'Depuis le fond de la bibliothèque vers le comptoir, l’accueil et la salle vitrée.',
 'poste_accueil':'Depuis le passage public vers le poste d’accueil-café unique et la salle vitrée.',
 'terrasse':'Depuis le seuil vers la terrasse couverte et l’emprise optionnelle d’extension.',
}
# Masques des vues : catégories de contexte extérieures issues du mapping de scène V5.
BASE_HIDE={'logements','voisin','fenetre_logt','arbre','trottoir','sol_ext','joint','technique'}
CEILING_NAMES=('faux-plafond','plafond acoustique','plafond hydrofuge')
LEGACY_TREE_LIGHTS=("Anneau LED indirect de l'oculus","Anneau LED sous la canopée de l'arbre à livres")
LEGACY_CEILING_LIGHT_PREFIXES=('Downlight encastré','Linéaire suspendu','Suspension terre cuite')
CUT_WALL_NAMES=('Enduit terre - mur est salle de lecture','Enduit terre - face intérieure de la façade',
                'Mur de base:Agglos creux 15 + Enduit 2 Faces 1.5_K&D:4350588',
                'V7 — façade rectiligne segmentée autour baies rectangulaires')


def role_v6(e):
    """Classification sémantique, en réutilisant les règles de scène V5 + objets V6."""
    n=e['nom'].lower(); c=e['classe']
    if e.get('is_v6') or e.get('is_v7'):
        if 'dallage extension terrasse' in n: return 'sol'
        if 'retour opaque wc' in n: return 'cloison'
        if 'plateforme réserve' in n: return 'mobilier'
        if 'intention lumière' in n: return 'luminaire'
        if 'vitrage' in n: return 'vitrage'
        if 'trame droite' in n or 'cadres et montant' in n: return 'cloison'
        if 'porte grille rectangulaire' in n: return 'cloison'
        if c in ('IfcFurnishingElement','IfcFurniture'): return 'mobilier'
    if any(k in n for k in CEILING_NAMES): return 'plafond'
    return role_v5(e)


def load_scene(path):
    """Charge les maillages Body avec les couleurs/style et psets du modèle IFC."""
    f=ifcopenshell.open(str(path)); s=ifcopenshell.geom.settings(); s.set('use-world-coords',True)
    out=[]
    for p in f.by_type('IfcProduct'):
        if p.Representation is None or p.is_a('IfcOpeningElement') or p.is_a('IfcSpace'): continue
        reps=p.Representation.Representations
        rep=next((r for r in reps if r.RepresentationIdentifier=='Body'),None)
        if rep is None: continue
        try:
            g=ifcopenshell.geom.create_shape(s,p,rep).geometry
        except Exception as exc:
            print(f"Maillage ignoré #{p.id()} {p.Name}: {str(exc)[:100]}",file=sys.stderr); continue
        v=np.asarray(g.verts,dtype=np.float64).reshape(-1,3)
        fc=np.asarray(g.faces,dtype=np.int64).reshape(-1,3)
        mids=np.asarray(g.material_ids,dtype=np.int64)
        iids=np.asarray(g.item_ids,dtype=np.int64)
        cols=[]
        for m in g.materials:
            try:
                comp=m.diffuse.components
                rgba=(float(comp[0]),float(comp[1]),float(comp[2]),1.0-float(m.transparency or 0.0))
            except Exception: rgba=(.76,.72,.65,1.0)
            cols.append(rgba)
        cols=np.asarray(cols or [(.76,.72,.65,1.0)])
        rgba=cols[np.clip(mids,0,len(cols)-1)] if len(mids) else np.tile(cols[0],(len(fc),1))
        ps=ue.get_psets(p)
        items=[]
        for k in np.unique(iids):
            sel=iids==k; items.append((fc[sel],rgba[sel]))
        psets=ps.get('KDEMI_Option_C_V6',{})
        out.append(dict(guid=p.GlobalId,classe=p.is_a(),nom=p.Name or '',tag=tag_v5(p.Name),
                        v4=False,repere=None,statut='',ptype=getattr(p,'PredefinedType',None),
                        verts=v,items=items,lot=ps.get('KDEMI_Esquisse',{}).get('Lot',''),
                        is_v6=(p.Name or '').startswith('V6 —'),is_v7=(p.Name or '').startswith('V7 —'),
                        v6props=psets,v7props=ps.get('KDEMI_Option_C_V7',{})))
    return out


def render_arrays(scene, view):
    if view=='terrasse':
        hide=BASE_HIDE-{'trottoir'}
    else:
        hide=BASE_HIDE
    excluded=[]
    kept=[]
    for e in scene:
        r=role_v6(e)
        omit=(r in hide)
        # Interior/exterior views remove ceiling planes so they cannot cap/collapse the room.
        if view in ('axo','interieur_entree','interieur_accueil','poste_accueil','terrasse') and r=='plafond': omit=True
        # Do not present the unverified high storage or optional terrace slab as built work.
        if 'plateforme réserve haute arrière' in e['nom'].lower() or 'dallage extension terrasse' in e['nom'].lower(): omit=True
        # These legacy rings belong to the removed central book tree and float without it.
        if e['nom'] in LEGACY_TREE_LIGHTS: omit=True
        # Old ceiling fittings remain in IFC for coordination but float when the ceiling is hidden.
        if view in ('axo','interieur_entree','interieur_accueil','poste_accueil') and not e.get('is_v7') and \
           e['classe']=='IfcLightFixture' and e['nom'].startswith(LEGACY_CEILING_LIGHT_PREFIXES): omit=True
        # Keep the terrace ground for the threshold image, but remove unmeasured context in axo.
        if view=='axo' and e['tag']=='4350707': omit=True
        # Unmeasured 20 x 20 m exterior-ground proxy is context, not a proposed surface.
        if e['tag']=='4350705': omit=True
        # Reveal the terrace through the entry instead of looking through a close grille.
        if view=='terrasse' and ('porte grille rectangulaire entrée' in e['nom'].lower() or
                                  'trame droite baie' in e['nom'].lower()): omit=True
        if omit: excluded.append({'classe':e['classe'],'nom':e['nom'],'role':r})
        else: kept.append(e)
    T=[];C=[];I=[]
    for k,e in enumerate(kept):
        product_t=[];product_c=[];product_i=[]
        for fc,rgba in e['items']:
            product_t.append(e['verts'][fc]); product_c.append(rgba); product_i.append(np.full(len(fc),k,dtype=int))
        if not product_t: continue
        pt=np.concatenate(product_t);pc=np.concatenate(product_c);pi=np.concatenate(product_i)
        # On the cut axo, lower the south and east facade/wall geometry to +1.00 m;
        # all other geometry is cut at +2.40 m below.
        if view=='axo' and e['nom'] in CUT_WALL_NAMES:
            pt,pc,pi=clip_horizontal(pt,pc,pi,1.0)
        if view=='terrasse' and e['tag']=='4350707':
            pc=np.tile(np.array([[.79,.78,.74,1.0]]),(len(pt),1))
        T.append(pt);C.append(pc);I.append(pi)
    if not T: return np.zeros((0,3,3)),np.zeros((0,4)),np.zeros(0,dtype=int),excluded,kept
    tri=np.concatenate(T); col=np.concatenate(C); ids=np.concatenate(I)
    if view=='axo': tri,col,ids=clip_horizontal(tri,col,ids,2.4)
    return tri,col,ids,excluded,kept


def clip_horizontal(tri,col,ids,zmax):
    """Coupe les triangles par z<=zmax; conserve interpolation et couleur par face."""
    out_t=[];out_c=[];out_i=[]
    for t,c,i in zip(tri,col,ids):
        poly=[t[0],t[1],t[2]]; result=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            ina=a[2]<=zmax+1e-9; inb=b[2]<=zmax+1e-9
            if ina and inb: result.append(b)
            elif ina and not inb:
                u=(zmax-a[2])/(b[2]-a[2]);result.append(a+u*(b-a))
            elif not ina and inb:
                u=(zmax-a[2])/(b[2]-a[2]);result.append(a+u*(b-a));result.append(b)
        # Fully inside triangles return their vertices but shifted starting vertex only.
        if all(v[2]<=zmax+1e-9 for v in t): result=[t[0],t[1],t[2]]
        if len(result)>=3:
            for j in range(1,len(result)-1):
                out_t.append([result[0],result[j],result[j+1]]);out_c.append(c);out_i.append(i)
    if not out_t:return np.zeros((0,3,3)),np.zeros((0,4)),np.zeros(0,dtype=int)
    return np.asarray(out_t),np.asarray(out_c),np.asarray(out_i,dtype=int)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--only',choices=list(CAMERAS))
    ap.add_argument('--size',nargs=2,type=int,default=(2200,1467),metavar=('W','H'))
    ap.add_argument('--ss',type=int,default=1)
    args=ap.parse_args(); OUT.mkdir(parents=True,exist_ok=True)
    src_sha=hashlib.sha256(SRC.read_bytes()).hexdigest()
    scene=load_scene(SRC)
    names=list(CAMERAS) if not args.only else [args.only]
    for key in names:
        t0=time.time();cam=CAMERAS[key];T,C,I,excluded,kept=render_arrays(scene,key)
        if not len(T): raise RuntimeError(f"Aucun triangle pour {key}")
        light=AXO if key=='axo' else INT
        shaded,_traits=render(T,C,I,cam,size=tuple(args.size),ss=args.ss,**light)
        outpath=OUT/f'{key}.png';shaded.save(outpath,optimize=True)
        meta={'vue':key,'description':DESCRIPTIONS[key],'source_ifc':'v7/DECIMO_PROPOSITION_V7.ifc','source_sha256':src_sha,
              'reperage':'Coordonnées monde IFC en mètres, z vers le haut; caméra absolue.',
              'camera':camera_info(cam,tuple(args.size)),'rendu':{**light,'supersampling':args.ss},
              'coupe_horizontale_z_m':2.4 if key=='axo' else None,
              'masques':{'roles_exclus':sorted(BASE_HIDE),'plafonds':'exclus des vues intérieures pour dégager les pièces',
                         'legacy_tree_led':'supprimés dans l’IFC V7',
                         'luminaires_plafond':'anciens downlights masqués lorsque le faux plafond est masqué; intentions V7 montrées',
                         'axo_murs':'façade sud segmentée V7 et mur est coupés à +1,00 m; coupe générale à +2,40 m',
                         'options':'plateforme réserve haute et dallage optionnel d’extension masqués dans toutes les vues',
                         'techniques':'réservations techniques V5 masquées dans les rendus de présentation',
                         'axo_terrain':'proxys sol extérieur 4350705 et terrasse 4350707 masqués',
                         'terrasse_grille':'grille et trames droites masquées au seuil dans cette vue pour lire la continuité terrasse / intérieur',
                         'produits_exclus':excluded},
              'produits_visibles':len(kept),'triangles_rendus':int(len(T)),
              'objets_v7_classes':{e['nom']:e['classe'] for e in kept if e['is_v7']},
              'sortie_png':str(outpath.relative_to(ROOT)),'script':'v7/scripts/render_maquette.py'}
        (OUT/f'{key}_camera.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'{key}: {outpath} | {len(T):,} triangles | {time.time()-t0:.1f}s',flush=True)

if __name__=='__main__': main()
