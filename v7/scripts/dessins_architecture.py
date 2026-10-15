#!/usr/bin/env python3
"""Dessins architecturaux sans cartouche, générés depuis IFC V7 (repli temporaire IFC V6).

Les projections, le pochage, la végétation et le calcul d'ombres réutilisent les modules
de dessin V5. Les cotes et surfaces sont toujours liées au fichier IFC source indiqué en JSON.
"""
from __future__ import annotations
import hashlib, json, sys, os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/nandjui-matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/nandjui-cache")
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle, FancyArrowPatch
from PIL import Image
import ifcopenshell, ifcopenshell.geom

ROOT=Path(__file__).resolve().parents[2]
V5S=ROOT/"v5"/"scripts"
sys.path[:0]=[str(V5S),str(ROOT/"charte")]
from scene import charger, role as v5_role
import dessin2d as D
from dessins import peindre, pocher, echelle_graphique
from ombres import calculer_ombres
from charte_kdemi import ENCRE, TAUPE, TERRE_CUITE, IROKO, OLIVE

V7=ROOT/"v7"/"DECIMO_PROPOSITION_V7.ifc"
V6=ROOT/"v6"/"DECIMO_ESQ_V6_OPTION_C.ifc"
IFC=V7 if V7.exists() else V6
OUT=ROOT/"v7"/"assets"/"dessins"; OUT.mkdir(parents=True,exist_ok=True)
SHA=hashlib.sha256(IFC.read_bytes()).hexdigest()
SCENE=charger(str(IFC))
plt.rcParams.update({"font.family":"DejaVu Sans","hatch.linewidth":.45,"figure.facecolor":"white","axes.facecolor":"white"})
GLASS="#D9E8E8"; WOOD="#9C7354"; SAGE="#788675"; CHALK="#F4F1EA"; PROJECT="#B96043"; DIM="#756E66"; LIGHT="#CBC6BE"

def role(e):
    r=v5_role(e); n=e["nom"].lower()
    if "plateforme réserve" in n:return "hypothese"
    if "dallage extension terrasse" in n:return "option"
    return r

def bounds(e): return e["verts"].min(0),e["verts"].max(0)
def is_new(e): return not e.get("v4",False) or "V7" in e["nom"] or "option" in e["nom"].lower() or "hypothèse" in e["nom"].lower()
def draw_filter(e,limits,zmax=5):
    lo,hi=bounds(e)
    return hi[0]>=limits[0] and lo[0]<=limits[1] and hi[1]>=limits[2] and lo[1]<=limits[3] and hi[2]>=-1 and lo[2]<=zmax and role(e) not in ("logements","voisin","fenetre_logt")
def fig(w=12,h=12): return plt.figure(figsize=(w,h),dpi=200,facecolor="white")
def save(f,name):
    path=OUT/name
    f.savefig(path,dpi=200,transparent=True)
    plt.close(f)
    # Le plan et les autres livrables ont une largeur constante de 2400 px.
    im=Image.open(path)
    if im.width!=2400:
        h=round(im.height*2400/im.width); im=im.resize((2400,h),Image.Resampling.LANCZOS); im.save(path)
    print(path)
def soft_shadow(R,v,ax,mode):
    try:return calculer_ombres(R,v,ax.get_xlim(),ax.get_ylim(),mode,px_m=110)
    except Exception as e:
        print(f"Ombres indisponibles ({type(e).__name__}); dessin au trait conservé.",file=sys.stderr); return None
def title(ax,s,x,y,color=ENCRE,size=10):
    ax.text(x,y,s,ha="left",va="bottom",color=color,fontsize=size,weight="semibold",zorder=500,bbox={"facecolor":"white","edgecolor":"none","alpha":.88,"pad":2})
