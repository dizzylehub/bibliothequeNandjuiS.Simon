"""Génère V7 comme variante modifiable de V6, sans écraser les versions antérieures.

Les espaces et enveloppes V5/V6 sont conservés comme géométrie de repérage à relever.
Les ajouts V7 sont un projet d'aménagement sur enveloppe existante supposée; la réserve
haute et l'extension de terrasse restent des options distinctes héritées de V6.
"""
from pathlib import Path
import ifcopenshell, ifcopenshell.api, ifcopenshell.guid
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'v6'/'DECIMO_ESQ_V6_OPTION_C.ifc'
OUT=ROOT/'v7'/'DECIMO_PROPOSITION_V7.ifc'
f=ifcopenshell.open(str(SRC)); api=ifcopenshell.api.run
OH=f.by_type('IfcOwnerHistory')[0]
body=next(x for x in f.by_type('IfcGeometricRepresentationSubContext') if x.ContextIdentifier=='Body')
rdc=next(x for x in f.by_type('IfcBuildingStorey') if 'RDC' in (x.Name or ''))
CM=100.0

def P2(x,y): return f.createIfcCartesianPoint((x*CM,y*CM))
def P3(x,y,z): return f.createIfcCartesianPoint((x*CM,y*CM,z*CM))
DZ=f.createIfcDirection((0.,0.,1.))
def box(x0,y0,x1,y1,z0,z1):
    prof=f.createIfcRectangleProfileDef('AREA',None,f.createIfcAxis2Placement2D(P2((x0+x1)/2,(y0+y1)/2),None),(x1-x0)*CM,(y1-y0)*CM)
    return f.createIfcExtrudedAreaSolid(prof,f.createIfcAxis2Placement3D(P3(0,0,z0),None,None),DZ,(z1-z0)*CM)

def style(name): return next((s for s in f.by_type('IfcSurfaceStyle') if s.Name==name),None)
def color_items(items,style_name):
    st=style(style_name)
    if st:
        for it in items: f.createIfcStyledItem(it,[st],None)
    return items

def remove(pid):
    p=f.by_id(pid)
    if p and p.is_a('IfcProduct'): api('root.remove_product',f,product=p)
def remove_named(names):
    for name in names:
        while True:
            p=next((x for x in f.by_type('IfcProduct') if (x.Name or '')==name),None)
            if p is None: break
            api('root.remove_product',f,product=p)

def add(name,cls,items,style_name,description,props,predefined=None,material_name=None):
    p=api('root.create_entity',f,ifc_class=cls,name=name,predefined_type=predefined)
    p.OwnerHistory=OH; p.Description=description
    api('spatial.assign_container',f,products=[p],relating_structure=rdc)
    api('geometry.edit_object_placement',f,product=p,matrix=np.eye(4),is_si=True)
    color_items(items,style_name)
    rep=f.createIfcShapeRepresentation(body,'Body','SweptSolid',items)
    api('geometry.assign_representation',f,product=p,representation=rep)
    ps=api('pset.add_pset',f,product=p,name='KDEMI_Option_C_V7')
    api('pset.edit_pset',f,pset=ps,properties={'Statut':'Projet V7 sur enveloppe V5 supposée — à relever','Modifiable':True,**props})
    if material_name:
        m=next((x for x in f.by_type('IfcMaterial') if x.Name==material_name),None)
        if m: f.createIfcRelAssociatesMaterial(ifcopenshell.guid.new(),OH,None,None,[p],m)
    return p

