from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.colors import HexColor, Color, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
import math

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "v6" / "DOSSIER_ESQUISSE_OPTION_C_V6.pdf"
W, H = landscape(A3)
BG = HexColor('#F6F4EF'); INK=HexColor('#242826'); MUTED=HexColor('#777B74')
ORANGE=HexColor('#D86B3D'); PALE=HexColor('#F1E5D9'); SAND=HexColor('#DDD0BD')
GREEN=HexColor('#718576'); BLUE=HexColor('#B8D3D2'); LIGHT=HexColor('#E7E6E0')
FONTDIR=ROOT/'charte'/'polices'
for name,file in [('Archivo','archivo-latin-400-normal.ttf'),('ArchivoMed','archivo-latin-500-normal.ttf'),('ArchivoSemi','archivo-latin-600-normal.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONTDIR/file)))
P=Path('/workspace/generated_images')
RENDER=P/'exec-4b11bc07-ca13-4a55-a30d-d700db9cf4f8.png'
if not RENDER.exists(): RENDER=ROOT/'v6'/'A06_vue_ambiance_piece_bleue_concept.png'
SITE=ROOT/'photos'/'LE SITE'/'WhatsApp Image 2026-10-13 at 5.50.23 PM (5).jpeg'
BLUE_ROOM=ROOT/'photos'/'interieur'/'WhatsApp Image 2026-10-13 at 6.12.46 PM (22).jpeg'
EXISTING=ROOT/'v5'/'dessins'/'A01_plan_RDC.png'

def image(c,path,x,y,w,h,mode='contain'):
    im=Image.open(path); iw,ih=im.size
    if mode=='cover':
        scale=max(w/iw,h/ih); dw,dh=iw*scale,ih*scale
    else:
        scale=min(w/iw,h/ih); dw,dh=iw*scale,ih*scale
    c.saveState(); c.setFillColor(white); c.rect(x,y,w,h,fill=1,stroke=0)
    c.drawImage(ImageReader(im),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')
    c.restoreState()

def txt(c,x,y,s,size=10,font='Archivo',color=INK):
    c.setFillColor(color); c.setFont(font,size); c.drawString(x,y,s)

def para(c,x,y,s,width,size=10,leading=None,font='Archivo',color=INK):
    leading=leading or size*1.35
    words=s.split(); lines=[]; line=''
    for word in words:
        cand=(line+' '+word).strip()
        if pdfmetrics.stringWidth(cand,font,size)<=width: line=cand
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    c.setFillColor(color); c.setFont(font,size)
    for i,l in enumerate(lines): c.drawString(x,y-i*leading,l)
    return y-len(lines)*leading

def pill(c,x,y,label,color=ORANGE):
    c.setFillColor(color); c.roundRect(x,y,6,6,3,fill=1,stroke=0)

def base(c,num,title,sub):
    c.setFillColor(BG); c.rect(0,0,W,H,fill=1,stroke=0)
    txt(c,42,H-38,'BIBLIOTHÈQUE DECIMO',15,'ArchivoSemi')
    txt(c,42,H-61,title,22,'ArchivoSemi',ORANGE)
    txt(c,42,H-81,sub,9,'Archivo',MUTED)
    c.setStrokeColor(HexColor('#D7D2C8')); c.setLineWidth(.7); c.line(42,H-94,W-42,H-94)
    c.line(42,36,W-42,36)
    txt(c,42,21,'ESQUISSE DE PRINCIPE  •  BASE IFC V5  •  COTES À CONFIRMER SUR SITE',7.4,'ArchivoSemi',MUTED)
    c.setFillColor(ORANGE); c.setFont('ArchivoSemi',8); c.drawRightString(W-42,21,f'V6  /  {num:02d}')

def note_box(c,x,y,w,h,title,text,accent=ORANGE):
    c.setFillColor(white); c.roundRect(x,y,w,h,7,fill=1,stroke=0)
    c.setFillColor(accent); c.rect(x,y+h-4,w,4,fill=1,stroke=0)
    txt(c,x+14,y+h-24,title,10,'ArchivoSemi',accent)
    para(c,x+14,y+h-42,text,w-28,8.5,11,'Archivo',INK)

def plan_diagram(c,x,y,scale):
    # Schematic scaled to V5 envelope only; internal zoning is a design hypothesis.
    ww,hh=6.78*scale,7.68*scale
    # terrace extents from V5 IFC; the additional outside strip is deliberately unmeasured.
    c.setFillColor(HexColor('#ECE6DB')); c.rect(x-0.15*scale,y-2.66*scale,ww+0.3*scale,2.66*scale,fill=1,stroke=0)
    c.setStrokeColor(HexColor('#BEB6A8')); c.setDash(2,3); c.rect(x-0.15*scale,y-3.62*scale,ww+0.3*scale,.96*scale,fill=0,stroke=1); c.setDash()
    txt(c,x+ww*.25,y-2.18*scale,'TERRASSE COUVERTE · V5',8,'ArchivoSemi',MUTED)
    txt(c,x+ww*.22,y-3.25*scale,'EXTENSION EXTÉRIEURE À ÉTUDIER',6.8,'ArchivoSemi',GREEN)
    # outside envelope and internal rough bands
    c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(3); c.rect(x,y,ww,hh,fill=1,stroke=1)
    # areas: left/back service and blue room, main right library, reception front-left
    left=ww*.40
    c.setFillColor(Color(BLUE.red,BLUE.green,BLUE.blue,alpha=.58)); c.setStrokeColor(ORANGE); c.setDash(5,3); c.setLineWidth(1.3)
    c.roundRect(x+6,y+hh*.34,left-12,hh*.55,7,fill=1,stroke=1); c.setDash()
    c.setFillColor(Color(PALE.red,PALE.green,PALE.blue,alpha=.9)); c.roundRect(x+6,y+8,left-12,hh*.30,7,fill=1,stroke=0)
    c.setFillColor(Color(GREEN.red,GREEN.green,GREEN.blue,alpha=.15)); c.rect(x+left,y+4,ww-left-5,hh-8,fill=1,stroke=0)
    # WC rear and small reserve above
    c.setFillColor(HexColor('#F1E6D8')); c.setStrokeColor(ORANGE); c.setDash(3,2); c.rect(x+8,y+hh*.79,left*.8,hh*.15,fill=1,stroke=1); c.setDash()
    # counter and seat: back against west wall, looking east; sightline north to meeting
    c.setFillColor(SAND); c.setStrokeColor(HexColor('#927354')); c.roundRect(x+12,y+hh*.08,left*.62,16,3,fill=1,stroke=1)
    c.setFillColor(INK); c.circle(x+12,y+hh*.08+8,4,fill=1,stroke=0)
    c.setStrokeColor(ORANGE); c.setLineWidth(1.4); c.line(x+22,y+hh*.08+8,x+left*.62+8,y+hh*.08+8); c.line(x+22,y+hh*.08+8,x+left*.8,y+hh*.47)
    # shelves on east and north perimeter
    c.setFillColor(HexColor('#8B6448'))
    for sy in [y+hh*.16,y+hh*.28,y+hh*.45,y+hh*.58,y+hh*.70,y+hh*.85]: c.rect(x+ww-12,sy,7,hh*.09,fill=1,stroke=0)
    c.rect(x+left+12,y+hh-18,ww-left-27,7,fill=1,stroke=0)
    # shared/cowork table
    c.setFillColor(SAND); c.roundRect(x+left+ww*.12,y+hh*.36,ww*.26,hh*.11,5,fill=1,stroke=0)
    for i in range(4): c.circle(x+left+ww*.16+i*ww*.065,y+hh*.34,3,fill=1,stroke=0)
    # meeting table
    c.setFillColor(SAND); c.roundRect(x+left*.13,y+hh*.49,left*.65,hh*.12,4,fill=1,stroke=0)
    # Indicative six-seat layout; final count depends on measured clearances.
    c.setFillColor(SAND)
    mt=x+left*.13; my=y+hh*.49; mw=left*.65; mh=hh*.12
    for xx in [mt+mw*.20,mt+mw*.50,mt+mw*.80]:
        c.circle(xx,my-5,2.8,fill=1,stroke=0); c.circle(xx,my+mh+5,2.8,fill=1,stroke=0)
    # entrance opening
    c.setStrokeColor(BG); c.setLineWidth(6); c.line(x+ww*.55,y,x+ww*.72,y)
    c.setFillColor(INK); c.setFont('ArchivoSemi',6.5); c.drawCentredString(x+ww*.63,y-13,'ENTRÉE · V5')
    c.setFillColor(ORANGE); c.setFont('ArchivoSemi',5.9); c.drawCentredString(x+left*.50,y+hh*.67,'PIÈCE BLEUE : SALLE VITRÉE*')
    c.setFillColor(INK); c.setFont('ArchivoSemi',5.8); c.drawCentredString(x+left*.40,y+hh*.89,'WC AU FOND')
    c.setFont('ArchivoSemi',5.8); c.drawCentredString(x+left*.40,y+hh*.83,'RÉSERVE EN HAUTEUR*')
    c.setFillColor(INK); c.setFont('ArchivoSemi',8); c.drawCentredString(x+left+(ww-left)/2,y+hh*.57,'BIBLIOTHÈQUE')
    c.setFont('Archivo',7); c.drawCentredString(x+left+(ww-left)/2,y+hh*.53,'rayonnages continus · coworking léger')
    c.setFont('ArchivoSemi',7); c.drawCentredString(x+left*.50,y+hh*.22,'ACCUEIL + CAFÉ')
    c.setFillColor(MUTED); c.setFont('Archivo',6.2); c.drawString(x,y+hh+12,'ENVELOPPE IFC V5 : 6,78 × 7,68 m (référence de maquette)')
    return ww,hh

def section(c,x,y,w,h):
    # Sectional principle without invented heights/dimensions.
    c.setStrokeColor(INK); c.setLineWidth(4); c.line(x,y,x+w,y); c.line(x,y+h*.55,x,y+h); c.line(x+w,y+h*.55,x+w,y+h)
    c.setFillColor(HexColor('#EEE9DF')); c.rect(x,y,w,h*.55,fill=1,stroke=0)
    # room glass on left, library zone center, WC/rear store right
    c.setStrokeColor(ORANGE); c.setLineWidth(2); c.rect(x+w*.04,y,w*.38,h*.72,fill=0,stroke=1)
    c.setStrokeColor(HexColor('#9EBAB9')); c.setLineWidth(1.5); c.line(x+w*.04,y+h*.12,x+w*.42,y+h*.12)
    # rear enclosure and observed raised zone (schematic, not structural validation)
    c.setFillColor(Color(.85,.79,.69,alpha=.55)); c.rect(x+w*.76,y+h*.55,w*.20,h*.18,fill=1,stroke=0)
    c.setStrokeColor(ORANGE); c.setDash(4,3); c.line(x+w*.74,y+h*.56,x+w*.98,y+h*.56); c.setDash()
    # book shelves
    c.setFillColor(HexColor('#8B6448'))
    for i in range(6): c.rect(x+w*.48+i*w*.035,y,w*.018,h*(.32+(i%2)*.06),fill=1,stroke=0)
    # low coffee counter
    c.setFillColor(SAND); c.rect(x+w*.06,y,w*.18,h*.16,fill=1,stroke=0)
    # glazed meeting partition
    c.setStrokeColor(HexColor('#8DA8A5')); c.setLineWidth(1.7)
    for xx in [x+w*.04,x+w*.17,x+w*.30,x+w*.42]: c.line(xx,y,xx,y+h*.72)
    # figures approximate, no scale claim
    c.setStrokeColor(INK); c.setLineWidth(1.1)
    for xx in [x+w*.15,x+w*.31,x+w*.58]:
        c.circle(xx,y+h*.13,4,fill=0,stroke=1); c.line(xx,y+h*.09,xx,y+h*.02)
    c.setStrokeColor(MUTED); c.setLineWidth(.8); c.line(x+w*.04,y+h*.78,x+w*.42,y+h*.78)
    txt(c,x+w*.08,y+h*.84,'RÉUNION VITRÉE',8,'ArchivoSemi',ORANGE)
    txt(c,x+w*.49,y+h*.45,'RAYONNAGES',8,'ArchivoSemi',ORANGE)
    txt(c,x+w*.76,y+h*.77,'WC + RÉSERVE HAUTE',7,'ArchivoSemi',ORANGE)
    txt(c,x+w*.76,y+h*.36,'accès / marches à relever',6.7,'Archivo',MUTED)
    txt(c,x+w*.02,y-16,'COUPE DE PRINCIPE — HAUTEURS, STRUCTURE ET ACCÈS À RELEVER',7,'ArchivoSemi',MUTED)

def main():
    if RENDER.exists():
        dest=ROOT/'v6'/'A06_vue_ambiance_piece_bleue_concept.png'; dest.write_bytes(RENDER.read_bytes())
    c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
    c.setTitle('Bibliothèque Decimo — Option C V6 — esquisse de principe')
    c.setAuthor('K&Démi — proposition de travail')
    # 01 cover
    base(c,1,'Lire, se rencontrer, prendre un café','Une bibliothèque de quartier pensée pour le quotidien, la famille et les petites réunions.')
    image(c,RENDER,42,96,W*.57,H-225,'cover')
    image(c,SITE,W*.61, H*.50, W*.35, H*.37,'cover')
    txt(c,W*.61,H*.47,'LE SITE RÉEL · OMBRAGE, MURET, DALLE ET JARDIN',8,'ArchivoSemi',MUTED)
    txt(c,W*.61, H*.42,'UNE SECONDE PROPOSITION',12,'ArchivoSemi',ORANGE)
    para(c,W*.61,H*.39,'Un lieu simple à construire : accueil-café tenu depuis un poste unique, bibliothèque généreuse, salle de réunion vitrée et terrasse habitée.',W*.34,11,16,'Archivo',INK)
    note_box(c,W*.61,115,W*.34,74,'INTENTION DE PROJET','Réutiliser le local existant, privilégier des modules droits de menuiserie, préserver la lumière et tirer parti de la terrasse couverte. La pièce bleue devient le repère de la salle vitrée, sous réserve de recaler le plan sur le relevé.',ORANGE)
    txt(c,42,68,'IMAGE D’AMBIANCE CONCEPTUELLE · elle traduit une intention, pas une restitution exacte du lieu.',7.5,'Archivo',MUTED)
    c.showPage()
    # 02 site evidence and IFC basis
    base(c,2,'Partir de l’existant','Lecture croisée des photos de site et d’intérieur avec la maquette IFC V5.')
    image(c,EXISTING,42,92,W*.48,H-210,'contain')
    txt(c,54,75,'PLAN IFC V5 · DOCUMENT DE RÉFÉRENCE, NON RELEVÉ TEL QUE CONSTRUIT',7.2,'ArchivoSemi',MUTED)
    image(c,BLUE_ROOM,W*.53,H*.52,W*.20,H*.31,'cover')
    image(c,SITE,W*.75,H*.52,W*.22,H*.31,'cover')
    txt(c,W*.53,H*.49,'PIÈCE BLEUE · VUE VERS LE FOND',7,'ArchivoSemi',MUTED)
    txt(c,W*.75,H*.49,'FAÇADE · SEUIL ET ENVIRONNEMENT',7,'ArchivoSemi',MUTED)
    note_box(c,W*.53,190,W*.20,86,'OBSERVÉ EN PHOTO','Pièce bleue allongée, porte au fond, deux marches et volume haut derrière une séparation. Aucune cote ni capacité porteuse ne se déduit des images.',ORANGE)
    note_box(c,W*.75,190,W*.22,86,'DEHORS','Dalle au droit de l’entrée, muret/grille, chemin irrégulier et surfaces plantées. Le prolongement de terrasse dépend des limites privatives et des niveaux.',GREEN)
    note_box(c,W*.53,88,W*.44,78,'BASE DE TRAVAIL','La V5 donne une enveloppe intérieure de 6,78 × 7,68 m, 43,55 m² intérieurs et 15,74 m² de terrasse couverte. Ces valeurs appartiennent à la maquette d’esquisse. Les photos et les hauteurs réelles restent à recaler par un relevé.',INK)
    c.showPage()
    # 03 arrangement plan
    base(c,3,'Plan d’aménagement de principe','Accueil-café à l’entrée · salle vitrée dans la pièce bleue · rayonnages abondants dans le volume principal.')
    scale=48
    x=77; y=252
    ww,hh=plan_diagram(c,x,y,scale)
    txt(c,x,y-3.62*scale-25,'Enveloppe à l’échelle de la V5; cloisons, mobiliers et zones intérieures sont indicatifs.',7.1,'ArchivoSemi',MUTED)
    txt(c,x,y-3.62*scale-36,'* Correspondance de la pièce bleue avec les espaces V5 à confirmer au relevé avant tout déplacement de cloison.',7.0,'Archivo',MUTED)
    # side editorial notes
    rx=545
    txt(c,rx,H-132,'ORGANISATION ET USAGES',12,'ArchivoSemi',INK)
    notes=[('01  ACCUEIL + CAFÉ','Poste unique adossé au mur. Depuis l’assise : la salle de réunion reste dans le champ latéral gauche, les livres devant. Comptoir de service compact à portée de main.'),('02  SALLE VITRÉE','Dans la pièce bleue repérée par la cliente. 4 à 6 places à étudier selon les dégagements réels; cloison et porte à caler après relevé.'),('03  BIBLIOTHÈQUE + COWORKING','Rayonnages droits sur les murs disponibles, renforcés au nord-est. Quelques postes individuels et une table commune, en gardant une circulation simple.'),('04  WC + RÉSERVE','WC au fond de la pièce bleue; écran visuel depuis les zones publiques. Le volume haut peut servir de réserve légère uniquement après vérification structurelle et accès.'),('05  TERRASSE','Garder la terrasse couverte V5. Étudier une extension sur le dallage extérieur après relevé des limites, seuils, garde-corps et niveaux.')]
    yy=H-158
    for t,b in notes:
        txt(c,rx,yy,t,9.5,'ArchivoSemi',ORANGE); yy=para(c,rx,yy-16,b,W-rx-50,8.5,11,'Archivo',INK)-13
    c.setStrokeColor(ORANGE); c.setLineWidth(1.2); c.setDash(4,3); c.roundRect(x+5,y+hh*.34,ww*.4-10,hh*.55,6,fill=0,stroke=1); c.setDash()
    c.showPage()
    # 04 architectural section and making logic
    base(c,4,'Coupe et détails à vérifier','Le projet se dessine autour de trois éléments existants : la pièce bleue, le volume arrière et le seuil terrasse.')
    section(c,60,310,W-120,240)
    note_box(c,60,128,270,112,'01 · HAUTEURS','Relever hauteur libre, retombées, niveau du plateau haut, garde-corps et éventuel accès. La hauteur de 3,00 m de la V5 n’est pas confirmée par photo.',ORANGE)
    note_box(c,350,128,270,112,'02 · STRUCTURE','Le rangement observé en hauteur est une hypothèse d’usage, pas une mezzanine validée. Faire vérifier appuis, dalle/solives, charge admissible et sécurité avant stockage.',INK)
    note_box(c,640,128,270,112,'03 · TERRASSE','Mesurer le seuil, les marches, le dallage et le muret. Confirmer l’emprise disponible et l’écoulement des eaux avant de prolonger les tables.',GREEN)
    note_box(c,930,128,W-990,112,'04 · FABRICATION','Mobilier en panneaux et tasseaux courants, table rectangulaire, étagères modulaires répétitives, cloison vitrée à trame simple. Les dimensions finales seront prises au relevé.',ORANGE)
    c.showPage()
    # 05 palette / deliverables and due diligence
    base(c,5,'Ambiance et étapes vers un dossier exécutable','Chaleur du bois et de la lumière, avec des détails sobres et des assemblages réalisables localement.')
    image(c,RENDER,42,135,W*.52,H-260,'cover')
    px=W*.59
    txt(c,px,H-130,'PALETTE PROPOSÉE',12,'ArchivoSemi',INK)
    sw=[('#F0EDE5','Enduit clair, mat'),('#B69A78','Bois naturel en touches'),('#D86B3D','Terre cuite en accent'),('#242826','Métal noir discret')]
    yy=H-161
    for col,label in sw:
        c.setFillColor(HexColor(col)); c.roundRect(px,yy-11,27,20,3,fill=1,stroke=0); txt(c,px+39,yy-5,label,9,'Archivo'); yy-=35
    txt(c,px,H-325,'DÉCISIONS À PRENDRE AU RELEVÉ',11,'ArchivoSemi',ORANGE)
    bullets=['Relever murs, ouvertures, poteaux et orientation; identifier sur place la pièce bleue dans le plan V5.','Coter WC, évacuations, alimentation et ventilation; confirmer la porte et l’écran visuel.','Mesurer le volume haut et faire vérifier la structure et l’accès.','Vérifier limites privatives, garde-corps et niveaux de la terrasse extérieure.','Valider la capacité de réunion souhaitée, le poste café et la largeur des passages.']
    yy=H-350
    for b in bullets:
        pill(c,px,yy-2,""); yy=para(c,px+13,yy,b,W-px-58,8.7,12,'Archivo',INK)-7
    note_box(c,px,104,W-px-42,56,'STATUT V6','Esquisse de conception et calque de programme dans l’IFC V5. Aucune géométrie V5 n’a été déplacée. Les planches ne valent ni plan d’exécution ni validation de structure.',INK)
    txt(c,42,88,'RÔLES DE REVUE IA MOBILISÉS',7.5,'ArchivoSemi',MUTED)
    txt(c,42,73,'Architecture intérieure · direction artistique · BIM/IFC · ingénierie · dossier graphique. Ce sont des rôles d’analyse IA, pas des professionnels habilités signataires.',7,'Archivo',MUTED)
    c.save()

if __name__=='__main__': main()