def dimh(ax,x1,x2,y,txt,ext=None,size=7):
    ax.plot([x1,x2],[y,y],color=DIM,lw=.6,zorder=400)
    for x in (x1,x2):
        ax.plot([x-.045,x+.045],[y-.045,y+.045],color=DIM,lw=.6,zorder=400)
        if ext is not None:ax.plot([x,x],[ext,y],color=DIM,lw=.45,zorder=399)
    ax.text((x1+x2)/2,y+.065,txt,ha="center",va="bottom",fontsize=size,color=DIM,bbox={"facecolor":"white","edgecolor":"none","pad":1},zorder=401)
def dimv(ax,y1,y2,x,txt,ext=None,size=7):
    ax.plot([x,x],[y1,y2],color=DIM,lw=.6,zorder=400)
    for y in (y1,y2):ax.plot([x-.045,x+.045],[y-.045,y+.045],color=DIM,lw=.6,zorder=400)
    if ext is not None:
        for y in (y1,y2):ax.plot([ext,x],[y,y],color=DIM,lw=.45,zorder=399)
    ax.text(x-.07,(y1+y2)/2,txt,rotation=90,ha="right",va="center",fontsize=size,color=DIM,bbox={"facecolor":"white","edgecolor":"none","pad":1},zorder=401)
def walk_arrow(ax,pts):
    ax.plot(*np.asarray(pts).T,color=OLIVE,lw=1.25,ls=(0,(3,2)),zorder=350)
    for a,b in zip(pts[:-1],pts[1:]):
        t=np.asarray(b)-a
        if np.linalg.norm(t):ax.add_patch(FancyArrowPatch(np.asarray(a)+.64*t,np.asarray(a)+.74*t,arrowstyle="-|>",mutation_scale=9,color=OLIVE,lw=.8,zorder=351))
def door_arcs(ax,e):
    lo,hi=bounds(e); dx,dy=hi[:2]-lo[:2]
    if "entrée" in e["nom"].lower():
        widths=[min(.9,dx*.62),max(.35,dx-min(.9,dx*.62))]; x=lo[0]
        for w in widths:
            ax.add_patch(Arc((x,lo[1]+.05),2*w,2*w,theta1=0,theta2=90,ec=TAUPE,lw=.75,ls=(0,(2,1)),zorder=180))
            ax.plot([x,x],[lo[1]+.05,lo[1]+.05+w],color=TAUPE,lw=.65,zorder=181); x+=w
    elif "porte vitrée" in e["nom"].lower():
        # Pivot sur jambage sud; ouverture dessinée côté salle 03 comme convention de plan.
        w=dy
        ax.add_patch(Arc((lo[0],lo[1]),2*w,2*w,theta1=90,theta2=180,ec=TAUPE,lw=.75,ls=(0,(2,1)),zorder=180))
        ax.plot([lo[0],lo[0]-w],[lo[1],lo[1]],color=TAUPE,lw=.65,zorder=181)
    elif "wc" in e["nom"].lower():
        w=min(dx,dy); ax.add_patch(Arc((lo[0],lo[1]),2*w,2*w,theta1=0,theta2=90,ec=TAUPE,lw=.65,ls=(0,(2,1)),zorder=180))
def floor_color(ax,limits):
    v=D.Vue((0,0,-1),(1,0,0),(0,1,0))
    for e in SCENE:
        if e["classe"]!="IfcCovering" or not any(s in e["nom"].lower() for s in ("revêtement de sol","dallage extension")):continue
        lo,hi=bounds(e)
        if hi[0]<limits[0] or lo[0]>limits[1] or hi[1]<limits[2] or lo[1]>limits[3]:continue
        T=np.concatenate([e["verts"][fc] for fc,_ in e["items"]]); g=D.silhouette(v.to2d(T))
        if g is not None:D.patch(ax,g,fc=CHALK if "réunion" in e["nom"].lower() else ("#E9E0D4" if "lecture" in e["nom"].lower() else "#E8E2D9"),ec="none",z=1,alpha=.65)

