"""Plan du RDC V4 — Bibliothèque Decimo : V3 + arbre à livres, niches cintrées, façade à claustra."""
import collections, sys
import numpy as np
import ifcopenshell, ifcopenshell.geom, ifcopenshell.util.element as ue
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon as MPoly, Arc, Rectangle, FancyArrowPatch
from matplotlib.collections import LineCollection
from shapely.geometry import Polygon, LineString, box, MultiPolygon
from shapely.ops import unary_union, polygonize

IFC = "/home/user/bibliothequeNandjuiS.Simon/DECIMO_ESQ_V2.ifc"
OUT = sys.argv[1]

sys.path.insert(0, "/tmp/claude-0/-home-user/5dfc2a2e-f67b-5d7c-bd12-e0811e213d4e/scratchpad")
from charte_kdemi import *
NOIR, GRIS, VERT, GCLAIR = ENCRE, TAUPE, TERRE_CUITE, SABLE_CLAIR
TAG, DEG = IROKO, OLIVE
H = 1.10                      # hauteur de coupe (m)
SCALE = 50                    # 1/50
XMIN, XMAX, YMIN, YMAX = -1.3, 7.3, -3.25, 8.05   # cadrage (m)

f = ifcopenshell.open(IFC)
rdc = next(s for s in f.by_type("IfcBuildingStorey") if "RDC" in s.Name)
s = ifcopenshell.geom.settings(); s.set("use-world-coords", True)
it = ifcopenshell.geom.iterator(s, f); it.initialize()

meshes = {}
while True:
    sh = it.get()
    v = np.array(sh.geometry.verts).reshape(-1, 3)
    t = np.array(sh.geometry.faces).reshape(-1, 3)
    el = f.by_id(sh.id)
    if ue.get_container(el) == rdc:
        meshes[sh.id] = (el, v, t)
    if not it.next():
        break

def section(v, t, h):
    segs = []
    for tri in v[t]:
        z = tri[:, 2] - h
        pts = []
        for i in range(3):
            a, b = tri[i], tri[(i + 1) % 3]
            za, zb = z[i], z[(i + 1) % 3]
            if (za < 0) != (zb < 0):
                k = za / (za - zb)
                pts.append(a[:2] + k * (b[:2] - a[:2]))
        if len(pts) == 2 and np.linalg.norm(pts[0] - pts[1]) > 1e-6:
            segs.append(LineString([tuple(np.round(p, 5)) for p in pts]))
    if not segs:
        return None
    polys = list(polygonize(unary_union(segs)))
    return unary_union(polys) if polys else None

def footprint(v, t):
    tris = [Polygon(p[:, :2]) for p in v[t]]
    tris = [p.buffer(1e-4) for p in tris if p.area > 1e-8]
    return unary_union(tris).buffer(-1e-4) if tris else None

def feature_edges(v, t, angle=25, up_only=True):
    tri = v[t]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
    vk = np.round(v, 4)
    key = lambda i: tuple(vk[i])
    edges = collections.defaultdict(list)
    for fi, (a, b, c) in enumerate(t):
        for p, q in ((a, b), (b, c), (c, a)):
            edges[tuple(sorted((key(p), key(q))))].append(fi)
    out = []
    cos = np.cos(np.radians(angle))
    for (p, q), fs in edges.items():
        if len(fs) == 2 and np.dot(n[fs[0]], n[fs[1]]) > cos:
            continue
        if up_only and all(abs(n[x][2]) < 0.2 for x in fs):
            continue
        if np.hypot(p[0] - q[0], p[1] - q[1]) < 1e-3:
            continue
        out.append([(p[0], p[1]), (q[0], q[1])])
    return out

def draw_geom(ax, g, **kw):
    if g is None or g.is_empty:
        return
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon":
            continue
        ax.add_patch(MPoly(np.array(p.exterior.coords), closed=True, **kw))
        for r in p.interiors:
            ax.add_patch(MPoly(np.array(r.coords), closed=True, fc="white",
                               ec=kw.get("ec", NOIR), lw=kw.get("lw", .3), zorder=kw.get("zorder", 1)))

def outline(ax, g, **kw):
    if g is None or g.is_empty:
        return
    for p in getattr(g, "geoms", [g]):
        if p.geom_type == "Polygon":
            ax.plot(*p.exterior.xy, **kw)
            for r in p.interiors:
                ax.plot(*r.xy, **kw)


def tag_of(e):
    return (e.Name or "").split(":")[-1]

def moved(v, dx=0.0, dy=0.0, rot=0.0, about=None):
    v = v.copy()
    if rot:
        c = np.array(about if about is not None else v[:, :2].mean(0))
        a = np.radians(rot)
        R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        v[:, :2] = (v[:, :2] - c) @ R.T + c
    v[:, 0] += dx; v[:, 1] += dy
    return v

