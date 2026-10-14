"""Plan du RDC V3 — Bibliothèque Decimo : base DECIMO_ESQ_V2.ifc + remarques du 14/10/2026."""
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
LOGO = "/root/.claude/skills/synced/68b949f7-29fd-4b06-8f9e-f06c81c76d86_30805531-b9b3-4d6e-85e6-49dfe06bdd23/charte-kd/assets/Logo KDA.jpg"
FONT = "/tmp/claude-0/-home-user/5dfc2a2e-f67b-5d7c-bd12-e0811e213d4e/scratchpad/fonts/Questrial-Regular.ttf"
OUT = sys.argv[1]

font_manager.fontManager.addfont(FONT)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=FONT).get_name()
plt.rcParams["pdf.fonttype"] = 42

NOIR, GRIS, VERT, GCLAIR = "#0B0C12", "#66747C", "#7AB648", "#F2F2F2"
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
}
MOVE = {
    "4350673": dict(dx=1.76, dy=0.14), "4350674": dict(dx=1.76, dy=0.14),  # comptoir d'accueil
    "4350675": dict(dx=1.76, dy=0.14),
}
# lave-mains du WC unique : pivoté contre le mur est (ancienne porte du WC 2 condamnée)
SINK_C = (1.575, 6.72)
for k in ("4350630", "4350631"):
    MOVE[k] = dict(rot=90, about=SINK_C, dx=2.72 - SINK_C[0], dy=6.86 - SINK_C[1])