def plan_amenagement():
    lim=(-.6,7.2,-4.0,8.0); f=fig(12,18.45); ax=f.add_axes([.04,.025,.92,.95])
    ax.set_xlim(lim[:2]);ax.set_ylim(lim[2:]);ax.set_aspect("equal",adjustable="box");ax.axis("off");ax.ech=46
    floor_color(ax,lim)
    v=D.Vue((0,0,-1),(1,0,0),(0,1,0),coupe=((0,0,1),1.0003))
    R=D.calculer(SCENE,v,lambda e,r:draw_filter(e,lim,4))
    peindre(ax,R,ombre=soft_shadow(R,v,ax,"plan"),veg="plan");pocher(ax,R)
    for e in SCENE:
        if e["classe"]=="IfcDoor" and draw_filter(e,lim,3):door_arcs(ax,e)
    walk_arrow(ax,[(4.05,-.1),(4.05,.55),(3.8,1.4),(3.25,2.1),(3.25,3.4)])
    title(ax,"PLAN D’AMÉNAGEMENT · IFC V7",-.45,7.68,size=11)
    title(ax,"Parcours public",4.55,.18,color=OLIVE,size=7)
    dimh(ax,-.09,6.69,7.08,"6,78 m · emprise IFC",7.41)
    dimv(ax,-.09,7.59,-.42,"7,68 m · emprise IFC",-.09)
    ax.text(.34,4.62,"SALLE VITRÉE",fontsize=7,color=PROJECT,rotation=90,ha="center",va="center",zorder=250,
            bbox={"facecolor":"white","edgecolor":"none","alpha":.72,"pad":1})
    ax.text(4.85,5.95,"BIBLIOTHÈQUE",fontsize=7,color=WOOD,ha="center",zorder=250)
    # Barre d'échelle numérotée et adaptée au plan rapproché.
    y=7.68; x0=4.45
    for i in range(2):
        ax.add_patch(Rectangle((x0+i,y),1,.055,fc=ENCRE if i==0 else "white",ec=ENCRE,lw=.55,zorder=450))
    for i,s in enumerate(("0","1","2 m")):
        ax.text(x0+i,y-.08,s,fontsize=7,color=DIM,ha="center",va="top",zorder=451,
                bbox={"facecolor":"white","edgecolor":"none","alpha":.88,"pad":.5})
    save(f,"plan_amenagement.png")

def furniture_background(ax,view,far,crop):
    for e in SCENE:
        if role(e) not in ("mobilier","autre","vitrage") or not draw_filter(e,(-.5,7.1,-.25,7.8),3.4):continue
        lo,hi=bounds(e)
        if not far(e,lo,hi):continue
        T=np.concatenate([e["verts"][fc] for fc,_ in e["items"]]);g=D.silhouette(view.to2d(T))
        if g is not None:D.patch(ax,g,fc="none",ec=LIGHT,lw=.65,z=3,alpha=.8)