# --- modifications V3 (annotations du 14/10/2026) ---------------------------
REMOVE = {
    "4350624", "4350627", "4350628",          # WC 1 et son lave-mains : un seul WC
    "4350622", "4350623",                     # portes des anciens WC 1 et WC 2
    "4350611", "4350610", "4350617",          # porte vitrée et vitrage haut de la salle de réunion
    "4350676",                                # console vinyles M01 déplacée contre la cloison
    "4350662",                                # rayonnage remplacé par une plante
    *[str(i) for i in range(4350712, 4350732)],  # anciennes lames de pergola
    # --- V4 ---
    "4350680", "4350681", "4350682", "4350683", "4350684", "4350685",   # bureau du fond + 3 chaises -> niches
    "4350661", "4350665",                     # rayonnages : zone agent du comptoir / devant la niche est
    "4350596", "4350597", "4350598", "4350599", "4350600", "4350601",   # baies de façade remplacées
    "4350602", "4350603", "4350604",
    "4350686", "4350691", "4350689", "4350690", "4350694", "4350695",   # rails lumineux raccourcis (canopée)
}
MOVE = {
    "4350673": dict(dx=1.76, dy=0.14), "4350674": dict(dx=1.76, dy=0.14),  # comptoir d'accueil
    "4350675": dict(dx=1.76, dy=0.14),
    # V4 : salon de lecture recentré, groupe terrasse décalé pour libérer l'axe d'entrée
    "4350677": dict(dx=0.07, dy=-0.26), "4350679": dict(dx=0.07, dy=-0.45), "4350678": dict(dx=0.07, dy=-0.56),
    "4350739": dict(dx=1.0), "4350740": dict(dx=1.0), "4350741": dict(dx=1.0),
}
# lave-mains du WC unique : pivoté contre le mur est (ancienne porte du WC 2 condamnée)
SINK_C = (1.575, 6.72)
for k in ("4350630", "4350631"):
    MOVE[k] = dict(rot=90, about=SINK_C, dx=2.72 - SINK_C[0], dy=6.86 - SINK_C[1])

# baies de façade V4 (x en m) : A et B coin lecture, D entrée, C accueil
A_X0, A_X1 = 0.55, 1.75
B_X0, B_X1 = 2.00, 2.70
D_X0, D_X1 = 3.35, 4.85
C_X0, C_X1 = 5.15, 6.25
WALL_EDIT = {   # tag : (ajouts, retraits) en boîtes (x0, y0, x1, y1)
    "4350608": ([(2.91, 6.40, 3.09, 7.39)], [(2.88, 5.30, 3.12, 6.14)]),   # porte WC 2 bouchée, baie vers dégagement
    "4350621": ([(1.80, 5.04, 2.79, 5.16)], []),                            # porte WC 1 bouchée
    "4350620": ([], [(1.90, 6.22, 2.83, 6.38)]),                            # nouvelle porte du WC
    "4350590": ([(0.85, -0.09, 1.90, 0.09), (3.85, -0.09, 5.75, 0.09)],     # façade : anciennes baies refermées
                [(A_X0, -0.1, A_X1, 0.1), (B_X0, -0.1, B_X1, 0.1), (D_X0, -0.1, D_X1, 0.1), (C_X0, -0.1, C_X1, 0.1)]),
}
NEW_WALLS = [
    box(1.76, 5.16, 1.88, 6.24).difference(box(1.74, 5.32, 1.90, 6.08)),  # cloison rangement / dégagement
    box(2.955, 2.82, 3.045, 4.07), box(2.955, 5.00, 3.045, 5.04),                                         # cloison pleine (dos du M01)
]
POCKET = box(3.09, 0.09, 3.23, 0.99)                                       # caisson de la porte à galandage

f_ = None
# --- figure A3 paysage ------------------------------------------------------
MM = 1 / 25.4
fig = plt.figure(figsize=(420 * MM, 297 * MM))
W_mm = (XMAX - XMIN) * 1000 / SCALE
H_mm = (YMAX - YMIN) * 1000 / SCALE
left_mm, bot_mm = 22, (297 - H_mm) / 2 - 4
ax = fig.add_axes([left_mm / 420, bot_mm / 297, W_mm / 420, H_mm / 297])
ax.set_xlim(XMIN, XMAX); ax.set_ylim(YMIN, YMAX); ax.set_aspect("equal"); ax.axis("off")
frame = box(XMIN, YMIN, XMAX, YMAX)
lw_cut, lw_mid, lw_fine, lw_hair = 1.1, 0.45, 0.25, 0.15
POCHE = POCHE
BOIS = "#B9A07E"   # bois des lames (couleur de projet, usage limité aux lames)

walls = {}
for eid, (e, v, t) in meshes.items():
    if e.is_a("IfcWall") or e.is_a("IfcWallStandardCase"):
        g = section(v, t, H)
        add, sub = WALL_EDIT.get(tag_of(e), ([], []))
        g = unary_union([g] + [box(*b) for b in add])
        for b in sub:
            g = g.difference(box(*b))
        walls[tag_of(e)] = g
walls_u = unary_union(list(walls.values()) + NEW_WALLS)

# Carrelage 60 x 60 (lignes du modèle)
interior = box(0.09, 0.09, 6.51, 7.41)
for eid, (e, v, t) in meshes.items():
    if e.is_a("IfcBuildingElementProxy") and np.ptp(v[:, 2]) < 0.02 and \
       (np.ptp(v[:, 0]) < 0.02 or np.ptp(v[:, 1]) < 0.02):
        ls = LineString([tuple(v[:, :2].min(0)), tuple(v[:, :2].max(0))]).intersection(interior.difference(walls_u))
        for g in getattr(ls, "geoms", [ls]):
            if not g.is_empty:
                ax.plot(*g.xy, color="#B8BEC2", lw=0.3, zorder=0)

