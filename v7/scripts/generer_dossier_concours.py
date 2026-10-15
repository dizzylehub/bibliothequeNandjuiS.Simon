#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dossier de concours V7 : export PDF A3, PPTX éditable, PNG et galerie HTML."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from pptx import Presentation
from pptx.util import Mm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.enum.dml import MSO_LINE_DASH_STYLE
import html, json, math, re, shutil, subprocess, sys, hashlib

ROOT = Path(__file__).resolve().parents[2]
V7 = ROOT / "v7"
ASSET = V7 / "assets"
DRAW = ASSET / "dessins"
IFC_ASSET = ASSET / "ifc"
AMBI = ASSET / "ambiance"
OUT = V7
PREVIEW = V7 / "apercus_concours"
TMP = Path("/tmp/decimo_v7_build")
W, H = 420.0, 297.0
INK = "292826"; MUTED = "79746D"; LINE = "D8D2C9"; PAPER = "F8F6F2"
TERRA = "BD5B3B"; TERRALIGHT = "F2E2D9"; WOOD = "9A704D"; WOODLIGHT = "D5B99A"
SAND = "E8DED1"; GREEN = "66735B"; GREENLIGHT = "E4E9DF"; DARK = "272B29"; BLUE = "CBDDE0"
FONT_REG = ROOT / "charte/polices/archivo-latin-400-normal.ttf"
FONT_MED = ROOT / "charte/polices/archivo-latin-500-normal.ttf"
FONT_BOLD = ROOT / "charte/polices/archivo-latin-600-normal.ttf"
LOGO = ROOT / "charte/logo_v3/KDemi_v3_A_arche_lockup.png"
IFC_MODEL = V7 / "DECIMO_PROPOSITION_V7.ifc"
REQUIRED_VIEWS = [IFC_ASSET/n for n in ("axo.png","interieur_entree.png","interieur_accueil.png","terrasse.png")]
REQUIRED_DRAWINGS = [DRAW/n for n in ("plan_amenagement.png","coupe_longitudinale.png","coupe_transversale.png","coupe_usage.png","elevation_rangements.png")]
def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

MODEL_SHA = sha256(IFC_MODEL) if IFC_MODEL.exists() else ""
def metadata_matches(path, meta_path):
    try:
        meta=json.loads(meta_path.read_text(encoding="utf-8"))
        png=IFC_ASSET/(path.stem+".png")
        return (meta.get("source_sha256")==MODEL_SHA and Path(meta.get("source_ifc","")).name==IFC_MODEL.name
                and png.exists())
    except Exception: return False

# Les métadonnées de provenance priment sur les dates : des exports V6 peuvent
# être plus récents sur disque tout en restant issus de la mauvaise maquette.
IFC_VIEW_META = {p: IFC_ASSET/(p.stem+"_camera.json") for p in REQUIRED_VIEWS}
IFC_VIEWS_READY = bool(MODEL_SHA) and all(p.exists() and metadata_matches(p,IFC_VIEW_META[p]) for p in REQUIRED_VIEWS)
try:
    drawing_meta=json.loads((DRAW/"dimensions_surfaces.json").read_text(encoding="utf-8"))
    DRAWINGS_READY = bool(MODEL_SHA) and drawing_meta.get("sha256")==MODEL_SHA and all(p.exists() for p in REQUIRED_DRAWINGS)
except Exception: DRAWINGS_READY=False
IFC_READY = IFC_VIEWS_READY and DRAWINGS_READY
PLAN_DETAIL_ACCUEIL = TMP/"plan_accueil_detail.png"
PLAN_IFC_PRESENTATION = TMP/"plan_v7_interieur.png"
if DRAWINGS_READY:
    # Détail de l’accueil, du comptoir et du passage public extrait du plan coté V7.
    plan=Image.open(DRAW/"plan_amenagement.png").convert("RGB")
    pw,ph=plan.size
    crop=(round(pw*.104),round(ph*.474),round(pw*.542),round(ph*.732))
    TMP.mkdir(parents=True,exist_ok=True)
    plan.crop(crop).save(PLAN_DETAIL_ACCUEIL)
    # Planche principale : intérieur et seuil agrandis, sans la grande marge de terrasse.
    plan=Image.open(DRAW/"plan_amenagement.png").convert("RGB")
    pw,ph=plan.size
    plan.crop((round(pw*.042),round(ph*.041),round(pw*.958),round(ph*.680))).save(PLAN_IFC_PRESENTATION)

for name, path in [("Archivo", FONT_REG), ("ArchivoMed", FONT_MED), ("ArchivoBold", FONT_BOLD)]:
    if path.exists(): pdfmetrics.registerFont(TTFont(name, str(path)))

pages = []

def add(kind, **kw):
    pages[-1]["els"].append({"kind":kind, **kw})

def new_page(code, title, deck=None, kicker=None, bg="FFFFFF"):
    pages.append({"code":code,"title":title,"deck":deck or "","kicker":kicker or "","els":[],"bg":bg})
    add("rect",x=0,y=0,w=W,h=H,fill=bg)
    add("text",x=15,y=10,w=130,h=5,text="K&DÉMI   /   BIBLIOTHÈQUE NANDJUI D. SIMON",size=8,color=INK,font="ArchivoBold",tracking=0.2)
    if kicker: add("text",x=15,y=22,w=200,h=5,text=kicker.upper(),size=8,color=TERRA,font="ArchivoBold")
    add("text",x=15,y=29,w=385,h=14,text=title,size=25,color=INK,font="ArchivoBold")
    if deck: add("text",x=15,y=45,w=385,h=8,text=deck,size=11,color=MUTED,font="Archivo")
    add("line",x=15,y=57,x2=405,y2=57,color=LINE,width=0.35)
    add("line",x=15,y=284,x2=405,y2=284,color=LINE,width=0.35)
    add("text",x=15,y=287,w=360,h=5,text="PROPOSITION V7  ·  DOSSIER DE CONCOURS  ·  ÉTUDE DE CONCEPTION",size=7,color=MUTED,font="Archivo")
    add("text",x=384,y=287,w=21,h=5,text=code,size=7,color=TERRA,font="ArchivoBold",align="right")