# Remove V6's first reception arrangement and the V5 small furniture that obstructs
# the new counter/staff route. The rest of the V6/V5 furniture remains untouched.
remove_named((
 'V6 — comptoir accueil-café intégré','V6 — siège poste accueil-café',
 'V6 — table coworking quatre places',
 'DECIMO_T02_Table_Ronde:ESQ - sur mesure:4350667',
 'DECIMO_P05_Pouf_indigo:ESQ','DECIMO_B02_Banquette:ESQ - sur mesure:4350666',
 'DECIMO_P01_Pouf:ESQ - sur mesure',
 'DECIMO_B01_Rayonnage_800:ESQ - sur mesure:4350658',
 'DECIMO_B01_Rayonnage_800:ESQ - sur mesure:4350659',
 'DECIMO_B01_Rayonnage_800:ESQ - sur mesure:4350660',
 'DECIMO_M01_Console_Vinyles_P40:ESQ - sur mesure',
 'DECIMO_V05_Podium_vitrine:ESQ - sur mesure',
 'DECIMO_N02_Niche_banquette:ESQ - sur mesure',
 'DECIMO_N01_Niche_bibliotheque:ESQ - sur mesure'))

# Glazing between meeting room Space 03 and reading Space 01.
# Replace only the measured-in-IFC solid partition/door; preserve room envelopes.
remove_named(('PORTE BOIS KDA:DECIMO - WC 930:4350622',
              'Cloison pleine salle de réunion','Baie porte salle de réunion'))
# Fixed transparent pane in the existing partition line, leaving a ~0.90 m glazed door.
add('V7 — vitrage fixe cloison salle 03 / lecture 01','IfcWindow',
    [box(2.990,2.88,3.010,4.02,.06,2.52)],'KDEMI - Vitrage clair',
    'Panneau fixe transparent, cloison rectiligne entre salle de réunion et bibliothèque.',
    {'Usage':'Cloison vitrée salle de réunion / lecture','Position':'x≈3,00 m; y=2,88–4,02 m; z=0,06–2,52 m','Statut':'Projet V7; emprise V5 conservée comme repérage, à relever'},'WINDOW','KDEMI - Vitrage clair')
add('V7 — porte vitrée salle 03 / lecture 01','IfcDoor',
    [box(2.990,4.11,3.010,4.97,.08,2.42)],'KDEMI - Vitrage clair',
    'Porte vitrée rectiligne dans la cloison entre la salle de réunion et la bibliothèque; représentation fermée, débattement non défini.',
    {'Usage':'Porte de liaison salle 03 / lecture 01','Largeur_utile_principe_m':.86,'Statut':'Projet V7 sur enveloppe V5 à relever','Debattement':'Non modélisé; à définir après relevé'},'DOOR','KDEMI - Vitrage clair')
# Bronze/black slim frame, threshold and one vertical mullion. The door leaf stays separate.
frame=[]
frame += [box(2.950,2.82,3.050,2.89,0,2.60),box(2.950,4.02,3.050,4.10,0,2.60),
          box(2.950,4.97,3.050,5.04,0,2.60),box(2.950,2.82,3.050,5.04,2.54,2.60),
          box(2.950,2.82,3.050,5.04,0,.055),box(2.950,3.42,3.050,3.46,.055,2.54)]
add('V7 — cadres et montant cloison vitrée salle 03 / lecture 01','IfcMember',frame,'KDEMI - Acier noir mat',
    'Cadres minces et montant vertical de la cloison vitrée; implantés dans la ligne de cloison pleine V5 déposée.',
    {'Usage':'Cadre de vitrage et porte','Statut':'Projet V7; épaisseur, fixations et détail de seuil à relever'},'MULLION','KDEMI - Acier noir mat')
# Close the acoustic plenum above the glazed partition up to the existing ceiling datum.
add('V7 — bandeau acoustique cloison salle 03 / lecture 01','IfcCovering',
    [box(2.950,2.82,3.050,5.04,2.60,3.30)],'KDEMI - Acoustique laine de bois sable',
    'Bandeau acoustique continu au-dessus du vitrage pour fermer le plénum jusqu’au faux plafond existant; ossature, raccords et performances à coordonner.',
    {'Usage':'Fermeture acoustique haute de cloison vitrée','Position':'x=2,95–3,05 m; y=2,82–5,04 m; z=2,60–3,30 m',
     'Hauteur_bandeau_m':.70,'Statut':'Projet V7; support, raccords, réaction au feu et performance acoustique à coordonner sur site'},'CEILING','KDEMI - Acoustique laine de bois sable')