def section_draw(name,axis,at,limits,h=6.4):
    f=fig(12,h);ax=f.add_axes([.04,.07,.92,.86]);ax.set_xlim(limits[:2]);ax.set_ylim(limits[2:]);ax.set_aspect("equal",adjustable="box");ax.axis("off");ax.ech=25
    if axis=="x":
        v=D.Vue((1,0,0),(0,1,0),(0,0,1),coupe=((-1,0,0),-at+.0003));crop=(-.25,7.6,-.2,3.75)
        keep=lambda e,r:draw_filter(e,(-.5,7.1,-.25,7.8),3.6);far=lambda e,l,hi:l[0]>at+.01
        cap=f"COUPE LONGITUDINALE · x = {at:.2f} m · {IFC.stem}"
    else:
        # Regarder depuis le sud vers le nord évite de masquer la coupe par la façade avant.
        v=D.Vue((0,1,0),(1,0,0),(0,0,1),coupe=((0,-1,0),-at+.0003));crop=(-.25,7,-.2,3.75)
        keep=lambda e,r:draw_filter(e,(-.5,7.1,-.25,7.8),3.6);far=lambda e,l,hi:hi[1]<at-.01
        cap=f"COUPE TRANSVERSALE · y = {at:.2f} m · {IFC.stem}"
    # La demi-maquette gardée est placée derrière le plan de coupe et
    # regardée dans sa profondeur; aucun mur de fond ne masque les meubles.
    base_keep=keep
    keep=lambda e,r: base_keep(e,r) and role(e)!="technique" and (role(e)!="hypothese" or name=="coupe_transversale.png") and (e["classe"]!="IfcLightFixture" or e["nom"].startswith("V7"))
    R=D.calculer(SCENE,v,keep)
    peindre(ax,R,mode="elev",ombre=soft_shadow(R,v,ax,"int"),veg="elev")
    # Poché précis des maçonneries; les dalles sont différenciées par une trame minérale claire.
    pocher(ax,[r for r in R if r["e"]["classe"]!="IfcSlab"])
    for r in R:
        if r["e"]["classe"]=="IfcSlab" and r["coupe"] is not None:
            D.patch(ax,r["coupe"],fc="#D8D2C9",ec=ENCRE,lw=D.LW[2],z=64,hatch="////")
    # Les pieds de table sont des composants derrière le plan de coupe :
    # les représenter individuellement évite la perte de profondeur d'un groupe IFC.
    for e in SCENE:
        if "table de réunion" not in e["nom"].lower(): continue
        for fc,_ in e["items"]:
            vv=e["verts"][fc].reshape(-1,3);lo=vv.min(0);hi=vv.max(0)
            if lo[2]<.01 and hi[2]<.76 and max(hi[0]-lo[0],hi[1]-lo[1])<.13:
                kept=(hi[0]>=at if axis=="x" else hi[1]>=at)
                if kept:
                    uu=1 if axis=="x" else 0
                    ax.add_patch(Rectangle((lo[uu],0),hi[uu]-lo[uu],hi[2],fc="#B8977B",ec=ENCRE,lw=.6,zorder=85))
    # Livres en élévation conventionnelle, sur les tablettes du fond uniquement.
    # Le poteau coupé et les rayonnages latéraux restent prioritaires visuellement.
    if name=="coupe_usage.png":
        rng=np.random.default_rng(27)
        for z in (.06,.53,1.01,1.49):
            x=3.47
            while x<5.52:
                bw=float(rng.uniform(.035,.075));bh=float(rng.uniform(.20,.30))
                ax.add_patch(Rectangle((x,z),bw,bh,fc=[WOOD,SAGE,PROJECT,"#D2C6B3"][int(rng.integers(0,4))],ec=TAUPE,lw=.23,zorder=80))
                x+=bw+.015
        ax.text(4.4,2.26,"Rayonnages du fond · livres figurés",fontsize=6,color=DIM,ha="center",zorder=350)
    ax.plot(limits[:2],[0,0],color=ENCRE,lw=1.2,zorder=200);ax.axhline(3.3,color=LIGHT,lw=.55,ls=(0,(5,3)),zorder=2)
    title(ax,cap,limits[0]+.16,limits[3]-.2,size=10)
    ax.text(limits[0]+.12,.06,"±0,00 · niveau IFC à relever",fontsize=7,color=DIM,va="bottom",zorder=350,bbox={"facecolor":"white","edgecolor":"none","alpha":.85,"pad":1})
    ax.text(limits[0]+.12,3.32,"+3,30 · sous-face dalle IFC, hypothèse à confirmer",fontsize=7,color=DIM,va="bottom",zorder=350,bbox={"facecolor":"white","edgecolor":"none","alpha":.85,"pad":1})
    dimv(ax,0,3.3,limits[1]-.12,"3,30 m · hauteur de modèle",limits[1]-.4)
    bx=limits[0]+.25; by=limits[2]+.13
    for i in range(4):
        ax.add_patch(Rectangle((bx+i,by),1,.035,fc=ENCRE if i%2==0 else "white",ec=ENCRE,lw=.4,zorder=450))
    for i in (0,2,4):
        ax.text(bx+i,by+.065,f"{i}"+(" m" if i==4 else ""),fontsize=6,color=DIM,ha="center",zorder=451)
    if name=="coupe_transversale.png":
        p=next((e for e in SCENE if "plateforme réserve" in e["nom"].lower()),None)
        if p:
            lo,hi=bounds(p)
            if axis=="y" and lo[1]<=at<=hi[1]:
                ax.add_patch(Rectangle((lo[0],lo[2]),hi[0]-lo[0],hi[2]-lo[2],fc="none",ec=PROJECT,lw=1.4,ls=(0,(4,2)),zorder=220))
                ax.annotate("RÉSERVE HAUTE · HYPOTHÈSE IFC",xy=((lo[0]+hi[0])/2,hi[2]),xytext=(lo[0]+.15,hi[2]+.34),fontsize=7.5,color=PROJECT,arrowprops={"arrowstyle":"->","color":PROJECT,"lw":.8},bbox={"facecolor":"white","edgecolor":"none","alpha":.92,"pad":2},zorder=300)
    save(f,name)