def txt(x,y,w,h,text,size=11,color=INK,bold=False,font=None,align="left",italic=False):
    add("text",x=x,y=y,w=w,h=h,text=text,size=size,color=color,font=font or ("ArchivoBold" if bold else "Archivo"),align=align,italic=italic)

def rect(x,y,w,h,fill,stroke=None,sw=.4,radius=0):
    add("rect",x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,width=sw,radius=radius)

def line(x,y,x2,y2,color=LINE,width=.5,dash=False):
    add("line",x=x,y=y,x2=x2,y2=y2,color=color,width=width,dash=dash)

def image(path,x,y,w,h,label=None,mode="cover"):
    p = Path(path) if path else None
    if p and not p.is_absolute(): p = ROOT / p
    if p and p.exists():
        add("image",path=str(p),x=x,y=y,w=w,h=h,mode=mode,label=label)
    else:
        rect(x,y,w,h,"F0EEE9",TERRA,.5)
        add("text",x=x+5,y=y+h*.42,w=w-10,h=12,text="VISUEL EN COURS DE PRODUCTION",size=10,color=TERRA,font="ArchivoBold",align="center")
        add("text",x=x+5,y=y+h*.52,w=w-10,h=14,text=label or (p.name if p else "asset attendu"),size=8,color=MUTED,font="Archivo",align="center")
    if label:
        add("text",x=x,y=y+h+1.3,w=w,h=5,text=label,size=7.2,color=MUTED,font="Archivo")

def label_card(x,y,w,title,body,num=None,accent=TERRA):
    line(x,y,x+w,y,color=accent,width=1.5)
    if num: txt(x,y+3,12,6,num,8,accent,bold=True)
    tx=x+(15 if num else 0)
    txt(tx,y+3,w-(tx-x),7,title,12,INK,bold=True)
    txt(x,y+12,w,25,body,9.5,MUTED)

def swatch(x,y,c,name,detail):
    rect(x,y,17,17,c,LINE,.35)
    txt(x+20,y+1,58,5,name,9,INK,bold=True)
    txt(x+20,y+7,58,9,detail,7.5,MUTED)

def photo(pathname): return ROOT / pathname

SITE_TREE = photo("photos/LE SITE/WhatsApp Image 2026-10-13 at 5.50.23 PM (5).jpeg")
SITE_GATE = photo("photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (2).jpeg")
BLUE_ROOM = photo("photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (18).jpeg")
BLUE_DOOR = photo("photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (23).jpeg")
EMPTY_ROOM = photo("photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (10).jpeg")
SITE_DALLAGE = photo("photos/LE SITE/WhatsApp Image 2026-10-13 at 5.50.22 PM.jpeg")
SITE_LAWN = photo("photos/LE SITE/WhatsApp Image 2026-10-13 at 5.50.23 PM (1).jpeg")
HERO_MONTAGE = AMBI/"seuil_projet.png"

# 01 — couverture : photo de l'existant, proposition clairement distinguée.
new_page("01","Bibliothèque Nandjui D. Simon","Une bibliothèque habitée · Du livre à la rencontre · Deux Plateaux, Abidjan","Proposition de concours")
hero_ready=HERO_MONTAGE.exists()
image(HERO_MONTAGE if hero_ready else SITE_TREE,15,63,246,208,
      "PHOTOMONTAGE IA · intention de façade sur photo du site" if hero_ready else "PHOTO DU SITE · arbre, chemin et abord existants")
if LOGO.exists(): image(LOGO,280,68,80,26,"Identité K&Démi",mode="contain")
txt(280,107,122,7,"DEUX PLATEAUX · ABIDJAN",9,TERRA,bold=True)
txt(280,121,124,42,"Lire le jour.\nSe retrouver le soir.",25,INK,bold=True)
txt(280,169,116,32,"Une adresse de quartier ouverte sur ses usages : lire, travailler, prendre un café, se réunir et prolonger la journée sous l’arbre.",12,INK)
line(280,218,399,218,TERRA,1.4)
txt(280,225,110,7,"DOSSIER DE CONCOURS · V7",9,INK,bold=True)
txt(280,236,110,16,"Projet architectural et intérieur\nPDF de présentation · A3 paysage",9,MUTED)
# La photographie est déjà légendée sous son cadre.
if hero_ready:
    txt(15,278,247,5,"Photomontage d’intention sur photo du site; finitions et usages proposés, non exact IFC.",6.7,MUTED)