# Remove arched project façade components before rebuilding the rectilinear alternative.
remove_named((
 'Porte d\'entrée cintrée double (0,90 + 0,60)',
 'Vitrage baie cintrée C','Vitrage baie cintrée B','Vitrage baie cintrée A',
 'Claustra terre cuite baie C','Claustra terre cuite baie B','Claustra terre cuite baie A',
 'Inserts Adinkra terre cuite - claustra baie A',
 'Inserts Adinkra terre cuite - claustra baie B',
 'Inserts Adinkra terre cuite - claustra baie C',
 'Vitrine en arche - châssis acier noir (baie A)',
 'Châssis fixe acier noir (baie B)','Châssis fixe acier noir (baie C)',
 'Portail d\'entrée terre cuite'))
# Remove the two tree/o culus feature rings from the superseded V5 centrepiece. Existing
# downlights stay in the engineering model; V7 adds distinct coordination intentions below.
remove_named(("Anneau LED indirect de l'oculus","Anneau LED sous la canopée de l'arbre à livres"))
# The curved niche liner and old tree oculus are superseded with their V5 furniture.
remove_named(('Doublage cintré des niches',"Oculus de l'arbre à livres - bandeau iroko et sous-face indigo"))
# Replace the V5 facade wall and curved opening cuts by rectangular project segments.
# The overall facade envelope is retained only as a survey reference.
remove_named(('Mur de base:Agglos creux 15 + Enduit 2 Faces 1.5_K&D:4350590',
              'Enduit terre - face intérieure de la façade',
              'Baie entrée principale','Baie cintrée A','Baie cintrée B','Baie cintrée C'))
apertures=((.55,1.75,.45,2.40),(2.00,2.70,.90,2.25),(3.35,4.85,0.0,2.798),(5.15,6.25,.60,2.35))
xs=sorted({.09,6.51,*[v for ap in apertures for v in ap[:2]]})
zs=sorted({0.0,3.30,*[v for ap in apertures for v in ap[2:]]})
facade=[]
for xa,xb in zip(xs,xs[1:]):
    for za,zb in zip(zs,zs[1:]):
        xm=(xa+xb)/2; zm=(za+zb)/2
        if any(x0 < xm < x1 and z0 < zm < z1 for x0,x1,z0,z1 in apertures): continue
        facade.append(box(xa,-.09,xb,.105,za,zb))
add('V7 — façade rectiligne segmentée autour baies rectangulaires','IfcWall',facade,'KDEMI - Enduit chaux sable',
    'Réinterprétation de la façade de projet V5 en segments orthogonaux autour des ouvertures rectangulaires V7; l’enveloppe globale est conservée comme repère mais cette géométrie doit être relevée et validée structurellement.',
    {'Usage':'Façade de proposition rectiligne','Emprise_globale':'x=0,09–6,51 m; y=-0,09–0,105 m; z=0–3,30 m',
     'Statut':'Correction de proposition sur enveloppe V5 supposée; ouvertures, structure et raccords à relever sur site'},'SOLIDWALL','KDEMI - Enduit chaux sable')
# Rectangular entrance grille door within opening #2062 (envelope stays unchanged).
entry=[]
entry += [box(3.38,-.055,3.43,-.025,.02,2.56),box(4.77,-.055,4.82,-.025,.02,2.56),
          box(3.40,-.055,4.80,-.025,2.52,2.57),box(3.40,-.055,4.80,-.025,.02,.07),
          box(4.085,-.055,4.115,-.025,.07,2.52)]