WALL_EDIT = {   # tag : (ajouts, retraits) en boîtes (x0, y0, x1, y1)
    "4350608": ([(2.91, 6.40, 3.09, 7.39)], [(2.88, 5.30, 3.12, 6.14)]),   # porte WC 2 bouchée, baie vers dégagement
    "4350621": ([(1.80, 5.04, 2.79, 5.16)], []),                            # porte WC 1 bouchée
    "4350620": ([], [(1.90, 6.22, 2.83, 6.38)]),                            # nouvelle porte du WC
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
POCHE = "#3A3F44"
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

GLASS = {"4350609", "4350597", "4350598"}
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
        ax.text(g.centroid.x, 3.6, "BATIMENT\nMITOYEN", rotation=90, ha="center", va="center",
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
door((0.92, 0.09), 0.91, 0, 90, (0.92, 1.0))           # entrée
door((2.83, 6.30), 0.93, 180, 270, (2.83, 5.37))       # WC, ouvrant vers le dégagement
door((3.00, 5.00), 0.93, 180, 270, (2.07, 5.00))       # salle de réunion (déplacée)
# porte coulissante du rangement
rect(1.90, 5.30, 1.93, 6.10, fc="white", ec=NOIR, lw=lw_mid, zorder=6)

# Claustra bois paramétrique du mur du fond (même écriture que la pergola)
def spacing(x, attractors, smin, smax, reach):
    d = min(abs(x - a) for a in attractors)
    return smin + (smax - smin) * (1 - np.exp(-(d / reach) ** 2))

XC, HW = 4.62, 1.50
offs, o = [0.0], 0.0
while True:
    o += spacing(XC + o, [XC], 0.075, 0.16, 1.1)
    if o > 1.48:
        break
    offs.append(o)
xs = sorted({round(XC + k * o, 4) for o in offs for k in (-1, 1)})
for x in xs:
    u = np.clip((x - XC) / HW, -0.995, 0.995)
    d = 0.05 + 1.0 * (1 - np.sqrt(1 - u * u))
    over_desk = 3.50 <= x <= 5.88
    dcut = 0.05 if over_desk else d
    rect(x - 0.017, 7.41 - dcut, x + 0.017, 7.41, fc=BOIS, ec=NOIR, lw=lw_hair, zorder=6)
    if over_desk and d > 0.06:
        ax.plot([x, x], [7.41 - d, 7.41 - 0.05], color=GRIS, lw=0.35, ls=(0, (2, 1.2)), zorder=6)
uu = np.linspace(-0.995, 0.995, 120)
ax.plot(XC + HW * uu, 7.41 - (0.05 + 1.0 * (1 - np.sqrt(1 - uu ** 2))), color=GRIS, lw=lw_fine,
        ls=(0, (4, 2)), zorder=6)
ax.text(4.70, 7.64, "CLAUSTRA BOIS PARAMETRIQUE (MUR DU FOND)", fontsize=4.8, color=GRIS, ha="center", va="bottom", zorder=8,
        bbox=dict(fc="white", ec="none", pad=0.5))

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
ax.text(6.6, -3.10, "PERGOLA BOIS PARAMETRIQUE — PROJECTION", fontsize=5.5, ha="right", color=GRIS)

# Repères mobilier
for code, pts in TAGS.items():
    for c in pts:
        ax.text(c.x, c.y, code, fontsize=4.6, ha="center", va="center", color="white", zorder=9,
                bbox=dict(boxstyle="circle,pad=0.18", fc=VERT, ec="none"))

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
    ("Salle de lecture", box(3.09, 0.09, 6.51, 7.41).difference(box(5.61, 3.30, 6.51, 4.20)), dict(x=4.70, y=5.47)),
]
surfaces = []
for nom, poly, pos in ROOMS:
    surfaces.append((nom, poly.area))
    room(nom=nom, surf=m2(poly.area), **pos)
terr = box(0.0, -2.75, 6.6, 0.0)
room(3.0, -0.55, "Terrasse couverte", m2(terr.area))

ax.add_patch(FancyArrowPatch((1.375, -0.75), (1.375, -0.12), arrowstyle="-|>", mutation_scale=9, color=VERT, lw=1.2, zorder=9))
ax.text(1.28, -0.45, "ENTREE", fontsize=6.5, ha="right", va="center", color=VERT, zorder=9,
        bbox=dict(fc="white", ec="none", pad=0.5))
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
logo = plt.imread(LOGO)
lh = 60 * logo.shape[0] / logo.shape[1]
lax = fig.add_axes([16 / 420, (297 - 12 - lh) / 297, 60 / 420, lh / 297]); lax.imshow(logo); lax.axis("off")

X0, X1, XR = 236 / 420, 404 / 420, 326 / 420
def T(x, y_mm, s, size, color=NOIR, **kw):
    return fig.text(x, 1 - y_mm / 297, s, fontsize=size, color=color, va="top", **kw)
T(X0, 16, "BIBLIOTHEQUE DECIMO", 22, GRIS)
T(X0, 27, "Plan du rez-de-chaussée — proposition d’aménagement intérieur", 12, VERT)
T(X0, 35, "Esquisse V3 (remarques du 14/10/2026 intégrées)  ·  Échelle 1/50 (A3)  ·  Coupe à +1,10 m", 8.5, GRIS)
fig.add_artist(plt.Line2D([X0, X1], [1 - 42 / 297] * 2, color=VERT, lw=1.2))

# colonne 1 : surfaces + mobilier
C1R = 316 / 420
T(X0, 49, "SURFACES INTERIEURES (ENV.)", 9, VERT)
y = 56; tot = 0
for nom, a in surfaces:
    T(X0, y, nom, 7.5); T(C1R, y, m2(a), 7.5, ha="right"); tot += a; y += 4.6
fig.add_artist(Rectangle((X0 - 1 / 420, 1 - (y + 4) / 297), (C1R - X0) + 2 / 420, 5.6 / 297,
                         transform=fig.transFigure, fc="#333333", ec="none"))
T(X0, y + 0.4, "Total intérieur", 7.5, "white"); T(C1R, y + 0.4, m2(tot), 7.5, "white", ha="right")
y += 8.5
T(X0, y, "Terrasse couverte (pergola)", 7.5, GRIS); T(C1R, y, m2(terr.area), 7.5, GRIS, ha="right")

LIB = {"A01": "Fauteuil", "B01": "Rayonnage 800", "B02": "Banquette", "C01": "Chaise courbe",
       "C02": "Comptoir d’accueil", "M01": "Console vinyles (40 cm)", "T01": "Table de réunion 1300",
       "T02": "Table ronde", "P01": "Pouf", "V01": "Plante en pot"}
y += 11
T(X0, y, "MOBILIER", 9, VERT); y += 6.5
for code in sorted(TAGS):
    fig.text(X0 + 2 / 420, 1 - (y + 1.1) / 297, code, fontsize=5.3, color="white", ha="center", va="center",
             bbox=dict(boxstyle="circle,pad=0.2", fc=VERT, ec="none"))
    T(X0 + 7 / 420, y, LIB.get(code, code), 7.5)
    T(C1R, y, f"× {len(TAGS[code])}", 7.5, GRIS, ha="right")
    y += 4.8

# colonne 2 : évolutions + légende
T(XR, 49, "EVOLUTIONS PAR RAPPORT A LA V2", 9, VERT)
EVOL = [
    "Un seul WC (ex-WC 2), accès depuis la salle\nde lecture par un dégagement ; lave-mains\nreporté contre l’ancienne porte, condamnée",
    "Ex-WC 1 : dégagement + rangement\n(porte coulissante)",
    "Salle de réunion : tableau mural, porte\ndéplacée en haut de cloison, partie basse\nde la cloison rendue pleine",
    "Console vinyles M01 (prof. 40 cm) contre\nla cloison de la salle de réunion",
    "Comptoir d’accueil déplacé côté vitrine",
    "Porte à galandage entre coin lecture\net salle de lecture",
    "Claustra bois paramétrique sur le mur du fond,\nmême écriture que la pergola",
    "Pergola bois paramétrique, inspiration\nKengo Kuma (voir principe ci-dessous)",
]
y = 56
for s in EVOL:
    T(XR, y, "—", 7.2, GRIS); txt = T(XR + 4 / 420, y, s, 7.2, linespacing=1.25)
    y += 4.2 * (s.count("\n") + 1) + 1.6

y += 3
T(XR, y, "LEGENDE", 9, VERT); y += 6.5
def leg(y, kind, txt):
    x = XR + 1 / 420; w = 8 / 420; h = 2.6 / 297; yy = 1 - (y + 2.8) / 297
    if kind == "mur":
        fig.add_artist(Rectangle((x, yy), w, h, transform=fig.transFigure, fc=POCHE, ec=NOIR, lw=.4))
    elif kind == "verre":
        fig.add_artist(Rectangle((x, yy + h / 3), w, h / 3, transform=fig.transFigure, fc="#DCEBF0", ec=NOIR, lw=.4))
    elif kind == "bois":
        for i in range(6):
            fig.add_artist(Rectangle((x + i * w / 6, yy), w / 14, h, transform=fig.transFigure, fc=BOIS, ec=NOIR, lw=.2))
    elif kind == "proj":
        fig.add_artist(plt.Line2D([x, x + w], [yy + h / 2] * 2, color=GRIS, lw=.5, ls=(0, (3, 2))))
    elif kind == "mit":
        fig.add_artist(Rectangle((x, yy), w, h, transform=fig.transFigure, fc="white", ec=GRIS, lw=.3, hatch="////"))
    T(XR + 11 / 420, y, txt, 6.8)
for k, s in [("mur", "Maçonnerie / cloison (coupée)"), ("verre", "Vitrage"), ("bois", "Lames bois (claustra, pergola)"),
             ("proj", "Au-dessus du plan de coupe"), ("mit", "Bâtiment mitoyen")]:
    leg(y, k, s); y += 5

# --- principe de la pergola (axonométrie) ------------------------------------
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
def beam(x0, y0, z0, dx, dy, dz):
    p = np.array([[x0, y0, z0], [x0 + dx, y0, z0], [x0 + dx, y0 + dy, z0], [x0, y0 + dy, z0]])
    top = p + [0, 0, dz]
    return [p, top, [p[0], p[1], top[1], top[0]], [p[1], p[2], top[2], top[1]],
            [p[2], p[3], top[3], top[2]], [p[3], p[0], top[0], top[3]]]
faces = []
for (px, py) in [(0.25, -2.5), (6.25, -2.5)]:
    faces += beam(px, py, 0, 0.08, 0.08, 2.65)
faces += beam(0.25, -2.5, 2.65, 6.08, 0.08, 0.10) + beam(0.25, -0.15, 2.65, 6.08, 0.08, 0.10)
for y in ya:
    faces += beam(-0.05, y, 2.75, 6.70, 0.04, 0.06)
for x in xa:
    yend = -2.52 - 0.30 * (0.5 + 0.5 * np.sin(2 * np.pi * (x - 0.6) / 3.3))
    hz = 0.10 + 0.16 * (0.5 + 0.5 * np.cos(2 * np.pi * (x - 1.375) / 3.4))   # hauteur variable des lames
    faces += beam(x - 0.017, yend, 2.81, 0.034, -0.17 - yend, hz)
axo = fig.add_axes([X0 - 6 / 420, 14 / 297, 112 / 420, 62 / 297], projection="3d", computed_zorder=False)
pc3 = Poly3DCollection(faces, facecolor=BOIS, edgecolor=NOIR, linewidths=0.08)
facade = [[(0, 0, 0), (6.6, 0, 0), (6.6, 0, 3.3), (0, 0, 3.3)]]
axo.add_collection3d(Poly3DCollection(facade, facecolor=GCLAIR, edgecolor=GRIS, linewidths=0.3))
axo.add_collection3d(pc3)
axo.set_xlim(-0.2, 6.8); axo.set_ylim(-3.2, 0.2); axo.set_zlim(0, 3.4)
axo.set_box_aspect((7.0, 3.4, 3.4)); axo.view_init(elev=28, azim=-62); axo.set_axis_off()
axo.patch.set_alpha(0)
T(X0, 196, "PRINCIPE — PERGOLA BOIS PARAMETRIQUE", 9, VERT)
T(XR + 22 / 420, 205, "Deux nappes de lames bois croisées, à la\n"
  "manière des assemblages de Kengo Kuma.\n\n"
  "Paramètres :\n"
  "— espacement des lames resserré au droit\n   de l’entrée et de la vitrine\n"
  "— nappe inférieure plus dense côté façade\n"
  "— hauteur des lames et rive côté rue\n   en ondulation\n\n"
  "Le claustra du mur du fond reprend la même\nlame et la même loi d’espacement.", 6.8, linespacing=1.3)

fig.add_artist(plt.Line2D([X0, X1], [1 - 270 / 297] * 2, color=GRIS, lw=.4))
T(X0, 273, "Base : maquette DECIMO_ESQ_V3.ifc (niveau N00 _ RDC), issue de la V2 + remarques du 14/10/2026 — à reporter dans le projet Revit.", 6.2, GRIS)
T(X0, 278, "Document d’esquisse — dimensions et surfaces indicatives, à vérifier sur site.", 6.2, GRIS)
T(X1, 278, "PLAN RDC — ESQ V3  ·  Octobre 2026", 6.2, VERT, ha="right")

fig.savefig(OUT + ".pdf"); fig.savefig(OUT + ".png", dpi=200)
print("ok", {k: len(v) for k, v in TAGS.items()}, [(n, round(a, 2)) for n, a in surfaces])