def elevations_rangements():
    f=fig(12,7.5)
    panels=[
      {"rect":[.05,.14,.43,.76],"view":D.Vue((1,0,0),(0,-1,0),(0,0,1)),"lim":(-6.95,-3.75,-.12,2.55),"filter":lambda e:("rayonnage droit est" in e["nom"].lower() or e["tag"]=="4350588"),"title":"ÉLÉVATION EST · RAYONNAGE DROIT","shelf":(-6.67,-4.33),"axis":"east"},
      {"rect":[.53,.14,.42,.76],"view":D.Vue((0,1,0),(1,0,0),(0,0,1)),"lim":(2.65,6.55,-.12,2.55),"filter":lambda e:("rayonnage droit nord" in e["nom"].lower() or e["tag"]=="4350589"),"title":"ÉLÉVATION NORD · RAYONNAGE DROIT","shelf":(3.26,6.10),"axis":"north"}]
    for p in panels:
        ax=f.add_axes(p["rect"]);ax.set_xlim(p["lim"][:2]);ax.set_ylim(p["lim"][2:]);ax.set_aspect("equal",adjustable="box");ax.axis("off");ax.ech=30
        R=D.calculer(SCENE,p["view"],lambda e,r:p["filter"](e) and draw_filter(e,(-.5,7.1,-.5,7.8),3.5))
        peindre(ax,R,veg="elev");pocher(ax,R);ax.plot(p["lim"][:2],[0,0],color=ENCRE,lw=1,zorder=200)
        title(ax,p["title"],p["lim"][0]+.08,2.35,size=9)
        # Livres de convention graphique; les tablettes et leur enveloppe suivent la géométrie IFC.
        x0,x1=p["shelf"];rng=np.random.default_rng(42 if p["axis"]=="north" else 61)
        for z in (.055,.535,1.015,1.495):
            x=x0+.10
            while x<x1-.16:
                w=float(rng.uniform(.075,.16));bh=float(rng.uniform(.22,.33));col=[WOOD,SAGE,PROJECT,"#D9D0C2"][int(rng.integers(0,4))]
                ax.add_patch(Rectangle((x,z),min(w,x1-.04-x),bh,fc=col,ec=ENCRE,lw=.28,zorder=210,alpha=.82));x+=w+.025
        dimh(ax,x0,x1,.02,f"{x1-x0:.2f} m · largeur IFC",.06,size=6.2)
        dimv(ax,0,2.05,p["lim"][0]+.2,"2,05 m · hauteur IFC",p["lim"][0]+.45,size=6.2)
        echelle_graphique(ax,p["lim"][0]+.3,p["lim"][2]+.1,2,1)
    f.text(.05,.055,"Livres dessinés conventionnellement; tablettes, enveloppes et hauteurs proviennent de l’IFC. Cotes à contrôler sur site.",fontsize=7,color=DIM)
    save(f,"elevation_rangements.png")

