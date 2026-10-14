import sys, numpy as np, ifcopenshell, ifcopenshell.geom
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
f = ifcopenshell.open(sys.argv[1])
s = ifcopenshell.geom.settings(); s.set("use-world-coords", True)
it = ifcopenshell.geom.iterator(s, f); it.initialize()
SKIP = {"4350700", "4350705", "4350706", "4350742", "4350743", "4350744", "4350745", "4350698"}
data = []
while True:
    sh = it.get(); e = f.by_id(sh.id)
    if not e.is_a("IfcOpeningElement") and (e.Name or "").split(":")[-1] not in SKIP:
        v = np.array(sh.geometry.verts).reshape(-1, 3); t = np.array(sh.geometry.faces).reshape(-1, 3)
        mats = sh.geometry.materials; mid = np.array(sh.geometry.material_ids)
        cols = []
        for k in range(len(t)):
            m = mats[mid[k]] if len(mid) and mid[k] >= 0 else None
            c = (*m.diffuse.components, 1 - (m.transparency or 0)) if m is not None else (0.8, 0.8, 0.8, 1)
            cols.append(c)
        data.append((e, v, t, cols))
    if not it.next(): break
def view(ax, keep, elev, azim, xl, yl, zl, title):
    polys, cols = [], []
    for e, v, t, c in data:
        if not keep(e, v): continue
        tri = v[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
        L = np.array([-0.4, -0.7, 0.6]); L /= np.linalg.norm(L)
        sh = 0.62 + 0.38 * np.abs(n @ L)
        for k in range(len(tri)):
            cc = np.array(c[k]); cc[:3] = np.clip(cc[:3] * sh[k], 0, 1)
            polys.append(tri[k]); cols.append(cc)
    ax.add_collection3d(Poly3DCollection(polys, facecolors=cols, edgecolors="none"))
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_zlim(*zl)
    ax.set_box_aspect((xl[1] - xl[0], yl[1] - yl[0], zl[1] - zl[0])); ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off(); ax.set_title(title, fontsize=11)
fig = plt.figure(figsize=(18, 9))
a1 = fig.add_subplot(1, 2, 1, projection="3d")
view(a1, lambda e, v: v[:, 2].min() < 3.4, 12, -78, (-0.6, 7.0), (-3.2, 7.6), (0, 3.5), "Façade sud (depuis la rue)")
a2 = fig.add_subplot(1, 2, 2, projection="3d")
view(a2, lambda e, v: v[:, 2].min() < 3.25 and not (e.is_a("IfcWall") and v[:, 1].max() < 0.2) and v[:, 1].min() > -0.3
     and "Portail" not in (e.Name or "") and "Enseigne" not in (e.Name or "") and "Claustra" not in (e.Name or "")
     and "Vitrage" not in (e.Name or "") and "entrée cintrée" not in (e.Name or "") and not (v[:, 2].min() > 2.8 and v[:, 1].max() < 7.0 and "Arbre" not in (e.Name or "") and "Rail" not in (e.Name or "")),
     30, -62, (-0.2, 6.8), (-0.3, 7.6), (0, 3.4), "Intérieur (façade masquée) : arbre à livres et niches")
fig.tight_layout(); fig.savefig(sys.argv[2], dpi=110)
