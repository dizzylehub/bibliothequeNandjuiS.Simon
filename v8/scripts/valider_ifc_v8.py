"""Contrôle de la maquette IFC V8 (Manadja) : schéma EXPRESS, géométrie, propriétés.

Usage : python3 v8/scripts/valider_ifc_v8.py  ->  v8/rapports/validation_ifc_v8.txt
"""
import hashlib
import logging
import os

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.validate
import ifcopenshell.util.element as ue

ICI = os.path.dirname(os.path.abspath(__file__))
IFC = os.path.join(ICI, "..", "NANDJUI_ESQ_V8.ifc")
RAP = os.path.join(ICI, "..", "rapports", "validation_ifc_v8.txt")

f = ifcopenshell.open(IFC)
lignes = [f"Fichier : NANDJUI_ESQ_V8.ifc · schéma {f.schema}",
          f"SHA-256 : {hashlib.sha256(open(IFC, 'rb').read()).hexdigest()}", ""]

log = ifcopenshell.validate.json_logger()
ifcopenshell.validate.validate(f, log, express_rules=True)
err = [m for m in log.statements if m.get("level", "").lower() in ("error", "critical")]
warn = [m for m in log.statements if m.get("level", "").lower() == "warning"]
lignes.append(f"Validation EXPRESS (règles incluses) : {len(err)} erreur(s), {len(warn)} avertissement(s)")
for m in err[:20]:
    lignes.append("  ERREUR " + str(m.get("message"))[:200])

s = ifcopenshell.geom.settings()
produits = [p for p in f.by_type("IfcProduct") if p.Representation and not p.is_a("IfcOpeningElement")]
ok, ko = 0, []
for p in produits:
    try:
        sh = ifcopenshell.geom.create_shape(s, p)
        if len(sh.geometry.verts) > 0:
            ok += 1
        else:
            ko.append(p.Name)
    except Exception as e:  # noqa: BLE001
        ko.append(f"{p.Name} ({e})")
lignes.append(f"Géométrie : {ok}/{len(produits)} représentations calculées")
for n in ko:
    lignes.append("  ÉCHEC " + str(n))

sans = [p.Name for p in produits if not p.is_a("IfcSpace") and "NANDJUI_V8" not in ue.get_psets(p)]
lignes.append(f"Objets sans jeu NANDJUI_V8 : {len(sans)}")
lignes.append(f"Ouvertures dans les murs : {len(f.by_type('IfcOpeningElement'))} IfcOpeningElement, {len(f.by_type('IfcRelFillsElement'))} remplies par une porte ou une fenêtre")
stat = {}
for p in produits:
    st = ue.get_psets(p).get("NANDJUI_V8", {}).get("Statut", "—")
    stat[st] = stat.get(st, 0) + 1
lignes.append("Répartition par statut : " + " ; ".join(f"{k} {v}" for k, v in sorted(stat.items())))
lignes.append("")
lignes.append("Espaces :")
for sp in f.by_type("IfcSpace"):
    q = ue.get_psets(sp).get("Qto_SpaceBaseQuantities", {})
    lignes.append(f"  {sp.Name} {sp.LongName} : {q.get('NetFloorArea')} m²")
lignes.append("")
lignes.append("Limites : la compatibilité Revit n'a pas été testée (logiciel non disponible ici).")
lignes.append("Les réseaux (câbles, tuyaux, gaines) ne sont pas modélisés : les plans T01 à T03 font référence ; seuls les équipements principaux sont repérés.")
lignes.append("Les hauteurs et la profondeur sont des hypothèses ; la maquette ne remplace pas un relevé.")
os.makedirs(os.path.dirname(RAP), exist_ok=True)
open(RAP, "w", encoding="utf-8").write("\n".join(lignes) + "\n")
print("\n".join(lignes))