for x in np.linspace(3.48,4.72,9): entry.append(box(float(x),-.052,float(x)+.018,-.028,.07,2.52))
for z in (.55,1.05,1.55,2.05): entry.append(box(3.43,-.052,4.77,-.028,z,z+.025))
add('V7 — porte grille rectangulaire entrée - hypothèse','IfcDoor',entry,'KDEMI - Acier noir mat',
    'Grille rectiligne à deux vantaux dans l’ouverture d’entrée existante; aucune modification de la maçonnerie ni du gabarit d’ouverture.',
    {'Usage':'Entrée principale','Statut':'Projet V7 sur ouverture V5 hypothétique, gabarit à relever','Trame':'Montants droits répétitifs, traverse horizontale','Ouverture':'OpeningElement V5 conservé; sens et fonctionnement des vantaux à définir'},'GATE','KDEMI - Acier noir mat')

# Rectangular glazing/grilles replacing the three arched project window units in their
# existing openings. The frame envelopes remain only indicative and require survey.
for label,x0,x1,z0,z1,divs in (
    ('A',.55,1.75,.45,2.40,7),('B',2.00,2.70,.90,2.25,4),('C',5.15,6.25,.60,2.35,7)):
    lo=x0+.035; hi=x1-.035; bot=z0+.035; top=z1-.035
    pane=[box(lo,-.012,hi,.006,bot,top)]
    add(f'V7 — vitrage rectangulaire baie {label} - hypothèse','IfcWindow',pane,'KDEMI - Vitrage clair',
        f'Vitrage rectangulaire simple dans la baie {label}; ouverture rectangulaire de proposition remplaçant la découpe cintrée IFC V5, à relever.',
        {'Usage':f'Baie façade {label}','Statut':'Projet rectiligne V7 sur enveloppe globale IFC V5 supposée','A_relever':'Profil et dimensions de la baie, appuis, cadre et étanchéité'},'WINDOW','KDEMI - Vitrage clair')
    bars=[]
    bars += [box(lo,-.052,hi,-.025,bot,bot+.035),box(lo,-.052,hi,-.025,top-.035,top)]
    for i in range(1,divs):
        x=lo+(hi-lo)*i/divs
        bars.append(box(x-.012,-.052,x+.012,-.025,bot+.035,top-.035))
    for z in (bot+.38,bot+.76,bot+1.14):
        if z<top-.04: bars.append(box(lo,-.052,hi,-.025,z,z+.022))
    add(f'V7 — trame droite baie {label} - hypothèse','IfcMember',bars,'KDEMI - Acier noir mat',
        f'Trame métallique rectiligne de proposition pour la baie {label}; ouverture à relever.',
        {'Usage':f'Grille droite baie {label}','Statut':'Projet V7 sur enveloppe à relever','Modules_verticaux':divs},'MULLION','KDEMI - Acier noir mat')

# Vitrine en arche is a project insert, not a structural wall; removed with its frame.
# The V5 wall/opening products remain as context/measurement hypotheses.

# Reoriented single reception/café workstation in Space 02.
# North-south counter; staff stool west, public clear zone east; staff enters around north end.
add('V7 — comptoir accueil-café longitudinal - poste unique','IfcFurnishingElement',[
    box(1.35,.20,2.00,1.70,.78,.84),
    box(1.37,.23,1.42,.29,0,.78),box(1.93,.23,1.98,.29,0,.78),
    box(1.37,1.61,1.42,1.67,0,.78),box(1.93,1.61,1.98,1.67,0,.78),
    box(1.96,.29,1.99,1.61,0,.78),
    box(1.50,.40,1.78,.70,.84,1.08),box(1.50,1.40,1.78,1.62,.84,.98)],
    'KDEMI - Bois iroko huilé','Comptoir unique orienté nord-sud, machine café en partie sud et caisse en partie nord.',
    {'Usage':'Accueil et café par une personne','Emprise_principe':'x=1,35–2,00 m; y=0,20–1,70 m','Acces_staff':'Par le côté nord du comptoir','Passage_staff_nord_m':.76,'Passage_public_est_m':.91,'Hauteur_plan_travail_m':.84,'Statut':'Projet V7 sur emprise Space 02 V5 à relever','Hypothese':'Hauteur, prises, alimentations et dégagements à valider'},'DESK','KDEMI - Bois iroko huilé')
