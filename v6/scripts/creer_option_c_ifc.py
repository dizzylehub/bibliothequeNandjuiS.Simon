"""Crée un calque de programme Option C dans une copie de la maquette IFC V5.

La géométrie V5 n'est pas déplacée. Les affectations proposées et les réserves
liées au relevé sont consignées dans des propriétés IFC dédiées.
"""
from pathlib import Path
import ifcopenshell
import ifcopenshell.guid

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "v5" / "DECIMO_ESQ_V5.ifc"
OUTPUT = Path(__file__).resolve().parents[1] / "DECIMO_ESQ_V6_OPTION_C_PROVISOIRE.ifc"

f = ifcopenshell.open(str(SOURCE))
spaces = {s.Name.split(" ", 1)[0]: s for s in f.by_type("IfcSpace")}
owner = f.by_type("IfcOwnerHistory")[0]

intentions = {
    "01": {
        "Programme_propose": "Bibliothèque, rayonnages renforcés côté nord-est, coworking léger et lecture",
        "Statut_geometrie": "À reconfigurer après repérage photo; géométrie V5 conservée dans cette copie",
        "Point_de_controle": "Positionner l'accueil-café près de l'entrée et conserver une vue dégagée sur les rayonnages",
    },
    "03": {
        "Programme_propose": "Salle de réunion vitrée dans la pièce identifiée en bleu par la maîtrise d'ouvrage",
        "Statut_geometrie": "Emplacement V5 non confirmé comme étant la pièce bleue; volume et cloison V5 non déplacés",
        "Point_de_controle": "Recaler limites, porte et capacité sur les photos et le relevé du local",
    },
    "07": {
        "Programme_propose": "WC arrière à réaménager; mezzanine existante signalée par la maîtrise d'ouvrage à étudier comme réserve",
        "Statut_geometrie": "WC V5 conservé à sa position actuelle; mezzanine absente de l'IFC V5",
        "Point_de_controle": "Relever appareils, évacuations, niveaux, hauteur libre, accès et structure avant modélisation",
    },
    "08": {
        "Programme_propose": "Terrasse couverte conservée et terrasse extérieure à prolonger jusqu'au dallage après garde-corps",
        "Statut_geometrie": "Seule la terrasse couverte V5 est quantifiée; prolongement extérieur non modélisé",
        "Point_de_controle": "Relever garde-corps, limites, niveaux et état porteur du dallage",
    },
}

def prop(name, value):
    return f.createIfcPropertySingleValue(name, None, f.createIfcLabel(value), None)

for ref, values in intentions.items():
    space = spaces[ref]
    pset = f.createIfcPropertySet(
        ifcopenshell.guid.new(), owner, "KDEMI_Option_C_Provisoire", None,
        [prop(k, v) for k, v in values.items()]
    )
    f.createIfcRelDefinesByProperties(ifcopenshell.guid.new(), owner, None, None, [space], pset)

group = f.createIfcGroup(
    ifcopenshell.guid.new(), owner, "Option C — programme à intégrer après relevé",
    "Calque de conception provisoire. Géométrie issue de la V5 et inchangée.", "OPTION_C_PROVISOIRE"
)
f.createIfcRelAssignsToGroup(
    ifcopenshell.guid.new(), owner, "Espaces concernés par l'Option C", None,
    [spaces[x] for x in intentions], None, group
)
pset = f.createIfcPropertySet(
    ifcopenshell.guid.new(), owner, "KDEMI_Option_C_Statut", None,
    [prop("Indice", "V6 — variante de travail"),
     prop("Base_IFC", "v5/DECIMO_ESQ_V5.ifc"),
     prop("Nature", "Calque sémantique provisoire; aucune géométrie V5 modifiée"),
     prop("Source_des_intentions", "Consignes, croquis et photos de la maîtrise d'ouvrage"),
     prop("Photos_examinees", "45 photos du dépôt : 18 vues extérieures et 27 vues intérieures"),
     prop("Constat_visuel", "Pièce bleue allongée, porte et volume haut au fond; aucune cote fiable déduite des perspectives"),
     prop("Condition_de_developpement", "Calage géométrique après relevé coté et vérification de la structure du volume haut")]
)
f.createIfcRelDefinesByProperties(ifcopenshell.guid.new(), owner, None, None, [group], pset)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
f.write(str(OUTPUT))
print(OUTPUT)