for g in list(walls.values()) + NEW_WALLS:
    draw_geom(ax, g, fc=POCHE, ec=NOIR, lw=lw_mid, zorder=4)

GLASS = {"4350609"}
SKIP = {"4350632", "4350705", "4350742", "4350743", "4350744", "4350745", "4350634"}
TAGS = {}

for eid, (e, v, t) in meshes.items():
    name, tg = e.Name or "", tag_of(e)
    if e.is_a("IfcOpeningElement") or e.is_a("IfcWall") or tg in SKIP or tg in REMOVE:
        continue
    if tg in MOVE:
        v = moved(v, **MOVE[tg])
    zmin, zmax = v[:, 2].min(), v[:, 2].max()
    if e.is_a("IfcBuildingElementProxy") and np.ptp(v[:, 2]) < 0.02 and \
       (np.ptp(v[:, 0]) < 0.02 or np.ptp(v[:, 1]) < 0.02):
        continue
    if tg == "4350700":   # bâtiment mitoyen
        g = footprint(v, t).intersection(frame)
        draw_geom(ax, g, fc="white", ec=GRIS, lw=lw_fine, hatch="////", zorder=0)
        ax.text(g.centroid.x, 3.6, "BÂTIMENT\nMITOYEN", rotation=90, ha="center", va="center",
                fontsize=6.5, color=GRIS, zorder=5, bbox=dict(fc="white", ec="none", pad=1.5))
        continue
    if tg in GLASS:
        draw_geom(ax, footprint(v, t), fc="#DCEBF0", ec=NOIR, lw=lw_mid, zorder=4)
        continue
    if tg == "4350707":
        outline(ax, footprint(v, t).intersection(frame), color=NOIR, lw=lw_mid, zorder=2)
        continue
    if tg == "4350706":
        outline(ax, footprint(v, t).intersection(frame), color=GRIS, lw=lw_fine, zorder=2)
        continue
    if zmin > H:
        outline(ax, footprint(v, t), color=GRIS, lw=lw_hair, ls=(0, (3, 2)), zorder=6)
        continue
    furn = e.is_a("IfcFurnishingElement") or e.is_a("IfcFlowTerminal") or e.is_a("IfcDoor")
    if zmax > H and not furn and zmin < 0.05:
        draw_geom(ax, section(v, t, H) or footprint(v, t), fc=POCHE, ec=NOIR, lw=lw_mid, zorder=4)
        continue
    g = footprint(v, t)
    lw = lw_cut * .55 if (zmax > H and furn) else lw_fine
    draw_geom(ax, g, fc="white", ec=NOIR, lw=lw, zorder=3)
    ed = feature_edges(v, t)
    if ed:
        ax.add_collection(LineCollection(ed, colors=NOIR, lw=lw_hair, zorder=3))
    if e.is_a("IfcFurnishingElement"):
        tp = ue.get_type(e)
        code = (tp.Name if tp else name).split(":")[0].replace("DECIMO_", "").split("_")[0]
        TAGS.setdefault(code, []).append(g.centroid)

# --- nouveaux éléments dessinés ---------------------------------------------
from shapely.geometry import Point
def rect(x0, y0, x1, y1, **kw):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, **kw))

# M01 — console vinyles 40 cm contre la cloison (3 modules, 2 platines)
for i, (y0, y1) in enumerate([(1.86, 2.58), (2.58, 3.30), (3.30, 4.02)]):
    rect(3.09, y0, 3.49, y1, fc="white", ec=NOIR, lw=lw_cut * .55, zorder=5)
    if i:
        ax.add_patch(plt.Circle((3.29, (y0 + y1) / 2), 0.15, fc="white", ec=NOIR, lw=lw_fine, zorder=5))
        ax.add_patch(plt.Circle((3.29, (y0 + y1) / 2), 0.02, fc=NOIR, ec="none", zorder=5))
TAGS.setdefault("M01", []).append(Point(3.29, 2.23))

# Tableau mural de la salle de réunion
rect(0.09, 2.95, 0.14, 4.75, fc=VERT, ec=NOIR, lw=lw_fine, zorder=5)
ax.text(0.24, 3.85, "TABLEAU", rotation=90, fontsize=5.2, color=GRIS, ha="center", va="center", zorder=8)

# Pouf du coin lecture
ax.add_patch(plt.Circle((2.27, 1.18), 0.22, fc="white", ec=NOIR, lw=lw_fine * 1.6, zorder=5))
ax.add_patch(plt.Circle((2.27, 1.18), 0.17, fc="none", ec=NOIR, lw=lw_hair, zorder=5))
TAGS.setdefault("P01", []).append(Point(2.27, 1.18))

# Plante (remplace un rayonnage)
pc = np.array([6.18, 2.85])
for a in np.linspace(0, 360, 9)[:-1] + 12:
    r = np.radians(a)
    tip = pc + 0.32 * np.array([np.cos(r), np.sin(r)])
    mid = pc + 0.2 * np.array([np.cos(r), np.sin(r)])
    nrm = 0.07 * np.array([-np.sin(r), np.cos(r)])
    ax.add_patch(MPoly([pc, mid + nrm, tip, mid - nrm], closed=True, fc="white", ec=NOIR, lw=lw_hair, zorder=5))
