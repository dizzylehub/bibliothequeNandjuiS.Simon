"""Plan du RDC — Bibliothèque Decimo (DECIMO_ESQ_V2.ifc), coupe horizontale à +1,10 m."""
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

# Carrelage 60 x 60 (lignes du modèle), découpé à l'intérieur
interior = box(0.09, 0.09, 6.51, 7.41)
walls_cut = []
for eid, (e, v, t) in meshes.items():
    if e.is_a("IfcWall") or e.is_a("IfcWallStandardCase"):
        walls_cut.append(section(v, t, H))
walls_u = unary_union([w for w in walls_cut if w])
for eid, (e, v, t) in meshes.items():
    if e.is_a("IfcBuildingElementProxy") and (v[:, 2].max() - v[:, 2].min()) < 0.02 and \
       (np.ptp(v[:, 0]) < 0.02 or np.ptp(v[:, 1]) < 0.02):
        ls = LineString([tuple(v[:, :2].min(0)), tuple(v[:, :2].max(0))]).intersection(interior.difference(walls_u))
        for g in getattr(ls, "geoms", [ls]):
            if not g.is_empty:
                ax.plot(*g.xy, color="#B8BEC2", lw=0.3, zorder=0)

# Bâtiment mitoyen (volume 4350700) : hachuré, coupé au cadre
for eid, (e, v, t) in meshes.items():
    if e.is_a("IfcBuildingElementProxy") and e.Name == "4350700":
        g = footprint(v, t).intersection(frame)
        draw_geom(ax, g, fc="white", ec=GRIS, lw=lw_fine, hatch="////", zorder=0)
        c = g.centroid
        ax.text(c.x, 3.6, "BATIMENT\nMITOYEN", rotation=90, ha="center", va="center",
                fontsize=6.5, color=GRIS, zorder=5,
                bbox=dict(fc="white", ec="none", pad=1.5))

GLASS = {"4350609", "4350610", "4350611", "4350597", "4350598"}
SKIP = {"4350632", "4350700", "4350705", "4350742", "4350743", "4350744", "4350745", "4350634"}
TAGS = {}
cut_polys = []

for eid, (e, v, t) in meshes.items():
    zmin, zmax = v[:, 2].min(), v[:, 2].max()
    name = e.Name or ""
    if e.is_a("IfcOpeningElement") or name in SKIP:
        continue
    if e.is_a("IfcBuildingElementProxy") and (zmax - zmin) < 0.02 and \
       (np.ptp(v[:, 0]) < 0.02 or np.ptp(v[:, 1]) < 0.02):
        continue  # lignes de calepinage déjà tracées
    if e.is_a("IfcWall") or e.is_a("IfcWallStandardCase"):
        g = section(v, t, H)
        cut_polys.append(g)
        draw_geom(ax, g, fc="#3A3F44", ec=NOIR, lw=lw_mid, zorder=4)
        continue
    if name in GLASS:
        g = footprint(v, t)
        draw_geom(ax, g, fc="#DCEBF0", ec=NOIR, lw=lw_mid, zorder=4)
        continue
    if e.is_a("IfcBuildingElementProxy") and name == "4350707":   # dalle terrasse
        outline(ax, footprint(v, t).intersection(frame), color=NOIR, lw=lw_mid, zorder=2)
        continue
    if e.is_a("IfcBuildingElementProxy") and name == "4350706":   # bordure
        outline(ax, footprint(v, t).intersection(frame), color=GRIS, lw=lw_fine, zorder=2)
        continue
    if zmin > H:   # au-dessus du plan de coupe : pointillés
        g = footprint(v, t)
        outline(ax, g, color=GRIS, lw=lw_hair, ls=(0, (3, 2)), zorder=6)
        continue
    furn = e.is_a("IfcFurnishingElement") or e.is_a("IfcFlowTerminal") or e.is_a("IfcDoor")
    if zmax > H and not furn and zmin < 0.05:  # élément structurel coupé (poteaux, montants, pilier)
        g = section(v, t, H) or footprint(v, t)
        draw_geom(ax, g, fc="#3A3F44", ec=NOIR, lw=lw_mid, zorder=4)
        continue
    # vue en projection (mobilier, sanitaires, éléments bas)
    g = footprint(v, t)
    zo = 3 if not e.is_a("IfcDoor") else 5
    lw = lw_cut * .55 if (zmax > H and furn) else lw_fine
    draw_geom(ax, g, fc="white", ec=NOIR, lw=lw, zorder=zo)
    if not e.is_a("IfcDoor"):
        ed = feature_edges(v, t)
        if ed:
            ax.add_collection(LineCollection(ed, colors=NOIR, lw=lw_hair, zorder=zo))
    if e.is_a("IfcFurnishingElement"):
        tp = ue.get_type(e)
        code = (tp.Name if tp else name).split(":")[0].replace("DECIMO_", "")
        TAGS.setdefault(code.split("_")[0], []).append((g.centroid, code))