# 02 — parti éditorial et expérience.
new_page("02","Du seuil à la rencontre","Un parcours simple transforme un local profond en lieu de quartier.","Le parti")
txt(15,68,156,36,"La bibliothèque se découvre en avançant : un accueil visible dès l’entrée, une salle vitrée qui emprunte la lumière, des livres à portée de main, puis l’ombre de la terrasse.",16,INK,bold=True)
image(SITE_GATE,185,68,108,78,"EXISTANT · grille et entrée photographiées")
image(BLUE_ROOM,298,68,107,78,"EXISTANT · pièce bleue à requalifier")
blocks=[("01","ARRIVER","Voir le comptoir depuis le seuil. Garder la grille et le passage lisibles."),("02","ÊTRE ACCUEILLI","Un poste unique, assis, tourné vers les livres et attentif à la salle vitrée."),("03","CHOISIR","À gauche, se réunir. À droite, lire, consulter ou travailler."),("04","PROLONGER","Retrouver l’arbre, l’air du soir et la terrasse sous réserve des limites réelles.")]
for i,(n,h,b) in enumerate(blocks):
    x=15+i*98
    txt(x,164,18,14,n,24,TERRA,bold=True)
    line(x,184,x+82,184,LINE,.5)
    txt(x,189,83,7,h,10,INK,bold=True)
    txt(x,200,83,25,b,9.5,MUTED)
rect(15,247,390,25,PAPER,LINE,.4)
txt(21,252,378,6,"LE GESTE ARCHITECTURAL",8,TERRA,bold=True)
txt(21,260,378,8,"Libérer le centre; faire travailler les murs avec des rayonnages droits, une trame vitrée calme et un mobilier en modules réparables.",10,INK)

# 03 — photographie et lecture de site.
new_page("03","Le lieu donne déjà la direction","L’ombre, la grille et la profondeur sont les premières données du projet.","01 · Lire le site")
image(SITE_TREE,15,65,238,126,"PHOTO · grand arbre et espace extérieur, position à relever")
image(SITE_GATE,258,65,147,94,"PHOTO · grille de sécurité et seuil")
image(BLUE_DOOR,258,164,71,75,"PHOTO · accès arrière et marches visibles")
image(SITE_DALLAGE,334,164,71,75,"PHOTO · dallage extérieur irrégulier")
label_card(15,201,71,"L’OMBRE","L’arbre existant rafraîchit l’abord; sa position exacte reste à relever.","01",GREEN)
label_card(98,201,71,"LE SEUIL","La grille et l’entrée rectangulaire doivent rester compréhensibles.","02")
label_card(181,201,72,"LA PROFONDEUR","Les vues montrent un fond peu éclairé; la lumière doit traverser.","03",WOOD)
txt(258,249,147,20,"Les photos sont des documents de l’existant. Elles ne donnent ni cotes fiables, ni limites foncières, ni capacité structurelle.",9,MUTED)

# 04 — concept spatial diagram, not a dimensioned plan.
new_page("04","Une ligne claire, quatre séquences","Schéma d’usage non coté · plan-programme accepté, géométrie à confirmer au relevé.","02 · Organiser")
rect(28,70,204,178,"F5F2ED",INK,1)
rect(38,78,184,36,"E8DED1",LINE,.5)
txt(45,89,160,7,"FOND · WC EXISTANT + ÉCRAN / RÉSERVE À VÉRIFIER",10,INK,bold=True,align="center")
rect(38,119,77,58,"DCE8E8",TERRA,.7)
txt(46,132,60,8,"SALLE VITRÉE",13,INK,bold=True,align="center")
txt(46,145,60,16,"Réunion · six places visées\nà vérifier au relevé",9,MUTED,align="center")
rect(119,119,103,80,"F0EEE9",LINE,.5)
txt(128,135,85,7,"BIBLIOTHÈQUE",13,INK,bold=True,align="center")
txt(130,149,81,17,"Rayonnages périphériques\nlecture · coworking",10,MUTED,align="center")
rect(38,182,77,42,"F2E2D9",TERRA,.7)
txt(45,193,64,7,"ACCUEIL + CAFÉ",11,INK,bold=True,align="center")
txt(45,204,64,7,"poste unique",9,MUTED,align="center")
rect(28,226,204,22,"E4E9DF",GREEN,.5)
txt(35,233,189,7,"TERRASSE COUVERTE  →  ARBRE / DALLAGE À CONFIRMER",9,GREEN,bold=True,align="center")
line(77,222,77,209,TERRA,1.6); line(77,209,77,188,TERRA,1.6); line(77,188,77,177,TERRA,1.6)
line(115,153,119,153,TERRA,1.2,dash=True)
txt(254,72,147,8,"LE PARCOURS",10,TERRA,bold=True)
txt(254,84,145,23,"Entrée et accueil au premier plan. La pièce bleue devient salle vitrée à gauche. Les livres et le travail occupent la grande salle à droite.",11,INK)
txt(254,123,147,7,"CE QUE LE PLAN GARDE",10,TERRA,bold=True)
txt(254,135,145,24,"WC au fond; circulation directe; terrasse couverte existante. L’extension extérieure reste une option tant que ses limites ne sont pas établies.",10,INK)
txt(254,182,147,7,"À NE PAS CONFONDRE",10,TERRA,bold=True)
txt(254,194,145,26,"Ce diagramme décrit le programme, pas les murs mesurés ni une implantation d’exécution. Les surfaces V5 restent des valeurs de maquette.",9.5,MUTED)

