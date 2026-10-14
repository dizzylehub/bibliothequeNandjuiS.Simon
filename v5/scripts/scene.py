"""Maillage de la maquette V5 (coordonnées monde, mètres) avec couleurs matériaux, mis en cache.

Chaque produit -> dict(guid, classe, nom, v4, repere, items: [(verts, faces, rgba)]).
"""
import os, sys, pickle, hashlib, logging
import numpy as np
import ifcopenshell, ifcopenshell.geom
import ifcopenshell.util.element as ue

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import V4_IFC, V5_IFC, CACHE  # noqa

logging.disable(logging.WARNING)

CONTEXTE = {"4350698": "logements", "4350700": "voisin", "4350701": "fenetre_logt", "4350702": "fenetre_logt",
            "4350703": "fenetre_logt", "4350704": "fenetre_logt", "4350705": "sol_ext", "4350706": "trottoir",
            "4350742": "arbre", "4350743": "arbre", "4350744": "arbre", "4350745": "arbre"}
JOINTS = {str(t) for t in range(4350636, 4350658)}


def tag(name):
    return (name or "").split(":")[-1]


def charger(path=V5_IFC):
    h = hashlib.md5(open(path, "rb").read()).hexdigest()[:12]
    os.makedirs(CACHE, exist_ok=True)
    cpath = os.path.join(CACHE, f"scene_{os.path.basename(path)}_{h}.pkl")
    if os.path.exists(cpath):
        return pickle.load(open(cpath, "rb"))
    f = ifcopenshell.open(path)
    v4 = {p.GlobalId for p in ifcopenshell.open(V4_IFC).by_type("IfcProduct")}
    s = ifcopenshell.geom.settings()
    s.set("use-world-coords", True)
    out = []
    for p in f.by_type("IfcProduct"):
        if p.Representation is None or p.is_a("IfcOpeningElement") or p.is_a("IfcSpace"):
            continue
        reps = p.Representation.Representations
        rep = next((r for r in reps if r.RepresentationIdentifier == "Body"), None)
        if rep is None:
            continue
        g = ifcopenshell.geom.create_shape(s, p, rep).geometry
        v = np.array(g.verts, dtype=np.float64).reshape(-1, 3)
        fc = np.array(g.faces, dtype=np.int64).reshape(-1, 3)
        mids = np.array(g.material_ids, dtype=np.int64)
        iids = np.array(g.item_ids, dtype=np.int64)
        cols = []
        for m in g.materials:
            c = m.diffuse.components
            cols.append((c[0], c[1], c[2], 1.0 - (m.transparency or 0.0)))
        cols = np.array(cols or [(0.8, 0.8, 0.8, 1.0)])
        rgba = cols[np.clip(mids, 0, len(cols) - 1)] if len(mids) else np.tile(cols[0], (len(fc), 1))
        ps = ue.get_psets(p)
        items = []
        for k in np.unique(iids):
            sel = iids == k
            items.append((fc[sel], rgba[sel]))
        out.append(dict(guid=p.GlobalId, classe=p.is_a(), nom=p.Name or "", tag=tag(p.Name), v4=p.GlobalId in v4,
                        repere=ps.get("KDEMI_Esquisse", {}).get("Repere"), statut=ps.get("KDEMI_Existant", {}).get("Statut", ""),
                        ptype=getattr(p, "PredefinedType", None), verts=v, items=items,
                        lot=ps.get("KDEMI_Esquisse", {}).get("Lot", "")))
    pickle.dump(out, open(cpath, "wb"))
    return out


def role(e):
    """Rôle graphique d'un produit pour les dessins et les vues."""
    t, n, c = e["tag"], e["nom"], e["classe"]
    if t in CONTEXTE:
        return CONTEXTE[t]
    if t in JOINTS:
        return "joint"
    if e["statut"].startswith("Existant porteur") or c == "IfcSlab":
        return "structure"
    if c.startswith("IfcWall"):
        return "cloison"
    if c == "IfcCovering":
        if "plafond" in n.lower() or "Oculus" in n:
            return "plafond"
        if "sol" in n.lower():
            return "sol"
        return "revetement"
    if t in ("4350632", "4350634", "4350707"):
        return "sol"
    if c in ("IfcWindow",) or "Vitrage" in n:
        return "vitrage"
    if c in ("IfcLightFixture",):
        return "luminaire"
    if e["lot"].startswith("Technique") or c in ("IfcPipeSegment", "IfcCableCarrierSegment", "IfcUnitaryEquipment",
                                                  "IfcElectricDistributionBoard", "IfcPump", "IfcJunctionBox",
                                                  "IfcProtectiveDevice", "IfcCommunicationsAppliance"):
        return "technique"
    if c in ("IfcFurnishingElement", "IfcFurniture", "IfcFlowTerminal"):
        return "mobilier"
    return "autre"


def triangles(scene, keep=lambda e: True):
    """Concatène les triangles (n,3,3), couleurs (n,4), indices produit (n,) des produits retenus."""
    T, C, I = [], [], []
    for k, e in enumerate(scene):
        if not keep(e):
            continue
        for fc, rgba in e["items"]:
            T.append(e["verts"][fc]); C.append(rgba); I.append(np.full(len(fc), k))
    if not T:
        return np.zeros((0, 3, 3)), np.zeros((0, 4)), np.zeros(0, int)
    return np.concatenate(T), np.concatenate(C), np.concatenate(I)