# Portes : débattements (ouverture vers l'intérieur des WC)
def door(ax, hinge, r, a0, a1, leaf_end):
    ax.add_patch(Arc(hinge, 2 * r, 2 * r, theta1=a0, theta2=a1, color=NOIR, lw=lw_hair, zorder=6))
    ax.plot([hinge[0], leaf_end[0]], [hinge[1], leaf_end[1]], color=NOIR, lw=lw_mid, zorder=6)
door(ax, (2.91, 7.36), 0.93, 180, 270, (1.98, 7.36))      # WC 2, depuis le hall
door(ax, (2.76, 5.10), 0.93, 90, 180, (2.76, 6.03))       # WC 1, depuis la salle de réunion
# Porte d'entrée vitrée (façade) et porte vitrée de la salle de réunion
door(ax, (0.92, 0.09), 0.91, 0, 90, (0.92, 1.0))
door(ax, (3.0, 3.68), 0.86, 180, 270, (2.14, 3.68))

# Repères mobilier (pastilles)
for code, items in TAGS.items():
    for c, full in items:
        ax.text(c.x, c.y, code, fontsize=4.6, ha="center", va="center", color="white", zorder=9,
                bbox=dict(boxstyle="circle,pad=0.18", fc=VERT, ec="none"))

# Noms des locaux
def room(x, y, nom, surf, size=8.5, inline=False):
    if inline:
        ax.text(x, y, f"{nom}  {surf}", fontsize=size, ha="center", va="center", color=NOIR, zorder=8,
                bbox=dict(fc="white", ec="none", pad=0.6, alpha=.85))
        return
    ax.text(x, y, nom, fontsize=size, ha="center", va="bottom", color=NOIR, zorder=8,
            bbox=dict(fc="white", ec="none", pad=0.6, alpha=.85))
    ax.text(x, y - 0.05, surf, fontsize=6.5, ha="center", va="top", color=VERT, zorder=8,
            bbox=dict(fc="white", ec="none", pad=0.6, alpha=.85))

ROOMS = [  # (nom, rectangle intérieur, position étiquette)
    ("Coin lecture", box(0.09, 0.09, 2.91, 2.47), (2.3, 0.62)),
    ("Salle de réunion", box(0.09, 2.50, 2.97, 5.04), (1.05, 2.58 + 0.12)),
    ("WC 1", box(0.09, 5.16, 2.91, 6.24), (1.45, 6.05)),
    ("WC 2", box(0.09, 6.36, 2.91, 7.41), (1.45, 7.17)),
    ("Salle de lecture", box(3.09, 0.09, 6.51, 7.41).difference(box(5.61, 3.30, 6.51, 4.20)), (4.95, 5.35)),
]
surfaces = []
for nom, poly, (x, y) in ROOMS:
    a = poly.area
    surfaces.append((nom, a))
    room(x, y, nom, f"{a:.1f} m²".replace(".", ","), size=8.5 if "WC" not in nom else 7, inline="WC" in nom)
terr = box(0.0, -2.75, 6.6, 0.0)
room(3.0, -0.55, "Terrasse couverte", f"{terr.area:.1f} m²".replace(".", ","))
ax.text(3.3, -2.95, "PERGOLA — LAMES EN PROJECTION (POINTILLES)", fontsize=5.5, ha="center", color=GRIS)

# Flèche d'entrée
ax.add_patch(FancyArrowPatch((1.375, -0.75), (1.375, -0.12), arrowstyle="-|>", mutation_scale=9,
                             color=VERT, lw=1.2, zorder=9))
ax.text(1.28, -0.45, "ENTREE", fontsize=6.5, ha="right", va="center", color=VERT, zorder=9)

# Cotes extérieures
def cote(ax, p, q, off, txt, vertical=False):
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

cote(ax, (-0.09, 7.59), (6.69, 7.59), 0.25, "6,78")
cote(ax, (0.09, 7.59), (2.91, 7.59), 0.0, "")
cote(ax, (6.69, -0.09), (6.69, 7.59), 0.35, "7,68", vertical=True)
cote(ax, (6.69, -2.75), (6.69, -0.09), 0.35, "2,66", vertical=True)

# --- cartouche & légende (charte K&D) --------------------------------------
logo = plt.imread(LOGO)
lw_px, lh_px = logo.shape[1], logo.shape[0]
lax = fig.add_axes([16 / 420, (297 - 12 - 60 * lh_px / lw_px) / 297, 60 / 420, 60 * lh_px / lw_px / 297])
lax.imshow(logo); lax.axis("off")

X0 = 236 / 420
def T(y_mm, s, size, color=NOIR, **kw):
    fig.text(X0, 1 - y_mm / 297, s, fontsize=size, color=color, va="top", **kw)

T(16, "BIBLIOTHEQUE DECIMO", 22, GRIS)
T(27, "Plan du rez-de-chaussée — proposition d’aménagement intérieur", 12, VERT)
T(35, "Esquisse V2  ·  Échelle 1/50 (format A3)  ·  Coupe horizontale à +1,10 m", 8.5, GRIS)
fig.add_artist(plt.Line2D([X0, 404 / 420], [1 - 42 / 297] * 2, color=VERT, lw=1.2))