# 05 — narrative day-to-evening.
new_page("05","Une journée, trois ambiances","Le projet accompagne les rythmes du quartier sans changer de langage.","03 · Habiter le lieu")
image(AMBI/"interieur_jour.png",15,68,124,102,"AMBIANCE IA · lire et travailler le jour")
image(IFC_ASSET/"interieur_entree.png" if IFC_VIEWS_READY else None,147,68,124,102,"MAQUETTE IFC V7 · géométrie de référence")
image(AMBI/"interieur_soir.png",279,68,126,102,"AMBIANCE IA · se retrouver le soir")
label_card(15,187,122,"MATIN · LIRE","Le jour entre par l’accueil et se prolonge vers les livres.","01",GREEN)
label_card(147,187,122,"JOUR · TRAVAILLER","La salle vitrée accueille les réunions; le reste de la salle demeure traversant.","02",TERRA)
label_card(279,187,126,"SOIR · SE RETROUVER","Les usages s’étendent vers la terrasse couverte et l’ombre existante.","03",WOOD)
txt(15,245,390,20,"Les ambiances IA ajoutent livres, personnes, végétal et finitions; la vue IFC au centre montre la géométrie de la maquette. Les légendes distinguent ces statuts.",9,MUTED)

# 06 — palette tactile.
new_page("06","Des matières familières, peu d’effets","Une palette construisible et réparable; échantillons à valider avec les entreprises locales.","04 · Matière")
mat=AMBI/"../matieres.png"
image(mat,15,67,235,180,"IMAGE IA D’INTENTION · matières à sourcer localement",mode="contain")
swatch(266,72,"EDE7DD","Enduit clair","Réparer puis peindre, finition mate lavable.")
swatch(266,105,"9A704D","Bois naturel","Menuiserie modulaire; essence et filière à confirmer.")
swatch(266,138,"BD5B3B","Terre cuite","Accent ponctuel; carreau ou panneau local à tester.")
swatch(266,171,"292B29","Métal sombre","Profilés vitrés et petites pièces, finition résistante.")
swatch(266,204,"CBDDE0","Verre clair","Salle vitrée; type et sécurité selon fabricant.")
txt(266,246,130,18,"Le sol existant sera diagnostiqué avant décision de conservation ou remplacement.",9,MUTED)

# 07 — plan principal from final V7 only; never substitute V5/V6 plan.
new_page("07","Un plan pour accueillir et lire","Plan de projet issu de l’IFC V7 · cotes et surfaces à rapprocher du relevé.","05 · Plan architectural")
image(PLAN_IFC_PRESENTATION if DRAWINGS_READY else None,15,64,266,207,"A01 · plan IFC V7 · intérieur et seuil" if DRAWINGS_READY else "Plan d’aménagement V7 attendu de l’équipe BIM — aucun plan V5/V6 substitué",mode="contain")
txt(297,67,105,7,"PROGRAMME",10,TERRA,bold=True)
items=[("01","Accueil-café · un seul poste"),("02","Salle vitrée · pièce bleue"),("03","Bibliothèque + coworking"),("04","WC au fond + écran"),("05","Terrasse couverte conservée")]
for i,(n,t) in enumerate(items):
    y=82+i*22
    txt(297,y,18,9,n,15,TERRA,bold=True); txt(317,y+1,85,12,t,10,INK)
line(297,198,404,198,TERRA,1)
txt(297,204,107,7,"LÉGENDE DE PROJET",9,TERRA,bold=True)
for i,(c,t) in enumerate([(INK,"Existant conservé"),(TERRA,"Création V7"),(MUTED,"À vérifier / option")]):
    y=217+i*10; rect(298,y,8,4,c); txt(311,y-1,90,6,t,8.5,INK)
txt(297,254,106,20,"Poteau existant conservé; cloison vitrée et dégagements dessinés depuis la maquette V7.",8.5,MUTED)

# 08 — axonometric.
new_page("08","Un même lieu, des usages qui se lisent","Axonométrie générale issue de la maquette V7 · existant et projet différenciés.","06 · Comprendre l’ensemble")
image(IFC_ASSET/"axo.png" if IFC_VIEWS_READY else None,15,64,390,207,"VUE IFC V7 · géométrie projet" if IFC_VIEWS_READY else "Axonométrie V7 attendue après modélisation; l’axo V6 n’est pas réutilisée")

# 09 — longitudinal section.
new_page("09","La lumière traverse le projet","Coupe d’usage au travers de la salle : table, assises et poteau conservé restent lisibles.","07 · Coupe d’usage")
image(DRAW/"coupe_usage.png" if DRAWINGS_READY else None,15,65,390,178,"A02 · coupe d’usage IFC V7" if DRAWINGS_READY else "Coupe d’usage V7 attendue de l’équipe BIM",mode="contain")
label_card(15,252,120,"ACCUEIL","Un seuil dégagé, un comptoir visible et un poste dimensionné pour une personne.","01")
label_card(147,252,120,"SALLE VITRÉE","La lumière circule; intimité et acoustique à définir avec le vitrage.","02",GREEN)
label_card(279,252,126,"RANGEMENTS","Rayonnages linéaires contre les murs; centre libre.","03",WOOD)

# 10 — transversal section.
new_page("10","Organiser l’espace en hauteur","Coupe transversale V7 · rangements et pièce de service en fond de salle.","08 · Coupe")
image(DRAW/"coupe_transversale.png" if DRAWINGS_READY else None,15,65,390,178,"A03 · coupe transversale V7" if DRAWINGS_READY else "Coupe transversale V7 attendue de l’équipe BIM",mode="contain")
rect(15,251,390,23,PAPER,LINE,.4)
txt(21,256,378,5,"UN FOND SOBRE, UNE SALLE OUVERTE",9,TERRA,bold=True)
txt(21,264,378,7,"Le WC existant se place derrière un écran; le rangement linéaire garde le centre libre.",9.5,INK)

