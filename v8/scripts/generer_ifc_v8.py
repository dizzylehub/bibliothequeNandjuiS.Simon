"""Maquette IFC4 V8 indice B (Manadja), construite sur la géométrie du plan E01.

Repère : X de gauche à droite vu depuis la terrasse, Y depuis la façade vers le fond (nord),
Z depuis le sol fini intérieur. Unités : mètre.

Chaque objet porte le jeu de propriétés NANDJUI_V8 :
  Statut  = Mesuré | Estimé | Proposé | Existant à démolir | Hypothèse à vérifier
  Source  = origine de la donnée
Les hauteurs (3,30 m sous dalle, 3,00 m sous plafond bois) sont des hypothèses héritées
de la V5, non relevées.

Usage : python3 v8/scripts/generer_ifc_v8.py  ->  v8/NANDJUI_ESQ_V8.ifc
"""
import os
import sys

import ifcopenshell
import ifcopenshell.api as api
import ifcopenshell.api.aggregate, ifcopenshell.api.context, ifcopenshell.api.geometry  # noqa: E401
import ifcopenshell.api.material, ifcopenshell.api.project, ifcopenshell.api.pset  # noqa: E401
import ifcopenshell.api.root, ifcopenshell.api.spatial, ifcopenshell.api.unit  # noqa: E401
import ifcopenshell.api.feature  # noqa: E401
import ifcopenshell.guid
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import plan_esquisse as G  # noqa: E402  (géométrie partagée avec le plan E01)

SORTIE = os.path.join(ICI, "..", "NANDJUI_ESQ_V8.ifc")

H_DALLE = 3.30          # hypothèse V5
H_PLAF = 3.00           # plafond en lames, proposé
EP = G.EP_EXT

f = ifcopenshell.api.project.create_file(version="IFC4")
projet = api.root.create_entity(f, ifc_class="IfcProject", name="Café-bibliothèque Nandjui · V8")
lm = api.unit.add_si_unit(f, unit_type="LENGTHUNIT")
am = api.unit.add_si_unit(f, unit_type="AREAUNIT")
vm = api.unit.add_si_unit(f, unit_type="VOLUMEUNIT")
api.unit.assign_unit(f, units=[lm, am, vm])
modele = api.context.add_context(f, context_type="Model")
body = api.context.add_context(f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=modele)

site = api.root.create_entity(f, ifc_class="IfcSite", name="Abidjan · résidence")
batiment = api.root.create_entity(f, ifc_class="IfcBuilding", name="Immeuble d'habitation · rez-de-chaussée")
rdc = api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="RDC · café-bibliothèque")
api.aggregate.assign_object(f, relating_object=projet, products=[site])
api.aggregate.assign_object(f, relating_object=site, products=[batiment])
api.aggregate.assign_object(f, relating_object=batiment, products=[rdc])
for o in (site, batiment, rdc):
    api.geometry.edit_object_placement(f, product=o, matrix=np.eye(4))
rdc.Elevation = 0.0

# ------------------------------------------------------------- styles et matériaux
COULEURS = {
    "Maçonnerie existante": ((0.80, 0.78, 0.74), 0.0),
    "Mur à démolir": ((0.85, 0.45, 0.30), 0.55),
    "Cloison neuve": ((0.93, 0.91, 0.87), 0.0),
    "Verre": ((0.55, 0.75, 0.82), 0.65),
    "Noyer": ((0.43, 0.26, 0.15), 0.0),
    "Velours cognac": ((0.66, 0.37, 0.17), 0.0),
    "Velours olive": ((0.34, 0.38, 0.23), 0.0),
    "Moutarde": ((0.79, 0.59, 0.18), 0.0),
    "Crème": ((0.94, 0.89, 0.80), 0.0),
    "Faïence blanche": ((0.97, 0.97, 0.96), 0.0),
    "Acier noir": ((0.12, 0.12, 0.12), 0.0),
    "Dallage terrasse": ((0.86, 0.83, 0.76), 0.0),
    "Sol intérieur": ((0.78, 0.70, 0.58), 0.0),
    "Béton": ((0.70, 0.70, 0.68), 0.0),
    "Claustra terre cuite": ((0.71, 0.38, 0.23), 0.0),
    "Végétal": ((0.30, 0.48, 0.28), 0.0),
}
MAT, STY = {}, {}
for nom, (rgb, tr) in COULEURS.items():
    m = api.material.add_material(f, name=nom)
    st = f.createIfcSurfaceStyle(nom, "BOTH", [f.createIfcSurfaceStyleShading(f.createIfcColourRgb(None, *rgb), tr)])
    MAT[nom], STY[nom] = m, st