# Tableau des surfaces
T(50, "SURFACES INTERIEURES (ENV.)", 9, VERT)
y = 57
tot = 0
for nom, a in surfaces:
    T(y, nom, 8); fig.text(330 / 420, 1 - y / 297, f"{a:.1f} m²".replace(".", ","), fontsize=8, ha="right", va="top")
    tot += a; y += 5
fig.add_artist(Rectangle((X0 - 1 / 420, 1 - (y + 4.2) / 297), (330 - 235) / 420, 6 / 297,
                         transform=fig.transFigure, fc="#333333", ec="none"))
T(y + 0.4, "Total intérieur", 8, "white"); fig.text(329 / 420, 1 - (y + .4) / 297, f"{tot:.1f} m²".replace(".", ","), fontsize=8, ha="right", va="top", color="white")
y += 9
T(y, "Terrasse couverte (pergola)", 8, GRIS); fig.text(330 / 420, 1 - y / 297, f"{terr.area:.1f} m²".replace(".", ","), fontsize=8, ha="right", va="top", color=GRIS)

# Nomenclature mobilier
LIB = {
    "A01": "Fauteuil", "B01": "Rayonnage 800", "B02": "Banquette", "C01": "Chaise courbe",
    "C02": "Comptoir d’accueil", "M01": "Console vinyles", "T01": "Table de réunion 1300",
    "T02": "Table ronde",
}
y += 12
T(y, "MOBILIER SUR MESURE", 9, VERT); y += 7
for code in sorted(TAGS):
    fig.text(X0 + 2 / 420, 1 - (y + 1.2) / 297, code, fontsize=5.5, color="white", ha="center", va="center",
             bbox=dict(boxstyle="circle,pad=0.2", fc=VERT, ec="none"))
    fig.text(X0 + 7 / 420, 1 - y / 297, LIB.get(code, code), fontsize=8, color=NOIR, va="top")
    fig.text(330 / 420, 1 - y / 297, f"× {len(TAGS[code])}", fontsize=8, color=GRIS, va="top", ha="right")
    y += 5.2

# Légende graphique
y += 6
T(y, "LEGENDE", 9, VERT); y += 7
def leg(y, kind, txt):
    x = X0 + 1 / 420; w = 9 / 420; h = 3 / 297; yy = 1 - (y + 3) / 297
    if kind == "mur":
        fig.add_artist(Rectangle((x, yy), w, h, transform=fig.transFigure, fc="#3A3F44", ec=NOIR, lw=.4))
    elif kind == "verre":
        fig.add_artist(Rectangle((x, yy + h / 3), w, h / 3, transform=fig.transFigure, fc="#DCEBF0", ec=NOIR, lw=.4))
    elif kind == "proj":
        fig.add_artist(plt.Line2D([x, x + w], [yy + h / 2] * 2, color=GRIS, lw=.5, ls=(0, (3, 2))))
    elif kind == "mit":
        fig.add_artist(Rectangle((x, yy), w, h, transform=fig.transFigure, fc="white", ec=GRIS, lw=.3, hatch="////"))
    fig.text(X0 + 13 / 420, 1 - y / 297, txt, fontsize=7.5, va="top", color=NOIR)
leg(y, "mur", "Maçonnerie agglos 15 cm enduite / cloison BA13 (coupée)"); y += 6
leg(y, "verre", "Vitrage — façade et cloison vitrée de la salle de réunion"); y += 6
leg(y, "proj", "Éléments au-dessus du plan de coupe (pergola, luminaires, faux plafond)"); y += 6
leg(y, "mit", "Bâtiment mitoyen"); y += 6

# Pied de cartouche
fig.add_artist(plt.Line2D([X0, 404 / 420], [1 - 268 / 297] * 2, color=GRIS, lw=.4))
fig.text(X0, 1 - 272 / 297, "Source : maquette DECIMO_ESQ_V2.ifc (Revit 2025) — niveau N00 _ RDC", fontsize=6.5, color=GRIS, va="top")
fig.text(X0, 1 - 277 / 297, "Document d’esquisse — dimensions et surfaces indicatives, à vérifier sur site.", fontsize=6.5, color=GRIS, va="top")
fig.text(404 / 420, 1 - 272 / 297, "Octobre 2026", fontsize=6.5, color=GRIS, va="top", ha="right")
fig.text(404 / 420, 1 - 277 / 297, "PLAN RDC — ESQ V2", fontsize=6.5, color=VERT, va="top", ha="right")

# Échelle graphique
sx, sy = XMIN + 0.1, YMIN + 0.05
for i in range(4):
    ax.add_patch(Rectangle((sx + i, sy), 1, 0.08, fc=NOIR if i % 2 == 0 else "white", ec=NOIR, lw=.3, zorder=9))
    ax.text(sx + i, sy + 0.14, str(i), fontsize=5.5, ha="center", color=GRIS)
ax.text(sx + 4, sy + 0.14, "4 m", fontsize=5.5, ha="center", color=GRIS)

fig.savefig(OUT + ".pdf")
fig.savefig(OUT + ".png", dpi=200)
print("ok", TAGS.keys(), surfaces)