ax.add_patch(plt.Circle(pc, 0.16, fc="white", ec=NOIR, lw=lw_fine, zorder=5))
TAGS.setdefault("V01", []).append(Point(*pc))

# Caisson de la porte à galandage (coin lecture / salle de lecture)
draw_geom(ax, POCKET, fc="#9AA3A8", ec=NOIR, lw=lw_mid, zorder=4)
ax.plot([3.16, 3.16], [0.13, 0.97], color=NOIR, lw=lw_mid * 1.6, zorder=6)
ax.plot([3.16, 3.16], [0.99, 1.84], color=NOIR, lw=lw_fine, ls=(0, (3, 2)), zorder=6)
ax.add_patch(FancyArrowPatch((3.36, 1.55), (3.36, 1.05), arrowstyle="-|>", mutation_scale=6, color=NOIR, lw=.4, zorder=6))
ax.text(3.33, 0.55, "GALANDAGE", rotation=90, fontsize=4.6, color=GRIS, ha="center", va="center", zorder=8)

# Portes (débattements)
def door(hinge, r, a0, a1, leaf_end):
    ax.add_patch(Arc(hinge, 2 * r, 2 * r, theta1=a0, theta2=a1, color=NOIR, lw=lw_hair, zorder=6))
    ax.plot([hinge[0], leaf_end[0]], [hinge[1], leaf_end[1]], color=NOIR, lw=lw_mid, zorder=6)
door((2.83, 6.30), 0.93, 180, 270, (2.83, 5.37))       # WC, ouvrant vers le dégagement
door((3.00, 5.00), 0.93, 180, 270, (2.07, 5.00))       # salle de réunion (déplacée)
# porte coulissante du rangement
rect(1.90, 5.30, 1.93, 6.10, fc="white", ec=NOIR, lw=lw_mid, zorder=6)


# =============================== V4 =========================================
TERRA, TERRA_F, IROKO, ENDUIT = "#B4583E", "#8E3F2B", "#9A6B43", "#E6D6BF"

def spacing(x, attractors, smin, smax, reach):
    d = min(abs(x - a) for a in attractors)
    return smin + (smax - smin) * (1 - np.exp(-(d / reach) ** 2))

def claustra_plan(x0, x1):
    """Baie cintrée : vitrage en retrait + claustra terre cuite au nu extérieur."""
    rect(x0, -0.09, x1, -0.03, fc=TERRA, ec=NOIR, lw=lw_fine, zorder=5)
    for xx in np.arange(x0 + 0.06, x1 - 0.02, 0.12):
        ax.add_patch(plt.Circle((xx, -0.06), 0.022, fc="white", ec="none", zorder=5))
    rect(x0, 0.0, x1, 0.025, fc="#DCEBF0", ec=NOIR, lw=lw_fine, zorder=5)

claustra_plan(A_X0, A_X1)
claustra_plan(B_X0, B_X1)
claustra_plan(C_X0, C_X1)

# Entrée principale : portail terre cuite + double porte vitrée cintrée (0,90 + 0,60) ouvrant vers l'extérieur
for x0, x1 in ((D_X0 - 0.15, D_X0), (D_X1, D_X1 + 0.15)):
    rect(x0, -0.21, x1, -0.09, fc=TERRA, ec=NOIR, lw=lw_mid, zorder=5)
for xx in (D_X0, D_X1):
    rect(xx - 0.025 if xx == D_X1 else xx, -0.03, xx + (0.0 if xx == D_X1 else 0.025), 0.03, fc=NOIR, ec=NOIR, lw=.2, zorder=6)
door((D_X0, -0.03), 0.90, 270, 360, (D_X0, -0.93))
door((D_X1, -0.03), 0.60, 180, 270, (D_X1, -0.63))
ax.plot([D_X0, D_X1], [-0.03, -0.03], color=NOIR, lw=lw_hair, ls=(0, (2, 2)), zorder=6)

# Jardinières maçonnées au pied de la façade (h 0,45)
for x0, x1 in ((0.35, 2.95), (5.05, 6.45)):
    rect(x0, -0.49, x1, -0.09, fc="white", ec=NOIR, lw=lw_fine, zorder=4)
    rect(x0 + 0.05, -0.44, x1 - 0.05, -0.09, fc="none", ec=NOIR, lw=lw_hair, zorder=4)
    for xx in np.arange(x0 + 0.22, x1 - 0.1, 0.42):
        for k in range(6):
            a = np.radians(k * 60 + 15)
            ax.add_patch(MPoly([(xx, -0.27), (xx + 0.15 * np.cos(a - .35), -0.27 + 0.15 * np.sin(a - .35)),
                                (xx + 0.18 * np.cos(a), -0.27 + 0.18 * np.sin(a)),
                                (xx + 0.15 * np.cos(a + .35), -0.27 + 0.15 * np.sin(a + .35))],
                               closed=True, fc="white", ec=DEG, lw=lw_hair, zorder=5))

