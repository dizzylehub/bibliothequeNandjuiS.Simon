"""Crée une variante IFC4 V6 Option C à partir de la V5 sans toucher à celle-ci.

Repère de conception : RDC 6,78 x 7,68 m; entrée au sud; pièces de service au nord-ouest.
Les nouveaux meubles et la réserve haute sont géométriquement modélisés. La géométrie
architecturale V5 (murs, vitrage, portes, réseaux, dalle, sanitaires) reste conservée;
les hypothèses de la réserve haute et du dallage terrasse sont identifiées par psets.
"""
from pathlib import Path
import ifcopenshell, ifcopenshell.api, ifcopenshell.guid
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'v5'/'DECIMO_ESQ_V5.ifc'
OUT=ROOT/'v6'/'DECIMO_ESQ_V6_OPTION_C.ifc'
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

def style(name):
    return next((s for s in f.by_type('IfcSurfaceStyle') if s.Name==name),None)
def color_items(items,style_name):
    st=style(style_name)
    if st:
        for it in items: f.createIfcStyledItem(it,[st],None)
    return items

def add(name,cls,items,material,color,description,props,predefined=None):
    p=api('root.create_entity',f,ifc_class=cls,name=name,predefined_type=predefined)
    p.OwnerHistory=OH; p.Description=description
    api('spatial.assign_container',f,products=[p],relating_structure=rdc)
    api('geometry.edit_object_placement',f,product=p,matrix=np.eye(4),is_si=True)
    color_items(items,color)
    rep=f.createIfcShapeRepresentation(body,'Body','SweptSolid',items)
    api('geometry.assign_representation',f,product=p,representation=rep)
    ps=api('pset.add_pset',f,product=p,name='KDEMI_Option_C_V6')
    api('pset.edit_pset',f,pset=ps,properties={'Indice':'V6 — proposition développée','Lot':material,'Statut':'Nouveau mobilier de projet',**props})
    if material:
        m=next((m for m in f.by_type('IfcMaterial') if m.Name==material),None)
        if m:
            f.createIfcRelAssociatesMaterial(ifcopenshell.guid.new(),OH,None,None,[p],m)
    return p

# Remove only furniture that the accepted A03 Option C replaces. Keep the fixed joinery,
# niches, banquette, wall board, panel enclosure, and all unrelated existing furniture.
# IfcFurniture is a subtype of IfcFurnishingElement, so IDs are deduplicated explicitly.
replace_ids={16035,36653,25484,25455,25461,25466,25477,16619,16768,16751,885,25629,25639}
for pid in sorted(replace_ids):
    p=f.by_id(pid)
    if p and p.is_a('IfcProduct'):
        api('root.remove_product',f,product=p)

# Update usage and limitation data on retained V5 spaces; no spatial geometry is moved.
space_info={
 '01':('Bibliothèque, rayonnages et coworking léger','V5 room envelope retained; furniture redesigned; verify clear routes on site.'),
 '02':('Accueil et café — poste unique','V5 zone near entrance re-used for combined reception and café service.'),
 '03':('Salle de réunion vitrée — zone bleue, usage confirmé','La cliente confirme l’usage réunion; l’emprise et le repérage de cet IfcSpace restent à confronter au relevé.'),
 '04':('Réserve / rangement arrière','V5 ground storage envelope retained; upper reserve is an indicative new object.'),
 '06':('Dégagement vers le WC — retour visuel en option','Emprise V5 conservée. Retour opaque de 0,03 m sur la rive de la cloison; largeur IFC indicative résiduelle 1,00 m, à relever et valider.'),
 '07':('WC existant au fond — à réaménager','Existing sanitary objects and connection geometry retained pending site check.'),
 '08':('Terrasse couverte existante','V5 roofed terrace retained; outside extension modeled as an option.'),
}
spaces={s.Name.split(' ',1)[0]:s for s in f.by_type('IfcSpace')}
for n,(long,status) in space_info.items():
    s=spaces.get(n)
    if not s: continue
    s.LongName=long; s.Description=status
    ps=api('pset.add_pset',f,product=s,name='KDEMI_Option_C_V6')
    api('pset.edit_pset',f,pset=ps,properties={'Usage_propose':long,'Statut_geometrie':'Emprise IFC V5 conservée; mobilier V6 modélisé','Hypothese':status})