D_Z = f.createIfcDirection((0.0, 0.0, 1.0))


def solide(x0, y0, x1, y1, z0, z1):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    prof = f.createIfcRectangleProfileDef("AREA", None,
                                          f.createIfcAxis2Placement2D(f.createIfcCartesianPoint(((x0 + x1) / 2, (y0 + y1) / 2)), None),
                                          x1 - x0, y1 - y0)
    return f.createIfcExtrudedAreaSolid(prof, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, float(z0))), None, None),
                                        D_Z, z1 - z0)


COMPTE = {}


def objet(classe, nom, boites, materiau, statut, source, predef=None, props=None, conteneur=None):
    p = api.root.create_entity(f, ifc_class=classe, name=nom, predefined_type=predef)
    api.spatial.assign_container(f, products=[p], relating_structure=conteneur or rdc)
    api.geometry.edit_object_placement(f, product=p, matrix=np.eye(4))
    items = [solide(*b) for b in boites]
    for it in items:
        f.createIfcStyledItem(it, [STY[materiau]], None)
    rep = f.createIfcShapeRepresentation(body, "Body", "SweptSolid", items)
    api.geometry.assign_representation(f, product=p, representation=rep)
    api.material.assign_material(f, products=[p], material=MAT[materiau])
    ps = api.pset.add_pset(f, product=p, name="NANDJUI_V8")
    api.pset.edit_pset(f, pset=ps, properties={"Statut": statut, "Source": source, "Indice": "V8-B", **(props or {})})
    COMPTE[classe] = COMPTE.get(classe, 0) + 1
    return p


def ouverture(mur, remplissage, boite):
    """Crée une IfcOpeningElement dans le mur et la remplit par la porte ou la fenêtre."""
    o = api.root.create_entity(f, ifc_class="IfcOpeningElement", name="Ouverture · " + (remplissage.Name or ""))
    api.geometry.edit_object_placement(f, product=o, matrix=np.eye(4))
    rep = f.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solide(*boite)])
    api.geometry.assign_representation(f, product=o, representation=rep)
    api.feature.add_feature(f, feature=o, element=mur)
    api.feature.add_filling(f, opening=o, element=remplissage)
    return o


def dims(p, larg, haut, op=None):
    p.OverallWidth, p.OverallHeight = float(larg), float(haut)
    if op and p.is_a("IfcDoor"):
        p.OperationType = op
    if p.is_a("IfcWindow"):
        p.PartitioningType = "SINGLE_PANEL"
    return p


MES, EST, PRO = "Mesuré", "Estimé", "Proposé"
CROQ = "Croquis de relevé du 14/10/2026 et précisions du 15/10"
PHOTO = "Estimation photos et proportions du croquis"
E01 = "Plan d'aménagement E01, esquisse V8"
HYP = "Hypothèse V5 non relevée"

X0, X1, PROF = 0.0, G.X_FIN, G.PROF

# ------------------------------------------------------------- enveloppe existante
LARG = "Largeur intérieure mesurée ; longueur (profondeur) estimée ; hauteur : " + HYP
objet("IfcWall", "Mur gauche existant", [(-EP, -EP, 0, PROF + EP, 0, H_DALLE)], "Maçonnerie existante", EST, LARG)
objet("IfcWall", "Mur droit existant", [(X1, -EP, X1 + EP, PROF + EP, 0, H_DALLE)], "Maçonnerie existante", EST, LARG)
mur_fond = objet("IfcWall", "Mur du fond existant", [(-EP, PROF, X1 + EP, PROF + EP, 0, H_DALLE)],
                 "Maçonnerie existante", EST, "Profondeur " + PHOTO)