# Arbre à livres (rayonnage circulaire Ø 0,90, noyau Ø 0,40, canopée Ø 2,60 en plafond)
TREE = np.array([4.75, 5.61])
ax.add_patch(plt.Circle(TREE, 1.30, fc="none", ec=GRIS, lw=lw_fine, ls=(0, (4, 2)), zorder=6))
ax.add_patch(plt.Circle(TREE, 0.45, fc="white", ec=NOIR, lw=lw_cut * .6, zorder=6))
ax.add_patch(plt.Circle(TREE, 0.20, fc=IROKO, ec=NOIR, lw=lw_fine, zorder=6))
for k in range(8):
    a = np.radians(k * 45 + 22.5)
    ax.plot([TREE[0] + .2 * np.cos(a), TREE[0] + .45 * np.cos(a)],
            [TREE[1] + .2 * np.sin(a), TREE[1] + .45 * np.sin(a)], color=NOIR, lw=lw_fine, zorder=6)
for k in range(48):
    a = np.radians(k * 7.5)
    ax.plot([TREE[0] + .24 * np.cos(a), TREE[0] + .42 * np.cos(a)],
            [TREE[1] + .24 * np.sin(a), TREE[1] + .42 * np.sin(a)], color=NOIR, lw=lw_hair * .7, zorder=6)
ax.text(TREE[0], TREE[1] + 1.18, "CANOPÉE Ø 2,60 (PLAFOND)", fontsize=4.3, color=GRIS, ha="center", va="center",
        zorder=8, bbox=dict(fc="white", ec="none", pad=0.3))
TAGS.setdefault("L01", []).append(Point(*TREE))

# Mur du fond : niches cintrées (2 bibliothèques + 1 banquette de lecture), doublage enduit
PIERS = [(3.09, 3.20), (4.10, 4.18), (5.43, 5.51), (6.41, 6.51)]
for x0, x1 in PIERS:
    rect(x0, 7.06, x1, 7.41, fc="#8C9397", ec=NOIR, lw=lw_mid, zorder=5)
for x0, x1 in ((3.20, 4.10), (5.51, 6.41)):
    rect(x0, 7.06, x1, 7.41, fc="white", ec=NOIR, lw=lw_cut * .55, zorder=5)
    rect(x0 + 0.03, 7.09, x1 - 0.03, 7.38, fc="none", ec=NOIR, lw=lw_hair, zorder=5)
    for xx in np.arange(x0 + 0.06, x1 - 0.05, 0.035):
        ax.plot([xx, xx], [7.12, 7.35], color=NOIR, lw=lw_hair * .7, zorder=5)
    TAGS.setdefault("N01", []).append(Point((x0 + x1) / 2, 7.235))
rect(4.18, 6.96, 5.43, 7.41, fc="white", ec=NOIR, lw=lw_fine, zorder=5)
rect(4.22, 7.00, 5.39, 7.30, fc="none", ec=NOIR, lw=lw_hair, zorder=5)
ax.plot([4.18, 5.43], [7.16, 7.16], color=GRIS, lw=lw_hair, ls=(0, (3, 2)), zorder=6)
TAGS.setdefault("N02", []).append(Point(4.805, 7.15))

# Rails lumineux raccourcis (arrêtés avant la canopée)
for xx in (3.65, 5.35):
    ax.plot([xx, xx], [0.40, 4.20], color=GRIS, lw=lw_hair, ls=(0, (3, 2)), zorder=6)

# Dégagements : sas d'entrée et cotes de passage
ax.add_patch(plt.Circle((4.10, 0.85), 0.75, fc="none", ec=DEG, lw=0.6, ls=(0, (3, 2)), zorder=7))
ax.text(4.10, 0.85, "Ø 1,50", fontsize=5.5, color=DEG, ha="center", va="center", zorder=8,
        bbox=dict(fc="white", ec="none", pad=0.4))

def passage(p, q, txt, side=1, size=5.2):
    p, q = np.array(p), np.array(q)
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<|-|>", color=DEG, lw=0.6, mutation_scale=5,
                                                    shrinkA=0, shrinkB=0), zorder=8)
    m = (p + q) / 2
    vert = abs(q[0] - p[0]) < abs(q[1] - p[1])
    ax.text(m[0] + (0.07 * side if vert else 0), m[1] + (0 if vert else 0.06 * side), txt, fontsize=size,
            color=DEG, rotation=90 if vert else 0, ha="center", va="center", zorder=8,
            bbox=dict(fc="white", ec="none", pad=0.3))

passage((3.09, 5.61), (4.30, 5.61), "1,21")
passage((5.20, 5.61), (6.12, 5.61), "0,92")
passage((4.75, 6.06), (4.75, 6.96), "0,90", side=-1)
passage((3.49, 3.05), (4.41, 3.05), "0,92")
passage((D_X0, -1.10), (D_X1, -1.10), "1,50 (0,90 + 0,60)", side=-1)
passage((2.37, -2.05), (4.71, -2.05), "axe libre 2,34", side=-1)

# Repères des principes (renvoient au cartouche)
MARKS = {1: (3.05, -0.38), 2: (6.05, 0.62), 3: (4.02, 6.45), 4: (3.62, 6.78), 5: (5.30, 2.95),
         6: (0.25, -0.30), 7: (3.40, -2.40)}
for n, (x, y) in MARKS.items():
    ax.text(x, y, str(n), fontsize=6.5, color="white", ha="center", va="center", zorder=10,
            bbox=dict(boxstyle="circle,pad=0.25", fc=NOIR, ec="none"))