# Reception/café joinery: continuous, plain worktop; operator seated against west wall,
# looking east to books; coffee machine and POS kept on the same accessible counter.
add('V6 — comptoir accueil-café intégré', 'IfcFurnishingElement',[
    box(.96,.20,2.75,.76,.78,.84), box(1.00,.22,1.08,.74,0,.78), box(2.63,.22,2.71,.74,0,.78),
    box(1.00,.68,2.71,.74,0,.78), box(1.00,.22,2.71,.28,0,.78), box(1.12,.30,1.52,.62,.84,1.10),
    box(1.68,.30,2.47,.62,.84,.93)],'KDEMI - Bois iroko huilé','#9A6B43',
    'Comptoir droit en modules de menuiserie, poste de permanence et café servis par une seule personne.',
    {'Fabrication':'Panneaux droits, chants protégés; dimensions de principe en mètres','Équipements':'Emplacements machine café et caisse esquissés','Hypothese':'Implantation à confirmer avec prises et alimentation eau éventuelle'},'DESK')

add('V6 — siège poste accueil-café','IfcFurnishingElement',[
    box(.21,.37,.58,.78,.43,.48),box(.24,.40,.29,.45,0,.43),box(.50,.40,.55,.45,0,.43),
    box(.24,.70,.29,.75,0,.43),box(.50,.70,.55,.75,0,.43),box(.20,.37,.25,.78,.43,.95),
    box(.20,.37,.58,.42,.90,.95)],'KDEMI - Bois iroko huilé','#9A6B43',
    'Assise du poste unique accueil-café, dossier tourné vers le mur ouest, personne face à l’est vers le comptoir et la bibliothèque.',
    {'Orientation':'Dos vers l’ouest; face vers l’est, comptoir unique à l’est','Dégagement':'0,38 m entre le siège et le bord du comptoir dans la géométrie de principe','Hypothese':'Relevé ergonomique à contrôler sur site'},'CHAIR')

# Six-place rectangular meeting table, with clear acrylic/glass partition inherited from V5.
table=[box(.52,3.32,2.45,4.16,.73,.79)]
for x in (.60,2.29):
    for y in (3.38,4.02): table.append(box(x,y,x+.08,y+.08,0,.73))
add('V6 — table de réunion 6 places','IfcFurnishingElement',table,'KDEMI - Bois iroko huilé','#9A6B43',
    'Table rectangulaire simple, six sièges envisagés dans la salle vitrée.',
    {'Capacite':'6 places envisagées; dégagements à mesurer','Dimensions':'1,93 x 0,84 m, hauteur 0,79 m (mobilier de principe)','Fabrication':'Plateau rectangulaire et piètements droits, fabrication locale'},'TABLE')
chairs=[]
for i,(x,y) in enumerate(((.75,3.02),(1.45,3.02),(2.15,3.02),(.75,4.38),(1.45,4.38),(2.15,4.38)),1):
    chair=[box(x-.18,y-.18,x+.18,y+.18,.43,.48),box(x-.17,y-.16,x-.12,y-.11,0,.43),box(x+.12,y-.16,x+.17,y-.11,0,.43),box(x-.17,y+.11,x-.12,y+.16,0,.43),box(x+.12,y+.11,x+.17,y+.16,0,.43)]
    chairs+=chair
add('V6 — 6 sièges salle de réunion','IfcFurnishingElement',chairs,'KDEMI - Bois iroko huilé','#9A6B43',
    'Six sièges individuels standardisés autour de la table de réunion.',
    {'Capacite':'Mobilier de principe; conserver les dégagements réglementaires après relevé'},'CHAIR')