add('V7 — siège accueil face est - poste unique','IfcFurnishingElement',[
    box(.64,.85,1.03,1.40,.43,.49),
    box(.58,.90,.63,.96,0,.43),box(.98,.90,1.03,.96,0,.43),
    box(.58,1.29,.63,1.35,0,.43),box(.98,1.29,1.03,1.35,0,.43),
    box(.55,.85,.61,1.40,.43,1.05)],'KDEMI - Bois iroko huilé',
    'Assise à l’ouest du comptoir, dossier vers le mur ouest et personne face à l’est; la salle de réunion se trouve au nord et dans le champ gauche.',
    {'Orientation':'Dos ouest; face est','Emprise_principe':'x=0,55–1,10 m; y=0,85–1,40 m','Passage_vers_comptoir_m':.25,'Statut':'Projet V7 à relever','Acces_staff':'Par le côté nord du comptoir; non garanti par cette géométrie indicative'},'CHAIR','KDEMI - Bois iroko huilé')

# Coworking table and six real seats (four shared + one per individual desk).
add('V7 — table coworking 4 places ajustée','IfcFurnishingElement',[
    box(3.95,2.35,5.55,3.10,.74,.80),
    box(4.02,2.42,4.10,2.48,0,.74),box(5.40,2.42,5.48,2.48,0,.74),
    box(4.02,2.97,4.10,3.03,0,.74),box(5.40,2.97,5.48,3.03,0,.74)],
    'KDEMI - Bois iroko huilé','Table coworking quatre places; retrait du bord ouest pour conserver l’axe de passage vers la salle vitrée.',
    {'Capacite':'4 places avec sièges séparés','Emprise_principe':'x=3,95–5,55 m; y=2,35–3,10 m','Passage_ouest_m':.90,'Statut':'Projet V7 à relever','Poteau':'Dégagement avec poteau IFC 4351026 à contrôler'},'TABLE','KDEMI - Bois iroko huilé')

def chair_items(cx,cy,face):
    x0,x1=cx-.20,cx+.20;y0,y1=cy-.20,cy+.20
    items=[box(x0,y0,x1,y1,.43,.49)]
    for x in (x0+.03,x1-.08):
        for y in (y0+.03,y1-.08): items.append(box(x,y,x+.05,y+.05,0,.43))
    if face=='north': items.append(box(x0,y0,x1,y0+.045,.43,.95))
    elif face=='south': items.append(box(x0,y1-.045,x1,y1,.43,.95))
    elif face=='east': items.append(box(x0,y0,x0+.045,y1,.43,.95))
    else: items.append(box(x1-.045,y0,x1,y1,.43,.95))
    return items

for name,cx,cy,face in (
 ('V7 — siège coworking sud 1',4.30,2.15,'north'),('V7 — siège coworking sud 2',5.15,2.15,'north'),
 ('V7 — siège coworking nord 1',4.30,3.30,'south'),('V7 — siège coworking nord 2',5.15,3.30,'south')):
    add(name,'IfcFurnishingElement',chair_items(cx,cy,face),'KDEMI - Bois iroko huilé',
        'Siège individuel de 0,40 m environ autour de la table partagée.',
        {'Usage':'Coworking','Orientation':face,'Statut':'Projet V7 à relever'},'CHAIR','KDEMI - Bois iroko huilé')
for i,cx in enumerate((4.445,5.555),1):
    add(f'V7 — siège bureau individuel {i}','IfcFurnishingElement',chair_items(cx,.82,'north'),
        'KDEMI - Bois iroko huilé','Siège réel affecté à un poste de lecture individuel.',
        {'Usage':'Bureau individuel','Orientation':'Face au nord vers le plateau','Statut':'Projet V7 à relever; vérifier le flux d’entrée côté ouest'},'CHAIR','KDEMI - Bois iroko huilé')

