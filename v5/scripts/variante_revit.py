"""Variante maillée de la V5 pour l'import Revit : v5/DECIMO_ESQ_V5_maille_Revit.ifc.

Chaque représentation « Body » est remplacée par des IfcTriangulatedFaceSet (repère local de l'objet,
centimètres comme le fichier source), un par matériau, stylés avec la couleur du matériau.
Les ouvertures sont déjà soustraites dans le maillage des murs : les IfcOpeningElement et les relations
IfcRelVoidsElement / IfcRelFillsElement sont retirés. GlobalId, noms, propriétés, espaces et
arborescence spatiale sont conservés. Revit importe ces objets comme formes non natives (DirectShape).
Usage : python3 v5/scripts/variante_revit.py
"""
import os, sys, logging
import numpy as np
import ifcopenshell, ifcopenshell.geom, ifcopenshell.util.unit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import V5_IFC, V5_REVIT  # noqa

logging.disable(logging.WARNING)


def main():
    f = ifcopenshell.open(V5_IFC)
    k = 1.0 / ifcopenshell.util.unit.calculate_unit_scale(f)  # m -> unité du fichier (cm)
    s = ifcopenshell.geom.settings()
    s.set("use-world-coords", False)
    ctx = next(c for c in f.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier == "Body")
    styles = {}

    def style(m):
        c = m.diffuse.components
        tr = float(m.transparency or 0.0)
        key = (m.name, round(c[0], 3), round(c[1], 3), round(c[2], 3), round(tr, 3))
        if key not in styles:
            rgb = f.createIfcColourRgb(None, *map(float, c))
            r = f.createIfcSurfaceStyleRendering(rgb, tr, None, None, None, None, None, None, "NOTDEFINED")
            styles[key] = f.createIfcSurfaceStyle(m.name or "Matériau", "BOTH", [r])
        return styles[key]

    n_prod, n_tri = 0, 0
    for p in list(f.by_type("IfcProduct")):
        if p.Representation is None or p.is_a("IfcOpeningElement") or p.is_a("IfcSpace"):
            continue
        reps = list(p.Representation.Representations)
        body = next((r for r in reps if r.RepresentationIdentifier == "Body"), None)
        if body is None:
            continue
        g = ifcopenshell.geom.create_shape(s, p, body).geometry
        v = np.array(g.verts, float).reshape(-1, 3) * k
        fc = np.array(g.faces, int).reshape(-1, 3)
        mids = np.array(g.material_ids, int)
        items = []
        for mi in (np.unique(mids) if len(mids) else [-1]):
            sel = fc[mids == mi] if mi >= 0 else fc
            used, inv = np.unique(sel, return_inverse=True)
            pts = f.createIfcCartesianPointList3D([tuple(map(float, q)) for q in np.round(v[used], 4)])
            fs = f.createIfcTriangulatedFaceSet(pts, None, True, [tuple(int(i) + 1 for i in t) for t in inv.reshape(-1, 3)], None)
            if mi >= 0:
                f.createIfcStyledItem(fs, [style(g.materials[mi])], None)
            items.append(fs)
            n_tri += len(sel)
        new = f.createIfcShapeRepresentation(ctx, "Body", "Tessellation", items)
        p.Representation.Representations = [new if r == body else r for r in reps]
        f.remove(body)
        n_prod += 1

    for rel in list(f.by_type("IfcRelFillsElement")) + list(f.by_type("IfcRelVoidsElement")):
        f.remove(rel)
    for o in list(f.by_type("IfcOpeningElement")):
        for inv in f.get_inverse(o):
            if inv.is_a("IfcRelContainedInSpatialStructure") or inv.is_a("IfcRelAggregates"):
                lst = [x for x in (inv.RelatedElements if hasattr(inv, "RelatedElements") else inv.RelatedObjects) if x != o]
                if lst:
                    setattr(inv, "RelatedElements" if hasattr(inv, "RelatedElements") else "RelatedObjects", lst)
                else:
                    f.remove(inv)
            elif inv.is_a("IfcRelDefinesByProperties"):
                lst = [x for x in inv.RelatedObjects if x != o]
                if lst:
                    inv.RelatedObjects = lst
                else:
                    f.remove(inv)
        pds = o.Representation
        f.remove(o)
        if pds is not None:
            for r in pds.Representations:
                f.remove(r)
            f.remove(pds)
    for la in f.by_type("IfcPresentationLayerAssignment"):
        if not la.AssignedItems:
            f.remove(la)
    for t in f.by_type("IfcTypeProduct"):
        if getattr(t, "RepresentationMaps", None):
            t.RepresentationMaps = None
    f.write(V5_REVIT)
    print(f"{V5_REVIT} : {n_prod} produits maillés, {n_tri} triangles, {len(styles)} styles")


if __name__ == "__main__":
    main()