baie = dims(objet("IfcWindow", "Baie haute du fond existante", [(4.50, PROF + 0.06, 5.30, PROF + 0.14, 2.20, 2.80)], "Verre", EST,
                  "Vue sur les photos de la grande salle ; dimensions estimées", predef="WINDOW"), 0.80, 0.60)
ouverture(mur_fond, baie, (4.50, PROF - 0.05, 5.30, PROF + EP + 0.05, 2.20, 2.80))
facade = objet("IfcWall", "Façade existante reprise", [(-EP, -EP, X1 + EP, 0, 0, H_DALLE)], "Maçonnerie existante", EST,
               "Largeur 6,75 m retenue ; baies redessinées en E01, à vérifier")
porte_entree = dims(objet("IfcDoor", "Grande porte d'entrée deux vantaux 1,60", [(3.6, -0.14, 5.2, -0.06, 0, 2.60)], "Verre", PRO,
                          "Largeur proposée, à vérifier sur la baie existante", predef="DOOR", props={"Ouverture": "Vers l'extérieur conseillée"}),
                    1.60, 2.60, "DOUBLE_DOOR_SINGLE_SWING")
ouverture(facade, porte_entree, (3.6, -EP - 0.05, 5.2, 0.05, 0, 2.60))
vitrine = dims(objet("IfcWindow", "Vitrine (ancienne porte)", [(0.6, -0.14, 2.4, -0.06, 0.45, 2.60)], "Verre", PRO, E01, predef="WINDOW"), 1.80, 2.15)
ouverture(facade, vitrine, (0.6, -EP - 0.05, 2.4, 0.05, 0.45, 2.60))
fen = dims(objet("IfcWindow", "Fenêtre de la banquette", [(5.6, -0.14, 6.4, -0.06, 0.45, 2.60)], "Verre", PRO, E01, predef="WINDOW"), 0.80, 2.15)
ouverture(facade, fen, (5.6, -EP - 0.05, 6.4, 0.05, 0.45, 2.60))
mur_wc = objet("IfcWall", "Mur séparatif bloc WC (conservé)", [(G.X_SEP0, G.Y_WC, G.X_SEP1, PROF, 0, H_DALLE)], "Maçonnerie existante", EST,
      "Épaisseur 0,15 estimée")
objet("IfcWall", "Mur séparatif à démolir", [(G.X_SEP0, 0, G.X_SEP1, G.Y_REU1, 0, H_DALLE)], "Mur à démolir", "Existant à démolir",
      "Brief du 15/10 ; avis structure obligatoire avant travaux", predef="NOTDEFINED", props={"Phase": "Démolition", "AvisStructure": "Requis"})
objet("IfcColumn", "Poteau 90 × 90 existant", [(G.POT[0], G.POT[1], G.POT[2], G.POT[3], 0, H_DALLE)], "Béton", MES, CROQ, predef="COLUMN")
objet("IfcSlab", "Dalle haute existante (sous-face supposée)", [(-EP, -EP, X1 + EP, PROF + EP, H_DALLE, H_DALLE + 0.20)], "Béton", "Hypothèse à vérifier",
      HYP, predef="ROOF")
objet("IfcSlab", "Sol intérieur refait", [(0, 0, X1, PROF, -0.08, 0)], "Sol intérieur", PRO, E01, predef="FLOOR")

# ------------------------------------------------------------- cloisons, vitrages, portes
cloison_wc = objet("IfcWall", "Cloison WC / salle de réunion", [(0, G.Y_REU1, G.X_SEP0, G.Y_WC, 0, 2.40)], "Cloison neuve", PRO, E01)
objet("IfcWall", "Cloison entre les deux WC", [(1.25, G.Y_WC, 1.35, PROF, 0, 2.40)], "Cloison neuve", PRO, E01)
objet("IfcSlab", "Plancher de la réserve haute au-dessus des WC", [(0, G.Y_REU1, G.X_SEP0, PROF, 2.40, 2.52)], "Cloison neuve",
      "Hypothèse à vérifier", "Volume haut visible sur photo ; appuis et charge non établis", predef="FLOOR")