# Straight replacement shelving against the west service wall, away from the main aisle.
west_shelves=[box(3.10,5.40,3.42,6.90,z,z+.035) for z in (.10,.50,.90,1.30,1.70,2.10)]
west_shelves += [box(3.10,5.40,3.13,6.90,.10,2.20),box(3.39,5.40,3.42,6.90,.10,2.20)]
add('V7 — rayonnage droit ouest du fond','IfcFurnishingElement',west_shelves,'KDEMI - Bois iroko huilé',
    'Rayonnage droit de relogement contre le mur de services, à l’écart de l’allée centrale et des portes.',
    {'Usage':'Rangement livres en fond de grande salle','Emprise_principe':'x=3,10–3,42 m; y=5,40–6,90 m; z=0–2,20 m',
     'Longueur_lineaire_m':1.50,'Nombre_tablettes':6,'Statut':'Projet V7 à relever; capacité à quantifier après calepinage des livres'},'SHELF','KDEMI - Bois iroko huilé')

# Lighting intent: simple linear warm-white elements for coordination, distinct from
# retained existing downlights. Exact power/positions/circuiting remain to be designed.
for name, geom, location in (
 ('V7 — intention lumière linéaire bibliothèque', [box(4.05,1.65,5.75,1.70,2.72,2.77)], 'Lecture / coworking'),
 ('V7 — intention lumière accueil', [box(1.45,.98,1.90,1.02,2.72,2.77)], 'Poste accueil-café'),
 ('V7 — intention lumière salle 03', [box(1.10,3.20,2.25,3.24,2.72,2.77)], 'Salle vitrée de réunion')):
    add(name,'IfcLightFixture',geom,'KDEMI - Lumière chaude 2700 K',
        f'Intention lumineuse V7 linéaire chaude pour {location}; à coordonner avec faux-plafond, alimentations et calcul éclairage.',
        {'Usage':location,'Statut':'Intention de projet à coordonner; pas une étude lumière','Température_couleur':'2700 K indicatif','Puissance':'À dimensionner','Coordination':'Faux-plafond, câblage, niveaux et photométrie à définir'},None,'KDEMI - Lumière chaude 2700 K')

# Put all V7 additions in an isolated, editable project group.
v7items=[p for p in f.by_type('IfcProduct') if (p.Name or '').startswith('V7 —')]
group=api('root.create_entity',f,ifc_class='IfcGroup',name='Projet V7 — aménagement rectiligne sur enveloppe V5 à relever')
group.Description='Éléments rectilignes V7 pour la cloison vitrée et son bandeau acoustique, accueil et traitement de façade. Enveloppes existantes non relevées; les hypothèses de réserve haute et terrasse restent distinctes.'
api('group.assign_group',f,products=v7items,group=group)
ps=api('pset.add_pset',f,product=group,name='KDEMI_Option_C_V7')
api('pset.edit_pset',f,pset=ps,properties={
 'Base_IFC':'DECIMO_ESQ_V6_OPTION_C.ifc','Perimetre':'Empreinte globale de l’enveloppe V5 conservée comme repère; façade de projet segmentée à nouveau en V7, murs latéraux conservés; relevé requis',
 'Modifications':'Cloison vitrée et porte avec bandeau acoustique fermé jusqu’à z=3,30 m entre Space 03/01; accueil longitudinal; suppression mobilier gênant Space 02 et relogement des niches courbes V5 en rayonnages droits au nord et au fond ouest; façade de proposition segmentée avec ouvertures rectangulaires, sans modifier les murs latéraux; intentions de lumière linéaire.',
 'Options_distinctes':'Plateforme haute et extension terrasse héritées de V6 restent des hypothèses séparées.'})

# Removing curved facade/niche coverings can leave empty IFC space-covering relations.
for rel in list(f.by_type('IfcRelCoversSpaces')):
    if not rel.RelatedCoverings: f.remove(rel)

f.header.file_name.name=OUT.name
OUT.parent.mkdir(parents=True,exist_ok=True);f.write(str(OUT))
print(OUT)
print('Produits IFC:',len(f.by_type('IfcProduct')),'| nouveaux V7:',len(v7items),'| espaces conservés:',len(f.by_type('IfcSpace')))