def surfaces_ifc():
    f=ifcopenshell.open(str(IFC));s=ifcopenshell.geom.settings();s.set("use-world-coords",True);spaces=[]
    for sp in f.by_type("IfcSpace"):
        if not sp.Representation:continue
        try:
            g=ifcopenshell.geom.create_shape(s,sp).geometry;v=np.asarray(g.verts).reshape(-1,3);fc=np.asarray(g.faces).reshape(-1,3);poly=D.silhouette(v[fc][:,:,:2]);lo=v.min(0);hi=v.max(0)
            spaces.append({"nom":sp.Name,"libelle_ifc":getattr(sp,"LongName",None),"statut":"désignation de modèle IFC, à vérifier sur site","surface_m2":round(float(poly.area),3) if poly is not None else None,
                           "emprise_m":{"x":round(float(lo[0]),3),"y":round(float(lo[1]),3),"largeur":round(float(hi[0]-lo[0]),3),"longueur":round(float(hi[1]-lo[1]),3)},"hauteur_modele_m":round(float(hi[2]-lo[2]),3)})
        except Exception as e:spaces.append({"nom":sp.Name,"surface_m2":None,"erreur":str(e)})
    objs=[]
    for e in SCENE:
        if not any(k in e["nom"].lower() for k in ("comptoir","rayonnage","plateforme","dallage","vitrage","cloison")):continue
        lo,hi=bounds(e)
        if not (is_new(e) or "V7" in e["nom"]):continue
        objs.append({"nom":e["nom"],"classe":e["classe"],"source":"IFC","hypothese":role(e)=="hypothese","option":role(e)=="option","dimensions_m":{"x":round(float(hi[0]-lo[0]),3),"y":round(float(hi[1]-lo[1]),3),"z":round(float(hi[2]-lo[2]),3)},"origine_m":[round(float(x),3) for x in lo]})
    walls=[e for e in SCENE if e["classe"].startswith("IfcWall")]
    if walls:
        los=[bounds(e)[0] for e in walls];his=[bounds(e)[1] for e in walls]
        ext={"xmin":round(float(min(x[0] for x in los)),3),"xmax":round(float(max(x[0] for x in his)),3),
             "ymin":round(float(min(x[1] for x in los)),3),"ymax":round(float(max(x[1] for x in his)),3)}
        ext["largeur_m"]=round(ext["xmax"]-ext["xmin"],3);ext["longueur_m"]=round(ext["ymax"]-ext["ymin"],3)
    else:ext=None
    total=sum(x["surface_m2"] or 0 for x in spaces if "terrasse" not in str(x.get("libelle_ifc","")).lower())
    data={"source_ifc":str(IFC.relative_to(ROOT)),"sha256":SHA,
          "note":"Surfaces et dimensions calculées depuis les géométries IFC; ne constituent pas un relevé de chantier. Les libellés hérités de la V5 décrivent une maquette de projet, pas un état photographié ou relevé.",
          "dimensions_visibles":{"enveloppe_murs_m":ext,"coupe_longitudinale_x_m":1.70,"coupe_transversale_y_m":4.35,"coupe_usage_y_m":3.75,"niveau_rdc_modele_m":0.0,"sous_face_dalle_modele_m":3.30},
          "surfaces_interieures_modele_m2":round(total,3),"espaces":spaces,"objets_selectionnes":objs}
    (OUT/"dimensions_surfaces.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    print(f"Source IFC : {IFC} · sha256 {SHA[:12]}")
    plan_amenagement()
    section_draw("coupe_longitudinale.png","x",1.70,(-.5,7.25,-.38,3.72))
    section_draw("coupe_transversale.png","y",4.35,(-.5,7.1,-.38,3.72))
    section_draw("coupe_usage.png","y",3.75,(-.5,7.1,-.38,3.72))
    elevations_rangements()
    surfaces_ifc()

if __name__=="__main__":main()