objet("IfcCurtainWall", "Baie vitrée sud salle de réunion", [(0, G.Y_REU0 - 0.03, G.X_SEP1, G.Y_REU0 + 0.03, 0, 2.75)], "Verre", PRO, E01,
      props={"Vitrage": "Sécurité feuilleté, à dimensionner par le fabricant"})
objet("IfcCurtainWall", "Baie vitrée est salle de réunion", [(G.X_SEP0 + 0.04, G.Y_REU0, G.X_SEP0 + 0.10, 4.05, 0, 2.75)], "Verre", PRO, E01)
objet("IfcWall", "Imposte au-dessus des baies vitrées", [(0, G.Y_REU0 - 0.05, G.X_SEP1, G.Y_REU0 + 0.05, 2.75, H_PLAF),
                                                        (G.X_SEP0 + 0.02, G.Y_REU0, G.X_SEP0 + 0.12, G.Y_REU1, 2.75, H_PLAF)],
      "Cloison neuve", PRO, "Bandeau acoustique")
dims(objet("IfcDoor", "Porte vitrée salle de réunion 0,95", [(G.X_SEP0 + 0.04, 4.05, G.X_SEP0 + 0.10, 5.0, 0, 2.20)], "Verre", PRO, E01,
           predef="DOOR", props={"Ouverture": "Vers la bibliothèque"}), 0.95, 2.20, "SINGLE_SWING_RIGHT")
p_wcr = dims(objet("IfcDoor", "Porte WC réunion 0,80", [(0.25, G.Y_REU1 + 0.02, 1.05, G.Y_WC - 0.02, 0, 2.10)], "Noyer", PRO, E01,
                   predef="DOOR"), 0.80, 2.10, "SINGLE_SWING_LEFT")
ouverture(cloison_wc, p_wcr, (0.25, G.Y_REU1 - 0.05, 1.05, G.Y_WC + 0.05, 0, 2.10))
p_wcp = dims(objet("IfcDoor", "Porte coulissante WC public 0,90", [(G.X_SEP1, 5.40, G.X_SEP1 + 0.05, 6.40, 0, 2.10)], "Noyer", PRO, E01,
                   predef="DOOR", props={"Manoeuvre": "Coulissante en applique, vantail rangé vers le nord (y 6,40 à 7,30)"}),
             0.90, 2.10, "SLIDING_TO_LEFT")
ouverture(mur_wc, p_wcp, (G.X_SEP0 - 0.05, 5.45, G.X_SEP1 + 0.05, 6.35, 0, 2.10))
objet("IfcCovering", "Plafond en lames de noyer", [(0, 0, X1, G.Y_REU1, H_PLAF, H_PLAF + 0.03), (G.X_SEP1, G.Y_REU1, X1, PROF, H_PLAF, H_PLAF + 0.03)], "Noyer", PRO,
      "Plénum 0,30 pour éclairage et réseaux", predef="CEILING")

# ------------------------------------------------------------- sanitaires
for x, nom in ((0.62, "WC réunion"), (2.17, "WC public")):
    objet("IfcSanitaryTerminal", f"Cuvette suspendue {nom}", [(x - 0.19, PROF - 0.60, x + 0.19, PROF - 0.05, 0.25, 0.42),
                                                              (x - 0.25, PROF - 0.15, x + 0.25, PROF, 0, 1.10)],
          "Faïence blanche", PRO, E01, predef="TOILETPAN")
objet("IfcSanitaryTerminal", "Lave-mains WC réunion", [(0.05, 6.0, 0.35, 6.45, 0.80, 0.90)], "Faïence blanche", PRO, E01, predef="WASHHANDBASIN")
objet("IfcSanitaryTerminal", "Lave-mains WC public", [(2.65, 6.6, 2.95, 7.05, 0.80, 0.90)], "Faïence blanche", PRO, E01, predef="WASHHANDBASIN")
objet("IfcSanitaryTerminal", "Évier de l'arrière-bar", [(0.05, 1.45, 0.55, 1.85, 0.80, 0.90)], "Faïence blanche", PRO,
      "Proposé par Le Génie : à confirmer selon l'exploitation du café", predef="SINK")