# Pergola paramétrique (lames bois en deux nappes, au-dessus du plan de coupe)
TERR_X0, TERR_X1 = 0.0, 6.60
xa, x = [], 0.05
while x < 6.56:
    xa.append(x); x += spacing(x, [1.375, 4.80], 0.07, 0.24, 1.3)
segA = []
for x in xa:
    yend = -2.52 - 0.30 * (0.5 + 0.5 * np.sin(2 * np.pi * (x - 0.6) / 3.3))
    segA.append([(x, -0.17), (x, yend)])
ya, y = [], -0.24
while y > -2.45:
    ya.append(y); y -= 0.08 + 0.20 * (abs(y) / 2.5) ** 1.4
segB = [[(-0.05, y), (6.65, y)] for y in ya]
ax.add_collection(LineCollection(segB, colors=BOIS, lw=0.25, alpha=.6, zorder=1))
ax.add_collection(LineCollection(segA, colors=BOIS, lw=0.4, alpha=.8, zorder=1))
ax.text(6.6, -3.10, "PERGOLA BOIS PARAMÉTRIQUE — PROJECTION", fontsize=5.5, ha="right", color=GRIS)

# Repères mobilier
for code, pts in TAGS.items():
    for c in pts:
        ax.text(c.x, c.y, code, fontsize=4.6, ha="center", va="center", color="white", zorder=9,
                bbox=dict(boxstyle="circle,pad=0.18", fc=TAG, ec="none"))

# Locaux
def room(x, y, nom, surf, size=8.5, inline=False, rot=0):
    bb = dict(fc="white", ec="none", pad=0.6, alpha=.85)
    if inline:
        ax.text(x, y, f"{nom}  {surf}", fontsize=size, ha="center", va="center", color=NOIR,
                zorder=8, bbox=bb, rotation=rot)
        return
    ax.text(x, y, nom, fontsize=size, ha="center", va="bottom", color=NOIR, zorder=8, bbox=bb)
    ax.text(x, y - 0.05, surf, fontsize=6.5, ha="center", va="top", color=VERT, zorder=8, bbox=bb)

m2 = lambda a: f"{a:.1f} m²".replace(".", ",")
ROOMS = [
    ("Coin lecture", box(0.09, 0.09, 2.91, 2.47), dict(x=2.25, y=0.62)),
    ("Salle de réunion", box(0.09, 2.50, 2.97, 5.04), dict(x=1.15, y=2.70)),
    ("WC", box(0.09, 6.36, 2.91, 7.41), dict(x=1.62, y=7.12, size=7, inline=True)),
    ("Dégagement", box(1.88, 5.16, 2.91, 6.24), dict(x=2.30, y=5.62, size=5.5, inline=True, rot=90)),
    ("Rangement", box(0.09, 5.16, 1.76, 6.24), dict(x=0.93, y=5.70, size=6.5, inline=True)),
    ("Salle de lecture", box(3.09, 0.09, 6.51, 7.41).difference(box(5.61, 3.30, 6.51, 4.20)), dict(x=4.12, y=2.10)),
]
surfaces = []
for nom, poly, pos in ROOMS:
    surfaces.append((nom, poly.area))
    room(nom=nom, surf=m2(poly.area), **pos)
terr = box(0.0, -2.75, 6.6, 0.0)
room(1.55, -0.70, "Terrasse couverte", m2(terr.area))

ax.add_patch(FancyArrowPatch((3.82, -1.55), (3.82, 0.55), arrowstyle="-|>", mutation_scale=9, color=VERT, lw=1.2, zorder=9))
ax.add_patch(FancyArrowPatch((4.42, 0.55), (4.42, -1.55), arrowstyle="-|>", mutation_scale=9, color=GRIS, lw=1.2, zorder=9))
ax.text(3.74, -0.80, "ENTRÉE", fontsize=6, ha="right", va="center", color=VERT, zorder=9, bbox=dict(fc="white", ec="none", pad=0.5))
ax.text(4.50, -0.80, "SORTIE", fontsize=6, ha="left", va="center", color=GRIS, zorder=9, bbox=dict(fc="white", ec="none", pad=0.5))
ax.add_patch(FancyArrowPatch((3.75, 5.72), (3.12, 5.72), arrowstyle="-|>", mutation_scale=6, color=VERT, lw=.8, zorder=9))

def cote(p, q, off, txt, vertical=False):
    if vertical:
        x = p[0] + off
        ax.plot([x, x], [p[1], q[1]], color=GRIS, lw=lw_fine)
        for yy in (p[1], q[1]):
            ax.plot([x - .06, x + .06], [yy - .06, yy + .06], color=GRIS, lw=lw_mid)
            ax.plot([p[0] + off * .25, x], [yy, yy], color=GRIS, lw=lw_hair)
        ax.text(x + .08, (p[1] + q[1]) / 2, txt, rotation=90, fontsize=6.5, va="center", ha="left", color=GRIS)
    else:
        y = p[1] + off
        ax.plot([p[0], q[0]], [y, y], color=GRIS, lw=lw_fine)
        for xx in (p[0], q[0]):
            ax.plot([xx - .06, xx + .06], [y - .06, y + .06], color=GRIS, lw=lw_mid)
            ax.plot([xx, xx], [p[1] + off * .25, y], color=GRIS, lw=lw_hair)
        ax.text((p[0] + q[0]) / 2, y + .07, txt, fontsize=6.5, ha="center", va="bottom", color=GRIS)
