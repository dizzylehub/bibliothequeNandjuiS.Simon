"""Exporte la maquette IFC V8 en maillages triangulés avec le nom du matériau de chaque face,
pour les rendus réalistes Blender (v8/scripts/rendu_blender.py).

Usage : python3 v8/scripts/exporter_scene.py  ->  v8/rendus/scene_v8.npz
"""
import json
import os

import ifcopenshell
import ifcopenshell.geom
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
f = ifcopenshell.open(os.path.join(ICI, "..", "NANDJUI_ESQ_V8.ifc"))
reg = ifcopenshell.geom.settings()
reg.set("use-world-coords", True)

# l'itérateur nomme les matériaux d'après l'entité IfcSurfaceStyleShading : on remonte au nom du style
NOM_STYLE = {}
for st in f.by_type("IfcSurfaceStyle"):
    for sh in st.Styles:
        NOM_STYLE[f"{sh.is_a()}-{sh.id()}"] = st.Name

objets, V, T, M = [], [], [], []
noms_mat = []
for p in f.by_type("IfcProduct"):
    if not p.Representation or p.is_a("IfcSpace") or p.is_a("IfcOpeningElement"):
        continue
    g = ifcopenshell.geom.create_shape(reg, p).geometry
    v = np.array(g.verts, dtype=np.float32).reshape(-1, 3)
    t = np.array(g.faces, dtype=np.int32).reshape(-1, 3)
    mids = np.array(g.material_ids) if len(g.material_ids) else np.zeros(len(t), int)
    mats = [NOM_STYLE.get(m.name, m.name) for m in g.materials] or ["Défaut"]
    for m in mats:
        if m not in noms_mat:
            noms_mat.append(m)
    glob = np.array([noms_mat.index(mats[i] if 0 <= i < len(mats) else mats[0]) for i in mids], dtype=np.int32)
    objets.append(dict(nom=p.Name or p.is_a(), classe=p.is_a(), n_v=len(v), n_t=len(t)))
    V.append(v); T.append(t); M.append(glob)

sortie = os.path.join(ICI, "..", "rendus", "scene_v8.npz")
np.savez_compressed(sortie, V=np.concatenate(V), T=np.concatenate(T), M=np.concatenate(M),
                    objets=json.dumps(objets, ensure_ascii=False), materiaux=json.dumps(noms_mat, ensure_ascii=False))
print(sortie, len(objets), "objets", noms_mat)