# ------------------------------------------------------------- mobilier intérieur
F = "IfcFurniture"


def chaise(x, y, nom, mat="Noyer"):
    objet(F, nom, [(x - 0.22, y - 0.22, x + 0.22, y + 0.22, 0.42, 0.46), (x - 0.20, y - 0.20, x - 0.16, y - 0.16, 0, 0.42),
                   (x + 0.16, y - 0.20, x + 0.20, y - 0.16, 0, 0.42), (x - 0.20, y + 0.16, x - 0.16, y + 0.20, 0, 0.42),
                   (x + 0.16, y + 0.16, x + 0.20, y + 0.20, 0, 0.42)], mat, PRO, E01, predef="CHAIR")


def fauteuil(x, y, nom, mat, dos):
    dx0, dy0, dx1, dy1 = {"n": (-0.38, 0.22, 0.38, 0.38), "s": (-0.38, -0.38, 0.38, -0.22),
                          "e": (0.22, -0.38, 0.38, 0.38), "o": (-0.38, -0.38, -0.22, 0.38)}[dos]
    objet(F, nom, [(x - 0.38, y - 0.38, x + 0.38, y + 0.38, 0.18, 0.42), (x + dx0, y + dy0, x + dx1, y + dy1, 0.42, 0.85),
                   (x - 0.34, y - 0.34, x - 0.30, y - 0.30, 0, 0.18), (x + 0.30, y + 0.30, x + 0.34, y + 0.34, 0, 0.18)],
          mat, PRO, E01, predef="CHAIR", props={"Style": "Mid-century"})


def table(x0, y0, x1, y1, h, nom, mat="Noyer"):
    objet(F, nom, [(x0, y0, x1, y1, h - 0.04, h), (x0 + 0.05, y0 + 0.05, x0 + 0.10, y0 + 0.10, 0, h - 0.04),
                   (x1 - 0.10, y0 + 0.05, x1 - 0.05, y0 + 0.10, 0, h - 0.04), (x0 + 0.05, y1 - 0.10, x0 + 0.10, y1 - 0.05, 0, h - 0.04),
                   (x1 - 0.10, y1 - 0.10, x1 - 0.05, y1 - 0.05, 0, h - 0.04)], mat, PRO, E01, predef="TABLE")


# accueil-café
objet(F, "Arrière-bar avec évier et machine", [(0, 0.25, 0.62, 2.0, 0, 0.90), (0, 0.25, 0.35, 2.0, 1.45, 2.20)], "Noyer", PRO, E01)
objet(F, "Comptoir-enfilade d'accueil", [(1.55, 0.95, 2.20, 2.05, 0.10, 1.05), (1.60, 1.0, 1.65, 1.05, 0, 0.10), (2.10, 2.0, 2.15, 1.95, 0, 0.10)],
      "Noyer", PRO, E01, props={"HauteurPlan": 1.05})
chaise(1.15, 1.5, "Siège du poste d'accueil", "Velours cognac")
for y in (1.2, 1.8):
    objet(F, "Tabouret de comptoir", [(2.37, y - 0.18, 2.73, y + 0.18, 0.70, 0.76), (2.53, y - 0.02, 2.57, y + 0.02, 0, 0.70)],
          "Velours cognac", PRO, E01, predef="CHAIR")
# salle de réunion
objet(F, "Banquette de réunion 5 places le long de la baie sud", [(0.10, 2.33, 2.90, 2.83, 0, 0.45), (0.10, 2.33, 2.90, 2.45, 0.45, 0.90)],
      "Velours cognac", PRO, "Demande du 16/10 : maximum de places", props={"Places": 5})
table(0.25, 2.88, 2.75, 3.68, 0.75, "Table de réunion 2,50 × 0,80")
for x in (0.55, 1.18, 1.82, 2.45):
    chaise(x, 3.95, "Chaise de réunion")
