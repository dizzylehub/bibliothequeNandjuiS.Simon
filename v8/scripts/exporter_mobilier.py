"""Exporte les volumes de chaque variante et de chaque assise (mobilier.py) en JSON,
pour les rendus studio Blender (rendu_mobilier_blender.py).

Usage : python3 v8/scripts/exporter_mobilier.py  ->  v8/rendus/mobilier_volumes.json
"""
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import mobilier as M  # noqa: E402
import mobilier_variantes as MV  # noqa: E402

pieces = {}
for p in MV.PLANCHES:
    for k, v in enumerate(p["variantes"]):
        pieces[f'VAR_{p["fichier"][:2]}_{"ABC"[k]}'] = v[1]()
for cle, f in (("M04", M.fauteuil), ("M05", M.chaise), ("M06", M.fauteuil_exterieur), ("M07", M.overallt)):
    pieces["REN_" + cle] = f()
sortie = os.path.join(ICI, "..", "rendus", "mobilier_volumes.json")
json.dump(pieces, open(sortie, "w", encoding="utf-8"), ensure_ascii=False)
print(sortie, len(pieces), "pièces", sorted({v[-1] if v[0] == "b" else v[3] for vol in pieces.values() for v in vol}))
