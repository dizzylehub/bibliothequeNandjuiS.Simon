"""Prépare DECIMO_ESQ_V5_Revit_editable.ifc : la V5 native (géométrie paramétrique conservée) avec les
corrections NON géométriques qui rendent l'import Revit plus propre et les éléments plus faciles à modifier.

Ne touche ni aux GlobalId, ni aux placements, ni aux représentations (contrôlé en fin de script).
Usage (racine du dépôt) : python3 v5/scripts/preparer_revit_editable.py
"""
import collections
import os
import sys

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element as E

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import RAPPORTS, V5, V5_IFC  # noqa: E402

SORTIE = os.path.join(V5, "DECIMO_ESQ_V5_Revit_editable.ifc")
f = ifcopenshell.open(V5_IFC)
journal = []


def log(msg):
    journal.append(msg)


def signature():
    s = {}
    for p in f.by_type("IfcProduct"):
        pl = p.ObjectPlacement
        s[p.GlobalId] = (pl.id() if pl else None, p.Representation.id() if p.Representation else None)
    return s


avant = signature()

# 1. Projet, site, bâtiment : noms exploitables (Revit affiche ces noms dans Info projet / Navigateur)
prj = f.by_type("IfcProject")[0]
prj.Name = "Bibliothèque Decimo - esquisse V5"
prj.LongName = "Bibliothèque Decimo - RDC sous logements, Abidjan"
site = f.by_type("IfcSite")[0]
site.Name = "Abidjan - site Decimo"
bat = f.by_type("IfcBuilding")[0]
bat.Name = "Decimo - RDC"
bat.CompositionType = "ELEMENT"
log("Projet, site, bâtiment nommés (Default / vide / titre V4-V2 périmés)")

# 2. Niveaux : bruit flottant sur la cote du RDC
for s in f.by_type("IfcBuildingStorey"):
    if s.Elevation is not None and abs(s.Elevation) < 1e-6:
        s.Elevation = 0.0
        log("Niveau %s : cote -1.9e-12 ramenée à 0" % s.Name)

# 3. PredefinedType manquants (Revit en déduit la sous-catégorie)
defauts = {"IfcWall": "STANDARD", "IfcWallStandardCase": "STANDARD", "IfcDoor": "DOOR", "IfcWindow": "WINDOW",
           "IfcBuildingElementProxy": "NOTDEFINED"}
n = 0
for cl, val in defauts.items():
    for p in f.by_type(cl, include_subtypes=False):
        if getattr(p, "PredefinedType", "x") is None:
            p.PredefinedType = val
            n += 1
log("%d PredefinedType renseignés (STANDARD / DOOR / WINDOW / NOTDEFINED)" % n)

# 4. Noms : les 60 génériques V4 portent leur ElementId Revit ; on ajoute matière et conserve l'id
n = 0
for p in f.by_type("IfcBuildingElementProxy"):
    if p.Name and p.Name.isdigit():
        m = E.get_material(p)
        mat = m.Name.replace("KDEMI - ", "") if m and m.is_a("IfcMaterial") else "sans matériau"
        p.Name = "Générique V4 - %s - %s" % (mat, p.Name)
        n += 1
log("%d génériques V4 renommés « Générique V4 - matériau - ElementId »" % n)
for p in f.by_type("IfcProduct"):
    if not p.Name:
        p.Name = "%s %s" % (p.is_a()[3:], p.GlobalId[:6])
        log("Produit sans nom : %s -> %s" % (p.GlobalId, p.Name))
f.by_type("IfcBuilding")[0].LongName = None

# 5. Types : un IfcTypeObject par famille (classe + ObjectType, sinon classe + nom) pour que Revit crée des
#    familles/types modifiables en une fois au lieu d'instances isolées. Aucune RepresentationMap ajoutée.
TYPES = {"IfcCovering": "IfcCoveringType", "IfcMember": "IfcMemberType", "IfcPlate": "IfcPlateType",
         "IfcSlab": "IfcSlabType", "IfcPipeSegment": "IfcPipeSegmentType", "IfcPump": "IfcPumpType",
         "IfcCableCarrierSegment": "IfcCableCarrierSegmentType", "IfcUnitaryEquipment": "IfcUnitaryEquipmentType",
         "IfcDoor": "IfcDoorType", "IfcWindow": "IfcWindowType", "IfcWall": "IfcWallType",
         "IfcFurniture": "IfcFurnitureType", "IfcFurnishingElement": "IfcFurnishingElementType",
         "IfcElectricDistributionBoard": "IfcElectricDistributionBoardType",
         "IfcProtectiveDevice": "IfcProtectiveDeviceType", "IfcJunctionBox": "IfcJunctionBoxType",
         "IfcCommunicationsAppliance": "IfcCommunicationsApplianceType"}
groupes = collections.defaultdict(list)
for cl in TYPES:
    for p in f.by_type(cl, include_subtypes=False):
        if not E.get_type(p):
            groupes[(cl, p.ObjectType or p.Name)].append(p)
for (cl, nom), elems in groupes.items():
    t = ifcopenshell.api.run("root.create_entity", f, ifc_class=TYPES[cl], name="ESQ - " + nom[:80])
    if hasattr(t, "PredefinedType"):
        t.PredefinedType = "NOTDEFINED"
    ifcopenshell.api.run("type.assign_type", f, related_objects=elems, relating_type=t)
log("%d IfcTypeObject créés pour %d éléments (familles Revit)" % (len(groupes), sum(map(len, groupes.values()))))

# 6. Matériaux : un matériau par élément sans matériau, d'après la classe (à affiner en APS)
MAT_DEFAUT = {"IfcSlab": "Béton armé", "IfcDoor": "Bois", "IfcFurniture": "Mobilier", "IfcFurnishingElement": "Mobilier"}
manquants = [p for p in f.by_type("IfcElement") if not E.get_material(p) and not p.is_a("IfcOpeningElement")]
mats = {}
for p in manquants:
    nom = MAT_DEFAUT.get(p.is_a(), "À définir")
    if nom not in mats:
        mats[nom] = ifcopenshell.api.run("material.add_material", f, name="ESQ - " + nom)
    ifcopenshell.api.run("material.assign_material", f, products=[p], material=mats[nom])
log("%d éléments sans matériau reçoivent un matériau de repli (%s)" % (len(manquants), ", ".join(mats)))

# 7. Hébergement : portes/fenêtres sans IfcRelFillsElement (Revit les importe alors sans mur hôte)
for d in f.by_type("IfcDoor") + f.by_type("IfcWindow"):
    if not d.FillsVoids:
        log("NON CORRIGÉ (géométrie V4 à ne pas toucher) : %s « %s » sans ouverture hôte" % (d.is_a(), d.Name))

# 8. Contrôle : GlobalId, placements et représentations strictement inchangés
apres = signature()
assert avant == apres, "la géométrie ou les placements ont changé"
f.write(SORTIE)
rapport = os.path.join(RAPPORTS, "preparation_revit_editable.txt")
with open(rapport, "w", encoding="utf-8") as fh:
    fh.write("Préparation Revit éditable - %s\n" % os.path.basename(SORTIE))
    fh.write("Contrôle : %d produits, GlobalId / placements / représentations identiques à la V5\n\n" % len(avant))
    fh.write("\n".join("- " + m for m in journal) + "\n")
print("\n".join(journal))
print("écrit", SORTIE)