objet(F, "Écran mural", [(0.0, 2.95, 0.04, 3.65, 1.0, 1.60)], "Acier noir", PRO, E01)
# mur de la collection
for nom, b in (("Rayonnage est avant", (X1 - 0.35, 0.25, X1, G.POT[1], 0, 2.90)),
               ("Rayonnage est arrière avec niches-vitrines", (X1 - 0.35, G.POT[3], X1, PROF - 0.35, 0, 2.90)),
               ("Rayonnage du fond", (G.X_SEP1 + 0.15, PROF - 0.35, X1, PROF, 0, 2.20))):
    x0, y0, x1, y1, z0, z1 = b
    bo = [(x0, y0, x1, y1, 0, 0.08)]
    n = 7
    for k in range(1, n + 1):
        z = z0 + (z1 - z0) * k / n
        bo.append((x0, y0, x1, y1, z - 0.025, z))
    if x1 - x0 < y1 - y0:
        for k in range(int((y1 - y0) / 0.8) + 1):
            yy = min(y0 + k * 0.8, y1 - 0.025)
            bo.append((x0, yy, x1, yy + 0.025, 0, z1))
        bo.append((x1 - 0.02, y0, x1, y1, 0, z1))
    else:
        for k in range(int((x1 - x0) / 0.8) + 1):
            xx = min(x0 + k * 0.8, x1 - 0.025)
            bo.append((xx, y0, xx + 0.025, y1, 0, z1))
        bo.append((x0, y1 - 0.02, x1, y1, 0, z1))
    objet(F, nom, bo, "Noyer", PRO, E01, predef="SHELF", props={"Lineaire": round(max(x1 - x0, y1 - y0), 2)})
objet(F, "Banquette de fenêtre", [(5.6, 0.0, 6.4, 0.5, 0, 0.45)], "Velours cognac", PRO, E01)
table(4.05, 1.80, 5.65, 2.70, 0.75, "Table d'hôtes 4 places")
for x in (4.45, 5.25):
    chaise(x, 1.48, "Chaise table d'hôtes")
    chaise(x, 3.02, "Chaise table d'hôtes")
objet(F, "Tablette de travail contre le poteau", [(G.POT[0] - 0.55, G.POT[1], G.POT[0], G.POT[3], 0.72, 0.76)], "Noyer", PRO, E01, predef="DESK")
for y in (3.52, 4.0):
    chaise(G.POT[0] - 0.85, y, "Chaise poste individuel")
for (x, y, d, m) in ((4.75, 5.05, "s", "Velours cognac"), (5.95, 5.05, "s", "Velours olive"),
                     (4.75, 6.30, "n", "Velours olive"), (5.95, 6.30, "n", "Velours cognac")):
    fauteuil(x, y, "Fauteuil de lecture", m, d)
table(5.03, 5.40, 5.67, 5.95, 0.40, "Table basse du salon")
objet("IfcCovering", "Tapis tissé du salon", [(4.25, 4.55, 6.35, 6.75, 0, 0.01)], "Moutarde", PRO, E01, predef="FLOORING")

# ------------------------------------------------------------- terrasse et pergola
TER = "Terrasse prolongée proposée ; emprise à autoriser"
objet("IfcSlab", "Dallage de la terrasse", [(G.X_TER0, G.Y_TER, G.X_TER1, 0, -0.15, -0.05)], "Dallage terrasse", PRO, TER, predef="FLOOR")
objet("IfcWall", "Claustra bas de limite (ouest)", [(G.X_TER0, G.Y_TER - 0.12, 3.40, G.Y_TER, -0.05, 0.85)], "Claustra terre cuite", PRO, TER)
objet("IfcWall", "Claustra bas de limite (est)", [(5.40, G.Y_TER - 0.12, G.X_TER1, G.Y_TER, -0.05, 0.85)], "Claustra terre cuite", PRO, TER)
objet("IfcWall", "Claustra bas latéraux", [(G.X_TER0, G.Y_TER, G.X_TER0 + 0.12, -0.3, -0.05, 0.85),
                                           (G.X_TER1 - 0.12, G.Y_TER, G.X_TER1, -0.3, -0.05, 0.85)], "Claustra terre cuite", PRO, TER)