cote((-0.09, 7.62), (6.69, 7.62), 0.25, "6,78")
cote((6.69, -0.09), (6.69, 7.59), 0.35, "7,68", vertical=True)
cote((6.69, -2.75), (6.69, -0.09), 0.35, "2,66", vertical=True)
# cote du M01 (40 cm)
ax.plot([3.09, 3.49], [4.14, 4.14], color=GRIS, lw=lw_fine, zorder=8)
for xx in (3.09, 3.49):
    ax.plot([xx - .03, xx + .03], [4.11, 4.17], color=GRIS, lw=lw_mid, zorder=8)
ax.text(3.29, 4.18, "40", fontsize=5, color=GRIS, ha="center", va="bottom", zorder=8)

sx, sy = XMIN + 0.1, YMIN + 0.05
for i in range(4):
    rect(sx + i, sy, sx + i + 1, sy + 0.08, fc=NOIR if i % 2 == 0 else "white", ec=NOIR, lw=.3, zorder=9)
    ax.text(sx + i, sy + 0.14, str(i), fontsize=5.5, ha="center", color=GRIS)
ax.text(sx + 4, sy + 0.14, "4 m", fontsize=5.5, ha="center", color=GRIS)


# --- cartouche (charte K&D) --------------------------------------------------
fig.add_artist(Rectangle((228 / 420, 0), 192 / 420, 1, transform=fig.transFigure, fc=SABLE_CLAIR, ec="none", zorder=-5))
draw_logo(fig, 16, 11, 15)

X0, X1, XR = 236 / 420, 404 / 420, 326 / 420
C1R = 316 / 420
def T(x, y_mm, s, size, color=NOIR, **kw):
    return fig.text(x, 1 - y_mm / 297, s, fontsize=size, color=color, va="top", **kw)
T(X0, 12.5, "Bibliothèque Decimo", 25, NOIR, fontproperties=FP_TITRE)
T(X0, 27, "Proposition d’aménagement V4 — arbre à livres et façade cintrée", 12, VERT)
T(X0, 35, "Plan du rez-de-chaussée  ·  Esquisse V4 (sur base V3)  ·  Échelle 1/50 (A3)  ·  Coupe à +1,10 m", 8.5, GRIS)
fig.add_artist(plt.Line2D([X0, X1], [1 - 42 / 297] * 2, color=VERT, lw=1.2))

PRINCIPES = [
    "Entrée principale cintrée dans un portail terre\ncuite : double porte vitrée 0,90 + 0,60, ouvrant\nvers l’extérieur, seuil plat, sas intérieur Ø 1,50",
    "Accueil : le comptoir fait face au flux d’entrée ;\nposte agent dos à la baie à claustra (C)",
    "Arbre à livres au fond, Ø 0,90 sous une canopée\nØ 2,60 ; tour complet en 0,90 minimum",
    "Mur du fond en 3 niches cintrées : 2 bibliothèques\net 1 banquette de lecture (fond en lames bois)",
    "Salon de lecture recentré entre console M01\net pilier ; passage principal 0,92 côté ouest",
    "Façade : baies cintrées à claustra terre cuite\n(A, B coin lecture ; C accueil) et jardinières",
    "Terrasse : groupe de tables est décalé de 1 m\npour dégager un axe d’entrée de 2,34 m",
]
T(X0, 49, "PRINCIPES D’AMÉNAGEMENT", 8.5, VERT, fontproperties=FP_MEDIUM)
y = 56
for i, s in enumerate(PRINCIPES, 1):
    fig.text(X0 + 2 / 420, 1 - (y + 1.3) / 297, str(i), fontsize=6, color="white", ha="center", va="center",
             bbox=dict(boxstyle="circle,pad=0.25", fc=NOIR, ec="none"))
    T(X0 + 7 / 420, y, s, 7.2, linespacing=1.25)
    y += 4.15 * (s.count("\n") + 1) + 2.2

y += 2
T(X0, y, "CONTRÔLE ERGONOMIQUE", 8.5, VERT, fontproperties=FP_MEDIUM); y += 6
ROWS = [("Passage principal", "min. 0,90", "0,92"), ("Tour de l’arbre à livres", "min. 0,90", "0,90 à 1,21"),
        ("Entrée (2 UP)", "min. 1,40", "1,50"), ("Vantail principal", "min. 0,90", "0,90"),
        ("Aire de manœuvre derrière l’entrée", "Ø 1,50", "Ø 1,50"),
        ("Hauteur libre sous canopée", "min. 2,20", "2,40"), ("Axe libre en terrasse", "min. 1,40", "2,34")]
fig.add_artist(Rectangle((X0 - 1 / 420, 1 - (y + 4.2) / 297), (C1R - X0) + 2 / 420, 5.4 / 297,
                         transform=fig.transFigure, fc=VERT, ec="none"))
T(X0, y + 0.4, "Critère", 7, "white"); T(290 / 420, y + 0.4, "Cible", 7, "white", ha="right")
T(C1R, y + 0.4, "Proposé", 7, "white", ha="right"); y += 6.4
for k, (a, b, c) in enumerate(ROWS):
    if k % 2:
        fig.add_artist(Rectangle((X0 - 1 / 420, 1 - (y + 3.6) / 297), (C1R - X0) + 2 / 420, 4.6 / 297,
                                 transform=fig.transFigure, fc="#EBDFCC", ec="none"))
    T(X0, y, a, 6.8); T(290 / 420, y, b, 6.8, GRIS, ha="right"); T(C1R, y, c, 6.8, ha="right")
    y += 4.6