# A03 Option C clears the central book tree and adds straight shelving in the NE corner.
# North niches remain; the new short run sits south of them. East V5 B01 modules are
# intentionally replaced by one longer straight run. Both runs stop clear of the fixed
# column (x=5.61..6.51, y=3.30..4.20) and the service/WC circulation.
def shelf_run(name, x0,y0,x1,y1, orientation, modules):
    h=2.05; items=[]
    items.append(box(x0,y0,x1,y1,0,.045))
    items.append(box(x0,y0,x1,y1,h-.045,h))
    for level in (.48,.96,1.44,1.92): items.append(box(x0,y0,x1,y1,level,level+.04))
    if orientation=='east':
        for j in range(modules+1):
            y=y0+j*(y1-y0)/modules
            items.append(box(x0,y-.022,x1,y+.022,.045,h-.045))
    else:
        for j in range(modules+1):
            x=x0+j*(x1-x0)/modules
            items.append(box(x-.022,y0,x+.022,y1,.045,h-.045))
    add(name,'IfcFurnishingElement',items,'KDEMI - Bois iroko huilé','#9A6B43',
        'Rayonnage droit ouvert, modules réguliers et tablettes horizontales; remplace une partie du rangement V5 et augmente le linéaire de livres.',
        {'Niveaux':5,'Modules':modules,'Hauteur_m':h,'Statut':'Implantation de principe Option C; relevé et ancrages à valider','Degagement':'À contrôler sur site; poteau et accès arrière conservés'},'SHELF')
shelf_run('V6 — rayonnage droit nord-est sous niches',3.28,6.70,6.08,6.96,'north',4)
shelf_run('V6 — rayonnage droit est prolongé',6.16,4.35,6.43,6.65,'east',4)

# Shared and individual light work points in the remaining library.
add('V6 — table coworking quatre places','IfcFurnishingElement',[
    box(4.03,2.35,5.73,3.12,.74,.80),box(4.10,2.42,4.18,2.56,0,.74),box(5.58,2.42,5.66,2.56,0,.74),
    box(4.10,2.91,4.18,3.05,0,.74),box(5.58,2.91,5.66,3.05,0,.74)],'KDEMI - Bois iroko huilé','#9A6B43',
    'Table partagée de quatre places, rectangulaire et réalisable en menuiserie standard.',
    {'Capacite':'4 postes','Dimensions':'1,70 x 0,77 m (mobilier indicatif)'},'TABLE')
for i,x in enumerate((4.12,5.23),1):
    add(f'V6 — poste de lecture individuel {i}','IfcFurnishingElement',[
        box(x,1.10,x+.65,1.52,.74,.79),box(x+.05,1.15,x+.12,1.22,0,.74),box(x+.53,1.15,x+.60,1.22,0,.74)],
        'KDEMI - Bois iroko huilé','#9A6B43','Petit poste individuel, table droite et compacte.',
        {'Usage':'Coworking / lecture','Dimensions':'0,65 x 0,62 m, mobilier indicatif'},'DESK')

# Short opaque WC privacy return attached to the east edge of the V5 corridor wall.
# It runs along the wall, not across the route: V5 clear width 1.03 m -> 1.00 m in IFC.
# Keep as a removable option pending door-swing, accessibility, and site checks.
add('V6 — retour opaque WC en option - à valider','IfcBuildingElementProxy',
    [box(2.88,5.32,2.91,5.80,0,1.85)],'KDEMI - Bois iroko huilé','#9A6B43',
    'Retour opaque court, accolé à la rive est de la cloison du dégagement pour masquer partiellement la vue vers le WC depuis la bibliothèque. Option démontable; ne traverse pas le dégagement.',
    {'Statut':'Option non bloquante à discuter et valider sur site','Emprise':'0,03 x 0,48 m, hauteur 1,85 m','Largeur_libre_IFC_m':1.00,'Base_calcul':'Dégagement IfcSpace 06 V5 = 1,03 m; retour placé le long de la rive','A_verifier':'Relevé des faces finies, porte et débattement, largeur réglementaire, visibilité depuis les points de vue et accessibilité'})