# 11 — day-to-day arrival IFC exact view.
new_page("11","Depuis l’entrée, comprendre le lieu","Vue issue de la maquette V7 — implantation et géométrie du modèle.","09 · Accueillir")
image(IFC_ASSET/"interieur_entree.png" if IFC_VIEWS_READY else None,15,64,390,207,"VUE DE MAQUETTE IFC V7 · non générée par IA" if IFC_VIEWS_READY else "Vue d’entrée V7 attendue après modélisation; la vue V6 n’est pas montrée")

# 12 — reception and cafe.
new_page("12","Un comptoir, deux services","Le point d’accueil oriente et sert le café en gardant le passage libre.","10 · Accueil-café")
image(PLAN_DETAIL_ACCUEIL if DRAWINGS_READY else None,15,64,250,207,"EXTRAIT DU PLAN IFC V7 · accueil-café et passage")
label_card(281,68,124,"COMPTOIR V7","0,65 × 1,50 m; plan de travail à 0,84 m de principe. Posture assise à tester.","01")
label_card(281,117,124,"CAFÉ LÉGER","Machine et petit froid en option; eau, évacuation et puissance à coordonner.","02",WOOD)
label_card(281,166,124,"DÉGAGEMENTS MODÈLE","0,91 m côté public; 0,76 m côté service. Largeurs théoriques à valider avec assise et équipement.","03",GREEN)
rect(281,224,124,32,TERRALIGHT)
txt(288,230,110,7,"DÉTAIL DE FABRICATION À VENIR",8,TERRA,bold=True)
txt(288,239,110,12,"Panneaux et plateaux courants, chants protégés, assemblages réparables.",9,INK)

# 13 — meeting room.
new_page("13","Se réunir en gardant la lumière","Une enveloppe vitrée simple distingue la salle et préserve la profondeur.","11 · Se réunir")
image(AMBI/"interieur_soir.png",15,64,260,177,"VUE D’AMBIANCE IA · se réunir le soir, non contractuelle")
image(BLUE_ROOM,286,64,119,82,"EXISTANT PHOTOGRAPHIÉ · pièce bleue")
image(DRAW/"coupe_transversale.png" if DRAWINGS_READY else None,286,153,119,88,"DÉTAIL IFC V7" if DRAWINGS_READY else "Détail vitrage V7 à intégrer",mode="contain")
txt(15,248,390,22,"Vitrage à trame régulière, porte visible et bande de signalisation. Six places sont un objectif de programme : elles ne seront annoncées comme capacité qu’après vérification des cotes et des dégagements.",10,INK)

# 14 — the library as living room.
new_page("14","Des murs qui rangent, un centre qui respire","Rayonnages droits contre les parois; au centre, lecture et travail partagés.","12 · Lire et travailler")
image(DRAW/"elevation_rangements.png" if DRAWINGS_READY else None,15,64,252,156,"A04 · élévation des rayonnages V7" if DRAWINGS_READY else "Élévation des rangements V7 attendue",mode="contain")
image(IFC_ASSET/"interieur_accueil.png" if IFC_VIEWS_READY else None,276,64,129,156,"VUE IFC V7 · bibliothèque et mobilier" if IFC_VIEWS_READY else "Vue intérieure IFC V7 attendue")
label_card(15,233,124,"LINÉAIRE UTILE","≈ 6,69 m équipés au nord, à l’est et à l’ouest dans la maquette; longueur à vérifier sur site.","01",WOOD)
label_card(147,233,124,"CENTRE DÉGAGÉ","Une table commune et quelques postes indépendants, sans obstacle central.","02",GREEN)
label_card(279,233,126,"CONFORT","Passages, accès aux prises et stabilité à contrôler au plan coté.","03")

# 15 — terrace as a real but conditional extension.
new_page("15","L’ombre prolonge la bibliothèque","La terrasse couverte étend les usages vers l’arbre et le jardin.","13 · Prolonger")
image(IFC_ASSET/"terrasse.png" if IFC_VIEWS_READY else None,15,64,250,177,"VUE DE MAQUETTE IFC V7 · terrasse couverte" if IFC_VIEWS_READY else "Vue terrasse V7 attendue après mise à jour IFC")
image(SITE_TREE,276,64,129,83,"PHOTO · arbre et abord")
image(SITE_DALLAGE,276,155,129,86,"PHOTO · seuil et dallage à relever")
rect(15,251,390,22,GREENLIGHT)
txt(21,256,378,5,"CONSERVER LE LIEN AU JARDIN",8,GREEN,bold=True)
txt(21,264,378,7,"Assises et végétation légère prolongent l’ombre, en préservant l’accès et le passage.",9.5,INK)

# 16 — day/night ambient comparisons.
new_page("16","À la tombée du jour, le café prend le relais","Ambiances conceptuelles IA présentées à côté de vues exactes de la maquette.","14 · Rythmes")
image(AMBI/"interieur_jour.png",15,64,190,123,"AMBIANCE IA · jour · illustration non contractuelle")
image(AMBI/"interieur_soir.png",215,64,190,123,"AMBIANCE IA · soir · illustration non contractuelle")
image(IFC_ASSET/"interieur_entree.png" if IFC_VIEWS_READY else None,15,194,190,72,"IFC V7 · source géométrique, rendu de maquette" if IFC_VIEWS_READY else "Vue IFC V7 à intégrer, sans génération IA")
txt(215,196,190,10,"RÈGLE DE FIDÉLITÉ",10,TERRA,bold=True)
txt(215,209,190,46,"L’image IA propose une atmosphère; la vue IFC contrôle les murs, portes, vitrages, meubles et proportions. Les deux portent une légende distincte. Aucun détail de construction ne se déduit d’un rendu d’ambiance.",11,INK)