T(X0, y + 1.5, "Cotes en mètres, mesurées au nu des éléments finis.", 6.2, GRIS)

LIB = {"A01": "Fauteuil", "B01": "Rayonnage 800", "B02": "Banquette", "C01": "Chaise courbe",
       "C02": "Comptoir d’accueil", "M01": "Console vinyles (40 cm)", "T01": "Table de réunion 1300",
       "T02": "Table ronde", "P01": "Pouf", "V01": "Plante en pot",
       "L01": "Arbre à livres (Ø 0,90, canopée)", "N01": "Niche cintrée bibliothèque",
       "N02": "Niche cintrée banquette"}
T(XR, 49, "MOBILIER", 8.5, VERT, fontproperties=FP_MEDIUM)
y = 56
for code in sorted(TAGS):
    fig.text(XR + 2 / 420, 1 - (y + 1.1) / 297, code, fontsize=5.3, color="white", ha="center", va="center",
             bbox=dict(boxstyle="circle,pad=0.2", fc=TAG, ec="none"))
    T(XR + 7 / 420, y, LIB.get(code, code), 7.2)
    T(X1, y, f"× {len(TAGS[code])}", 7.2, GRIS, ha="right")
    y += 4.7

y += 5
T(XR, y, "LÉGENDE", 8.5, VERT, fontproperties=FP_MEDIUM); y += 6.5
def leg(y, kind, txt):
    x = XR + 1 / 420; w = 8 / 420; h = 2.6 / 297; yy = 1 - (y + 2.8) / 297
    if kind == "mur":
        fig.add_artist(Rectangle((x, yy), w, h, transform=fig.transFigure, fc=POCHE, ec=NOIR, lw=.4))
    elif kind == "doublage":
        fig.add_artist(Rectangle((x, yy), w, h, transform=fig.transFigure, fc="#8C9397", ec=NOIR, lw=.4))
    elif kind == "claustra":
        fig.add_artist(Rectangle((x, yy), w, h, transform=fig.transFigure, fc=TERRA, ec=NOIR, lw=.4))
    elif kind == "verre":
        fig.add_artist(Rectangle((x, yy + h / 3), w, h / 3, transform=fig.transFigure, fc="#DCEBF0", ec=NOIR, lw=.4))
    elif kind == "bois":
        for i in range(6):
            fig.add_artist(Rectangle((x + i * w / 6, yy), w / 14, h, transform=fig.transFigure, fc=BOIS, ec=NOIR, lw=.2))
    elif kind == "proj":
        fig.add_artist(plt.Line2D([x, x + w], [yy + h / 2] * 2, color=GRIS, lw=.5, ls=(0, (3, 2))))
    elif kind == "deg":
        fig.add_artist(plt.Line2D([x, x + w], [yy + h / 2] * 2, color=DEG, lw=.8))
    elif kind == "mit":
        fig.add_artist(Rectangle((x, yy), w, h, transform=fig.transFigure, fc="white", ec=GRIS, lw=.3, hatch="////"))
    T(XR + 11 / 420, y, txt, 6.8)
for k, s in [("mur", "Maçonnerie / cloison (coupée)"), ("doublage", "Doublage cintré des niches"),
             ("claustra", "Claustra terre cuite / portail"), ("verre", "Vitrage"),
             ("bois", "Lames bois (pergola)"), ("proj", "Au-dessus du plan de coupe"),
             ("deg", "Cote de passage / dégagement"), ("mit", "Bâtiment mitoyen")]:
    leg(y, k, s); y += 4.9

y += 4
T(XR, y, "À VALIDER AVANT MISE À JOUR IFC", 8.5, VERT, fontproperties=FP_MEDIUM); y += 6
for s in ["Le mur du fond passe du claustra V3 aux\nniches cintrées (lames bois en fond de niche)",
          "Le bureau du fond et ses 3 chaises sont\nremplacés par la banquette de la niche centrale",
          "2 rayonnages supprimés (zone agent, niche est),\ncompensés par les niches et l’arbre à livres",
          "L’ancienne porte du coin lecture devient\nune baie à claustra (accès par la salle de lecture)"]:
    T(XR, y, "—", 6.8, GRIS); T(XR + 4 / 420, y, s, 6.8, linespacing=1.25)
    y += 4.0 * (s.count("\n") + 1) + 1.8

fig.add_artist(plt.Line2D([X0, X1], [1 - 270 / 297] * 2, color=GRIS, lw=.4))
T(X0, 273, "Base : maquette DECIMO_ESQ_V3.ifc (niveau N00 _ RDC) — proposition V4 non encore reportée dans la maquette.", 6.2, GRIS)
T(X0, 278, "Document d’esquisse — dimensions et surfaces indicatives, à vérifier sur site.", 6.2, GRIS)
T(X1, 278, "K&Démi  ·  PLAN RDC — ESQ V4  ·  Octobre 2026", 6.2, VERT, ha="right")

fig.savefig(OUT + ".pdf"); fig.savefig(OUT + ".png", dpi=200)
print("ok", {k: len(v) for k, v in TAGS.items()})