# Small rear upper reserve platform: explicit design proposal, not structural approval.
platform=[box(.48,4.20,2.76,4.92,2.08,2.18)]
for x in (.50,1.20,1.90,2.70): platform.append(box(x,4.21,x+.04,4.91,2.18,2.28))
for y in (4.23,4.55,4.87): platform.append(box(.50,y,2.72,y+.035,2.18,2.24))
add('V6 — plateforme réserve haute arrière - hypothèse','IfcSlab',platform,'KDEMI - Bois iroko huilé','#9A6B43',
    'Plateforme de rangement légère au-dessus de la partie arrière de la pièce bleue présumée (IfcSpace 03). Emprise et structure à confirmer; ne pas construire ni charger avant relevé et validation ingénieur.',
    {'Statut':'Hypothèse géométrique V6; non validée structurellement','Usage':'Réserve légère; accès non défini','Niveau':'+2,08 à +2,28 m de principe','Structure':'À dimensionner après relevé; aucune capacité de charge définie','Acces':'Échelle amovible à étudier; garde-corps, hauteur libre sous plateforme et évacuation à vérifier','Risques':'Capacité portante, chute, hauteur libre, incendie et accès; validation structure/sécurité requise'},'FLOOR')

# Outdoor extension is modeled as an alternative ground plane, not as a land title assertion.
patio=[box(.15,-3.78,6.35,-2.75,.005,.025)]
add('V6 — dallage extension terrasse - emprise optionnelle','IfcCovering',patio,'KDEMI - Grès cérame sable','#D8CCB6',
    'Zone de terrasse extérieure proposée au-delà de la terrasse couverte V5, jusqu’au chemin dallé visible en photo.',
    {'Statut':'Option de projet, limites foncières et niveau à vérifier','Surface_de_principe_m2':round(6.2*1.03,2),'Finis':'Dallage antidérapant extérieur; pente/évacuation à définir','Hypothese':'Géométrie illustrative fondée sur l’enveloppe V5 et non sur un levé topographique; recouvrement graphique du terrain V5 volontaire'},'FLOOR')

# Option group facilitates isolation/editing of all V6-only additions in IFC tools.
# Add a project group using the new element descriptions/ids recorded by the pset marker.
v6_elements=[e for e in f.by_type('IfcProduct') if e.Name and e.Name.startswith('V6 —')]
group=api('root.create_entity',f,ifc_class='IfcGroup',name='Option C V6 — mobilier, réserve, terrasse')
group.Description='Géométrie de projet modifiable; éléments de réserve haute et terrasse explicitement marqués comme hypothèses.'
api('group.assign_group',f,products=v6_elements,group=group)
ps=api('pset.add_pset',f,product=group,name='KDEMI_Option_C_V6')
api('pset.edit_pset',f,pset=ps,properties={'Base_IFC':'DECIMO_ESQ_V5.ifc','Modifications':'Accueil-café à poste unique, réunion 6 places, rayonnages droits nord/est, coworking; arbre à livres central supprimé; retour opaque WC optionnel, réserve haute et terrasse optionnelles.','Geometrie_existante':'Murs, ouvertures, réseaux et sanitaires V5 préservés.','Echelle':'Proposition de conception; cotes des hypothèses à vérifier sur site.'})

f.header.file_name.name=OUT.name
OUT.parent.mkdir(parents=True,exist_ok=True); f.write(str(OUT))
print(OUT)
print('IFC products',len(f.by_type('IfcProduct')),'new grouped',len(v6_elements),'spaces',len(f.by_type('IfcSpace')))