# 17 — materials details and locally buildable systems.
new_page("17","Faire simple pour construire juste","Assemblages courants; choix finaux après échantillons et consultation des artisans.","15 · Détails et matière")
image(AMBI/"../matieres.png",15,64,185,145,"IMAGE IA D’INTENTION MATIÈRES · non contractuelle")
items=[("MENUISERIE","Panneaux adaptés à l’humidité, chants protégés, tablettes réglables."),("VITRAGE","Profilés métalliques courants, verre de sécurité et quincaillerie disponible."),("PEINTURE","Support réparé, peinture lavable mate; test préalable des murs."),("SOL","Diagnostic et essais de nettoyage/réparation avant remplacement.")]
for i,(h,b) in enumerate(items):
    x=215+(i%2)*95; y=69+(i//2)*72
    label_card(x,y,88,h,b,f"0{i+1}", [WOOD,TERRA,GREEN,DARK][i])
txt(215,220,190,31,"À faire valider : disponibilité locale, essence et provenance du bois, tenue en climat humide, entretien, prix et délais. Palette indicative, non contractuelle.",9.5,MUTED)

# 18 — constructibility & phasing.
new_page("18","Un projet lisible, un chantier par étapes","D’abord sécuriser l’existant; ensuite installer les usages et les finitions.","16 · Réaliser")
steps=[("01","RELEVER","Plan, niveaux, portes, réseaux et limites extérieures."),("02","VALIDER","Cloison vitrée, assise d’accueil, WC, charges et cheminements."),("03","COORDONNER","Électricité, éclairage, plomberie, ventilation et supports."),("04","FABRIQUER","Menuiseries modulaires, vitrage, mobilier et finitions échantillonnés."),("05","INSTALLER","Pose par lots; contrôle des passages, accès et maintenance.")]
for i,(n,h,b) in enumerate(steps):
    x=15+i*78
    rect(x,88,68,112,"FFFFFF",LINE,.5)
    txt(x+7,96,55,12,n,24,TERRA,bold=True)
    txt(x+7,115,55,8,h,10,INK,bold=True)
    txt(x+7,130,55,48,b,9,MUTED)
    if i<4: line(x+68,144,x+77,144,TERRA,1)
rect(15,222,390,43,PAPER,LINE,.4)
txt(22,230,85,6,"FABRICATION LOCALE",8,TERRA,bold=True)
txt(22,240,367,15,"Comptoirs, rayonnages et tables en éléments répétitifs; profils de vitrage et pièces métalliques standards. Les détails de fixation et les dimensions sont arrêtés après relevé et consultation des entreprises.",9.5,INK)

# 19 — technical coordination, from engineering role when provided.
new_page("19","Vérifier les points clés avant le chantier","Décisions à coordonner avant lancement des plans d’exécution.","17 · Coordination technique")
tech = V7 / "faisabilite.json"
if tech.exists():
    try: techdata=json.loads(tech.read_text(encoding="utf-8"))
    except Exception: techdata={}
else: techdata={}
topics=[("EAU / CAFÉ","Position du point d’eau, évacuation gravitaire et équipements du comptoir."),("ÉLECTRICITÉ","Puissances café, prises, circuits et état du tableau existant."),("AIR / LUMIÈRE","Éclairage général et de lecture; ventilation et climatisation après cloisonnement."),("WC / RÉSERVE","Appareils, ventilation, porte, écran et structure du volume haut."),("EXTÉRIEUR","Seuils, pentes, propriété, garde-corps et eaux pluviales.")]
for i,(h,b) in enumerate(topics):
    y=68+i*35
    txt(15,y,10,8,f"{i+1:02d}",15,TERRA,bold=True); txt(33,y,83,8,h,10,INK,bold=True); txt(123,y,170,18,b,9.5,INK)
    rect(306,y,99,18,"F5F2ED",LINE,.35); txt(311,y+5,88,7,"À COORDONNER",8,MUTED,bold=True)
txt(15,254,390,16,"Aucune validation de structure, d’accessibilité réglementaire ou de chantier n’est revendiquée par ce dossier de conception.",9,MUTED)

# 20 — complete site plan, including the covered terrace.
new_page("20","Du plan intérieur au jardin","Plan général de l’IFC V7 · les locaux et la terrasse couverte dans une même lecture.","18 · Plan d’ensemble")
image(DRAW/"plan_amenagement.png" if DRAWINGS_READY else None,15,64,390,207,"PLAN GÉNÉRAL IFC V7 · bâtiment, seuil et terrasse" if DRAWINGS_READY else "Plan général V7 attendu de l’équipe BIM",mode="contain")

# 21 — longitudinal section as a complete architectural drawing.
new_page("21","La bibliothèque dans toute sa profondeur","Coupe longitudinale IFC V7 · hauteur et niveaux à rapprocher du relevé.","19 · Coupe longitudinale")
image(DRAW/"coupe_longitudinale.png" if DRAWINGS_READY else None,15,64,390,207,"COUPE LONGITUDINALE IFC V7" if DRAWINGS_READY else "Coupe longitudinale V7 attendue de l’équipe BIM",mode="contain")

# 22 — closing: proposal + transparent state.
new_page("22","Une adresse pour lire, apprendre et se retrouver","Une proposition ancrée dans le site, dessinée pour être construite par étapes.","20 · La proposition")
image(HERO_MONTAGE if HERO_MONTAGE.exists() else SITE_LAWN,15,64,235,207,"PHOTOMONTAGE IA · intention sur photo du site" if HERO_MONTAGE.exists() else "LE SITE EXISTANT · photographie, non cotée")
txt(269,70,134,7,"CE QUE LE PROJET PROPOSE",9,TERRA,bold=True)
txt(269,84,132,37,"Un seuil accueillant.\nUne salle claire.\nDes livres tout autour.\nUne terrasse à l’ombre.",16,INK,bold=True)
line(269,144,405,144,LINE,.5)
txt(269,153,134,6,"DOCUMENTS DE PROJET",9,TERRA,bold=True)
txt(269,165,132,25,"Plan, coupes, élévations et vues issus de l’IFC V7; matériaux et assemblages illustrés; PDF et présentation modifiable.",10,INK)
txt(269,202,134,6,"POINTS À CONFIRMER",9,TERRA,bold=True)
txt(269,214,132,37,"Relevé coté · raccordement photo/plan · volume haut · WC et réseaux · limites de terrasse · consultation des entreprises.",10,INK)
txt(269,264,132,7,"CONCEPTION ET MISE EN PAGE ASSISTÉES PAR IA",7.5,MUTED)

def color(hexstr): return tuple(int(hexstr[i:i+2],16) for i in (0,2,4))

def crop_file(path,w,h):
    p=Path(path); im=Image.open(p).convert("RGB")
    ratio=w/h; ir=im.width/im.height
    if ir>ratio:
        nw=round(im.height*ratio); x=(im.width-nw)//2; im=im.crop((x,0,x+nw,im.height))
    else:
        nh=round(im.width/ratio); y=(im.height-nh)//2; im=im.crop((0,y,im.width,y+nh))
    TMP.mkdir(parents=True,exist_ok=True)
    out=TMP/(re.sub(r"\W+","_",p.stem)+f"_{int(w*10)}x{int(h*10)}.jpg")
    im.save(out,quality=93)
    return out

def draw_pdf(pdfpath):
    c=canvas.Canvas(str(pdfpath),pagesize=(W*mm,H*mm),pageCompression=1)
    c.setTitle("Bibliothèque Nandjui D. Simon — Une bibliothèque habitée")
    c.setAuthor("K&Démi")
    c.setSubject("Dossier de concours architectural V7 · Deux Plateaux, Abidjan")
    for page in pages:
        for e in page["els"]:
            k=e["kind"]
            if k=="rect":
                c.setFillColorRGB(*[v/255 for v in color(e["fill"])])
                if e.get("stroke"):
                    c.setStrokeColorRGB(*[v/255 for v in color(e["stroke"])])
                    c.setLineWidth(e.get("width",.4)*mm)
                else: c.setStrokeColorRGB(*[v/255 for v in color(e["fill"])])
                x=e["x"]*mm; y=(H-e["y"]-e["h"])*mm; w=e["w"]*mm; h=e["h"]*mm
                if e.get("radius"): c.roundRect(x,y,w,h,e["radius"]*mm,fill=1,stroke=1 if e.get("stroke") else 0)
                else: c.rect(x,y,w,h,fill=1,stroke=1 if e.get("stroke") else 0)
            elif k=="line":
                c.setStrokeColorRGB(*[v/255 for v in color(e["color"])])
                c.setLineWidth(e.get("width",.5)*mm)
                if e.get("dash"): c.setDash(2*mm,1.6*mm)
                c.line(e["x"]*mm,(H-e["y"])*mm,e["x2"]*mm,(H-e["y2"])*mm)
                if e.get("dash"): c.setDash()
            elif k=="image":
                p=Path(e["path"]); x=e["x"]*mm; y=(H-e["y"]-e["h"])*mm; w=e["w"]*mm; h=e["h"]*mm
                if e.get("mode")=="cover": p=crop_file(p,e["w"],e["h"])
                c.drawImage(str(p),x,y,w,h,preserveAspectRatio=(e.get("mode")=="contain"),anchor="c",mask="auto")
            elif k=="text":
                font=e.get("font","Archivo"); size=e.get("size",10)
                if font not in pdfmetrics.getRegisteredFontNames(): font="Helvetica-Bold" if "Bold" in font else "Helvetica"
                lines=[]
                for para in str(e["text"]).split("\n"):
                    lines += simpleSplit(para,font,size,e["w"]*mm) or [""]
                leading=size*1.24*mm/2.83465
                top=(H-e["y"])*mm
                c.setFont(font,size); c.setFillColorRGB(*[v/255 for v in color(e.get("color",INK))])
                for i,t in enumerate(lines):
                    if (i+1)*leading > e.get("h",100)*mm: break
                    yy=top-(i+1)*leading
                    if e.get("align")=="right": c.drawRightString((e["x"]+e["w"])*mm,yy,t)
                    elif e.get("align")=="center": c.drawCentredString((e["x"]+e["w"]/2)*mm,yy,t)
                    else: c.drawString(e["x"]*mm,yy,t)
        c.showPage()
    c.save()

def draw_pptx(pptxpath):
    prs=Presentation(); prs.slide_width=Mm(W); prs.slide_height=Mm(H)
    prs.core_properties.title="Bibliothèque Nandjui D. Simon — Une bibliothèque habitée"
    prs.core_properties.author="K&Démi"
    prs.core_properties.subject="Dossier de concours architectural V7 · Deux Plateaux, Abidjan"
    blank=prs.slide_layouts[6]
    for page in pages:
        slide=prs.slides.add_slide(blank)
        for e in page["els"]:
            k=e["kind"]
            if k=="rect":
                shape=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Mm(e["x"]),Mm(e["y"]),Mm(e["w"]),Mm(e["h"]))
                shape.fill.solid(); shape.fill.fore_color.rgb=RGBColor(*color(e["fill"]))
                if e.get("stroke"):
                    shape.line.color.rgb=RGBColor(*color(e["stroke"])); shape.line.width=Pt(e.get("width",.4)*2.83465)
                else: shape.line.fill.background()
            elif k=="line":
                shape=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Mm(e["x"]),Mm(e["y"]),Mm(e["x2"]),Mm(e["y2"]))
                shape.line.color.rgb=RGBColor(*color(e["color"])); shape.line.width=Pt(e.get("width",.5)*2.83465)
                if e.get("dash"):
                    try: shape.line.dash_style=MSO_LINE_DASH_STYLE.DASH
                    except Exception: pass
            elif k=="image":
                p=Path(e["path"])
                if e.get("mode")=="cover": p=crop_file(p,e["w"],e["h"])
                if e.get("mode")=="contain":
                    with Image.open(p) as im: ir=im.width/im.height
                    boxr=e["w"]/e["h"]
                    if ir>boxr:
                        iw=e["w"]; ih=iw/ir; ix=e["x"]; iy=e["y"]+(e["h"]-ih)/2
                    else:
                        ih=e["h"]; iw=ih*ir; ix=e["x"]+(e["w"]-iw)/2; iy=e["y"]
                    slide.shapes.add_picture(str(p),Mm(ix),Mm(iy),width=Mm(iw),height=Mm(ih))
                else:
                    slide.shapes.add_picture(str(p),Mm(e["x"]),Mm(e["y"]),width=Mm(e["w"]),height=Mm(e["h"]))
            elif k=="text":
                box=slide.shapes.add_textbox(Mm(e["x"]),Mm(e["y"]),Mm(e["w"]),Mm(e.get("h",20)))
                tf=box.text_frame; tf.clear(); tf.word_wrap=True
                tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
                tf.vertical_anchor=MSO_ANCHOR.TOP
                paras=str(e["text"]).split("\n")
                for i,part in enumerate(paras):
                    p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
                    p.text=part; p.font.name="Archivo"; p.font.size=Pt(e.get("size",10)); p.font.bold="Bold" in e.get("font","")
                    p.font.color.rgb=RGBColor(*color(e.get("color",INK)))
                    p.alignment={"right":PP_ALIGN.RIGHT,"center":PP_ALIGN.CENTER}.get(e.get("align"),PP_ALIGN.LEFT)
                    p.space_after=Pt(0); p.space_before=Pt(0); p.line_spacing=1.08
        # Native text and images remain independently editable in PowerPoint.
    prs.save(pptxpath)