objet("IfcDoor", "Portillon", [(3.40, G.Y_TER - 0.10, 4.40, G.Y_TER - 0.02, -0.05, 0.85)], "Acier noir", PRO, TER, predef="GATE")
H_PG = 2.90
for x in (-0.9, 1.25, 3.40, 5.55, 7.7):
    objet("IfcColumn", "Poteau de pergola acier 100 × 100", [(x - 0.05, -4.95, x + 0.05, -4.85, -0.05, H_PG)], "Acier noir", PRO,
          "Section indicative, à dimensionner (Le Génie)", predef="COLUMN")
for k in range(9):
    x = -0.9 + k * 8.6 / 8
    objet("IfcBeam", "Chevron de pergola", [(x - 0.04, -4.95, x + 0.04, -EP - 0.10, H_PG, H_PG + 0.20)], "Acier noir", PRO,
          "Entraxe 1,075 m ; section à dimensionner", predef="JOIST")
objet("IfcBeam", "Poutre de rive de pergola", [(-1.0, -4.98, 7.8, -4.82, H_PG, H_PG + 0.20)], "Acier noir", PRO, TER, predef="BEAM")
objet("IfcBeam", "Lisse d'appui contre la façade", [(-1.0, -EP - 0.10, 7.8, -EP, H_PG, H_PG + 0.20)], "Acier noir", PRO,
      "Scellement chimique, support à reconnaître ; accord de la copropriété", predef="BEAM")
lames = []
y = -4.8
while y < -0.35:
    lames.append((-0.9, y, 7.7, y + 0.045, H_PG + 0.20, H_PG + 0.295))
    y += 0.30
objet("IfcMember", "Lames de bois de la pergola", lames, "Noyer", PRO, "Lames 45 × 95 sur chant, entraxe 0,30 m ; bois classe 4 ou composite", predef="NOTDEFINED")
# salons extérieurs
objet(F, "Banquette extérieure en L (ouest)", [(-0.75, -4.6, -0.2, -1.0, -0.05, 0.42), (-0.75, -4.6, 2.6, -4.05, -0.05, 0.42),
                                               (-0.75, -4.6, -0.6, -1.0, 0.42, 0.80), (-0.75, -4.6, 2.6, -4.45, 0.42, 0.80)],
      "Crème", PRO, TER)
objet(F, "Banquette extérieure (est)", [(7.05, -4.6, 7.6, -1.2, -0.05, 0.42), (7.45, -4.6, 7.6, -1.2, 0.42, 0.80)], "Crème", PRO, TER)
table(0.4, -3.4, 1.6, -2.6, 0.38, "Table basse extérieure")
table(5.9, -3.2, 6.6, -2.5, 0.38, "Table basse extérieure")
for (x, y, d, m) in ((2.2, -2.3, "e", "Velours cognac"), (1.0, -1.7, "s", "Velours olive"),
                     (6.25, -1.9, "s", "Velours cognac"), (5.75, -3.9, "o", "Velours olive")):
    fauteuil(x, y, "Fauteuil bas d'extérieur", m, d)
for (x, y) in ((2.2, -3.3), (6.4, -4.2)):
    objet(F, "Pouf", [(x - 0.22, y - 0.22, x + 0.22, y + 0.22, -0.05, 0.40)], "Moutarde", PRO, TER)
for (x, y) in ((-0.55, -0.45), (7.4, -0.45), (2.9, -4.55)):
    objet(F, "Jardinière et plante", [(x - 0.22, y - 0.22, x + 0.22, y + 0.22, -0.05, 0.50)], "Claustra terre cuite", PRO, TER, predef="NOTDEFINED")
    objet("IfcGeographicElement", "Plante en pot", [(x - 0.30, y - 0.30, x + 0.30, y + 0.30, 0.50, 1.40)], "Végétal", PRO, TER)

# ------------------------------------------------------------- équipements techniques (repères des plans T01 à T03)
TEC = "Plans techniques T01 à T03 (Le Génie) ; puissances à confirmer"
objet("IfcElectricDistributionBoard", "Tableau divisionnaire", [(2.75, 0.0, 3.15, 0.15, 1.20, 1.90)], "Acier noir", PRO, TEC, predef="DISTRIBUTIONBOARD")
for nom, b in (("Split 18 000 BTU bibliothèque", (3.15, 6.6, 3.40, 7.3, 2.45, 2.80)),
               ("Split 12 000 BTU au-dessus de l'entrée", (4.0, 0.0, 4.8, 0.23, 2.62, 2.95)),
               ("Split 9 000 BTU salle de réunion", (0.0, 4.2, 0.25, 4.9, 2.45, 2.80))):
    objet("IfcUnitaryEquipment", nom, [b], "Crème", PRO, TEC, predef="SPLITSYSTEM")
for x in (0.4, 3.3, 6.2):
    objet("IfcUnitaryEquipment", "Groupe extérieur de climatisation", [(x - 0.40, PROF + EP + 0.02, x + 0.40, PROF + EP + 0.32, 0.30, 0.90)],
          "Crème", "Hypothèse à vérifier", "Mur nord : accès, bruit et accord de la copropriété à valider", predef="SPLITSYSTEM")
objet("IfcPump", "Pompe de relevage de l'évier", [(0.30, 1.0, 0.55, 1.35, 0.05, 0.40)], "Crème", PRO, TEC, predef="SUMPPUMP")

# ------------------------------------------------------------- espaces
ESPACES = (
    ("01", "Accueil-café ouvert", (0, 0, G.X_SEP0, G.Y_REU0)),
    ("02", "Salle de réunion (location)", (0, G.Y_REU0, G.X_SEP0, G.Y_REU1)),
    ("03", "WC réunion", (0, G.Y_WC, 1.25, PROF)),
    ("04", "WC public", (1.35, G.Y_WC, G.X_SEP0, PROF)),
    ("05", "Bibliothèque et salon de lecture", (G.X_SEP1, 0, X1, PROF)),
    ("06", "Terrasse couverte prolongée", (G.X_TER0, G.Y_TER, G.X_TER1, 0)),
)
SURF = {}
for num, nom, (x0, y0, x1, y1) in ESPACES:
    z0, z1 = (-0.05, H_PG) if num == "06" else (0, H_PLAF)
    sp = api.root.create_entity(f, ifc_class="IfcSpace", name=num, predefined_type="INTERNAL" if num != "06" else "EXTERNAL")
    sp.LongName = nom
    api.aggregate.assign_object(f, relating_object=rdc, products=[sp])
    api.geometry.edit_object_placement(f, product=sp, matrix=np.eye(4))
    if num == "05":
        poly = [(G.X_SEP0, 0), (X1, 0), (X1, G.POT[1]), (G.POT[0], G.POT[1]), (G.POT[0], G.POT[3]), (X1, G.POT[3]), (X1, PROF),
                (G.X_SEP1, PROF), (G.X_SEP1, G.Y_REU0), (G.X_SEP0, G.Y_REU0)]
        prof = f.createIfcArbitraryClosedProfileDef("AREA", None, f.createIfcPolyline([f.createIfcCartesianPoint(pt) for pt in poly + poly[:1]]))
        forme = f.createIfcExtrudedAreaSolid(prof, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None), D_Z, z1 - z0)
        surf = 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))))
    else:
        forme = solide(x0, y0, x1, y1, z0, z1)
        surf = (x1 - x0) * (y1 - y0)
    rep = f.createIfcShapeRepresentation(body, "Body", "SweptSolid", [forme])
    api.geometry.assign_representation(f, product=sp, representation=rep)
    SURF[nom] = surf
    q = api.pset.add_qto(f, product=sp, name="Qto_SpaceBaseQuantities")
    api.pset.edit_qto(f, qto=q, properties={"NetFloorArea": round(surf, 2), "Height": round(z1 - z0, 2)})
    ps = api.pset.add_pset(f, product=sp, name="NANDJUI_V8")
    api.pset.edit_pset(f, pset=ps, properties={"Statut": EST if num != "06" else PRO,
                                               "Source": "Surfaces calculées sur profondeur estimée 7,60 m" if num != "06" else TER,
                                               "Indice": "V8-B"})

f.write(SORTIE)
print(SORTIE)
for k, v in sorted(COMPTE.items()):
    print(f"  {k}: {v}")
for k, v in SURF.items():
    print(f"  {k}: {v:.2f} m²")