def export_html():
    PREVIEW.mkdir(parents=True,exist_ok=True)
    import fitz
    doc=fitz.open(OUT/"DOSSIER_CONCOURS_V7.pdf")
    titles=[]
    for i,p in enumerate(doc):
        pix=p.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False)
        pix.save(PREVIEW/f"page_{i+1:02}.png")
        titles.append(pages[i]["title"])
    cards=[]
    for i,t in enumerate(titles,1):
        cards.append(f'<a class="card" href="page_{i:02}.png"><img loading="lazy" src="page_{i:02}.png"><span>{i:02} · {html.escape(t)}</span></a>')
    html_doc='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bibliothèque Nandjui D. Simon — Concours V7</title><style>*{box-sizing:border-box}body{margin:0;background:#f2eee8;color:#292826;font:16px Arial,sans-serif}header{padding:24px 5vw;background:#fff;position:sticky;top:0;z-index:2;border-bottom:1px solid #d8d2c9}h1{font-size:clamp(22px,4vw,42px);margin:0 0 6px}header p{margin:0;color:#79746d}.grid{padding:24px 5vw;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:18px}.card{display:block;background:#fff;color:inherit;text-decoration:none;box-shadow:0 2px 14px #0001}.card img{width:100%;height:auto;display:block}.card span{display:block;padding:12px 15px;font-weight:600}footer{padding:25px 5vw;color:#79746d}footer a{display:inline-block;margin-top:12px;padding:10px 14px;color:#fff;background:#292826;text-decoration:none;border-radius:3px}</style><header><h1>Bibliothèque Nandjui D. Simon</h1><p>Une bibliothèque habitée · Du livre à la rencontre · Proposition de concours V7 · K&Démi</p></header><main class="grid">'''+''.join(cards)+'''</main><footer>Images d’ambiance IA, photos d’état des lieux et vues IFC sont légendées séparément dans le dossier. Présentation de conception, sans valeur de plan d’exécution.<br><a href="../VISITE_MAQUETTE_V7.html">Explorer la maquette 3D IFC</a></footer></html>'''
    (PREVIEW/"index.html").write_text(html_doc,encoding="utf-8")

def main():
    OUT.mkdir(exist_ok=True); TMP.mkdir(exist_ok=True); PREVIEW.mkdir(exist_ok=True)
    draw_pdf(OUT/"DOSSIER_CONCOURS_V7.pdf")
    draw_pptx(OUT/"DOSSIER_CONCOURS_V7_EDITABLE.pptx")
    export_html()
    print(f"Pages: {len(pages)} | vues IFC V7 validées: {IFC_VIEWS_READY} | dessins V7 validés: {DRAWINGS_READY}")
    print(f"PDF: {OUT/'DOSSIER_CONCOURS_V7.pdf'}")
    print(f"PPTX: {OUT/'DOSSIER_CONCOURS_V7_EDITABLE.pptx'}")
    print(f"Galerie: {PREVIEW/'index.html'}")

if __name__ == "__main__": main()
