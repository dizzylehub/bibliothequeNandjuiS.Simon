"""Proposition V4 — pages 2 (élévations) et 3 (matériaux, textures, références)."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, PathPatch, Circle, Polygon as MPoly
from matplotlib.path import Path

LOGO = "/root/.claude/skills/synced/68b949f7-29fd-4b06-8f9e-f06c81c76d86_30805531-b9b3-4d6e-85e6-49dfe06bdd23/charte-kd/assets/Logo KDA.jpg"
FONT = "/tmp/claude-0/-home-user/5dfc2a2e-f67b-5d7c-bd12-e0811e213d4e/scratchpad/fonts/Questrial-Regular.ttf"
REF1 = "/tmp/claude-0/-home-user/5dfc2a2e-f67b-5d7c-bd12-e0811e213d4e/images/1.webp"
REF2 = "/tmp/claude-0/-home-user/5dfc2a2e-f67b-5d7c-bd12-e0811e213d4e/images/2.png"
OUT = sys.argv[1]
font_manager.fontManager.addfont(FONT)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=FONT).get_name()
plt.rcParams["pdf.fonttype"] = 42

NOIR, GRIS, VERT, GCLAIR = "#0B0C12", "#66747C", "#7AB648", "#F2F2F2"
# couleurs de projet (matériaux)
ENDUIT_BLANC, TERRA, TERRA_F, CLAUSTRA_FOND = "#F3EFE6", "#B4583E", "#8E3F2B", "#3B2A24"
IROKO, IROKO_C, ENDUIT_SABLE, ACIER, VITRE, LED = "#9A6B43", "#B8875A", "#E6D6BF", "#1E1E1E", "#CFE3EA", "#F2C46D"
GRES, TISSU, VEGETAL = "#D9CDB8", "#A9533A", "#5E8C4A"
MM = 1 / 25.4
lw_mid, lw_fine, lw_hair = 0.45, 0.25, 0.15
rng = np.random.default_rng(7)

def page():
    fig = plt.figure(figsize=(420 * MM, 297 * MM))
    logo = plt.imread(LOGO)
    lh = 60 * logo.shape[0] / logo.shape[1]
    lax = fig.add_axes([16 / 420, (297 - 12 - lh) / 297, 60 / 420, lh / 297]); lax.imshow(logo); lax.axis("off")
    return fig

def T(fig, x_mm, y_mm, s, size, color=NOIR, **kw):
    return fig.text(x_mm / 420, 1 - y_mm / 297, s, fontsize=size, color=color, va="top", **kw)

def drawing_axes(fig, x_mm, y_top_mm, xlim, ylim, scale):
    w = (xlim[1] - xlim[0]) * 1000 / scale
    h = (ylim[1] - ylim[0]) * 1000 / scale
    ax = fig.add_axes([x_mm / 420, (297 - y_top_mm - h) / 297, w / 420, h / 297])
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.axis("off")
    return ax

def footer(fig, ref):
    fig.add_artist(plt.Line2D([236 / 420, 404 / 420], [1 - 270 / 297] * 2, color=GRIS, lw=.4))
    T(fig, 236, 273, "Proposition V4 — à valider avant report dans la maquette DECIMO_ESQ_V3.ifc.", 6.2, GRIS)
    T(fig, 236, 278, "Document d’esquisse — dimensions indicatives, à vérifier sur site.", 6.2, GRIS)
    T(fig, 404, 278, ref, 6.2, VERT, ha="right")

def header(fig, sub, line):
    T(fig, 236, 16, "BIBLIOTHEQUE DECIMO", 22, GRIS)
    T(fig, 236, 27, sub, 12, VERT)
    T(fig, 236, 35, line, 8.5, GRIS)
    fig.add_artist(plt.Line2D([236 / 420, 404 / 420], [1 - 42 / 297] * 2, color=VERT, lw=1.2))

# --- formes cintrées ----------------------------------------------------------
def arch_path(x0, x1, z0, z_spring, n=48):
    r = (x1 - x0) / 2; c = (x0 + x1) / 2
    pts = [(x0, z0), (x1, z0), (x1, z_spring)]
    pts += [(c + r * np.cos(a), z_spring + r * np.sin(a)) for a in np.linspace(0, np.pi, n)]
    pts += [(x0, z_spring), (x0, z0)]
    return Path(pts, closed=True)

def pill_path(x0, x1, z0, z1, n=36):
    r = (x1 - x0) / 2; c = (x0 + x1) / 2
    pts = [(c + r * np.cos(a), z1 - r + r * np.sin(a)) for a in np.linspace(0, np.pi, n)]
    pts += [(c + r * np.cos(a), z0 + r + r * np.sin(a)) for a in np.linspace(np.pi, 2 * np.pi, n)]
    pts.append(pts[0])
    return Path(pts, closed=True)

def rounded_box_path(x0, x1, z0, z1, r, corner="tl", n=24):
    if corner == "tl":
        pts = [(x0, z0), (x1, z0), (x1, z1), (x0 + r, z1)]
        pts += [(x0 + r + r * np.cos(a), z1 - r + r * np.sin(a)) for a in np.linspace(np.pi / 2, np.pi, n)]
        pts += [(x0, z0)]
    return Path(pts, closed=True)

def claustra(ax, path, s=0.10, z=3):
    """Claustra terre cuite : anneaux reliés par des pontets, fond sombre (vides)."""
    bb = path.get_extents()
    clip = PathPatch(path, fc=CLAUSTRA_FOND, ec="none", zorder=z); ax.add_patch(clip)
    arts = []
    xs = np.arange(bb.x0 - s, bb.x1 + s, s); zs = np.arange(bb.y0 - s, bb.y1 + s, s)
    for x in xs:
        for zz in zs:
            arts.append(ax.add_patch(Circle((x, zz), s * 0.30, fc="none", ec=TERRA, lw=1.5, zorder=z + 1)))
            arts.append(ax.add_patch(Rectangle((x + s * 0.30, zz - s * 0.07), s * 0.40, s * 0.14, fc=TERRA, ec="none", zorder=z + 1)))
            arts.append(ax.add_patch(Rectangle((x - s * 0.07, zz + s * 0.30), s * 0.14, s * 0.40, fc=TERRA, ec="none", zorder=z + 1)))
            arts.append(ax.add_patch(Circle((x + s / 2, zz + s / 2), s * 0.09, fc=TERRA, ec="none", zorder=z + 1)))
    for a in arts:
        a.set_clip_path(clip)
    ax.add_patch(PathPatch(path, fc="none", ec=NOIR, lw=lw_mid, zorder=z + 2))

def books(ax, x0, x1, z0, h, z=4, clip=None):
    pal = [TERRA, "#C89B5B", "#7F8F6A", "#E9DFC9", "#5B4636", "#9EA7A0", "#D2B48C", "#6E2F25", "#C8C3B5"]
    x = x0 + 0.01
    while x < x1 - 0.02:
        w = rng.uniform(0.018, 0.045); hh = h * rng.uniform(0.68, 0.95)
        if rng.random() < 0.08:
            x += 0.04; continue
        p = ax.add_patch(Rectangle((x, z0), min(w, x1 - x - 0.005), hh, fc=pal[rng.integers(len(pal))],
                                   ec=NOIR, lw=0.08, zorder=z))
        if clip is not None:
            p.set_clip_path(clip)
        x += w + 0.002

def dim_v(ax, x, z0, z1, txt, side=1, color=GRIS):
    ax.plot([x, x], [z0, z1], color=color, lw=lw_fine)
    for zz in (z0, z1):
        ax.plot([x - .05, x + .05], [zz - .05, zz + .05], color=color, lw=lw_mid)
    ax.text(x + 0.06 * side, (z0 + z1) / 2, txt, rotation=90, fontsize=5.8, color=color,
            ha="left" if side > 0 else "right", va="center")

def dim_h(ax, x0, x1, z, txt, color=GRIS):
    ax.plot([x0, x1], [z, z], color=color, lw=lw_fine)
    for xx in (x0, x1):
        ax.plot([xx - .05, xx + .05], [z - .05, z + .05], color=color, lw=lw_mid)
    ax.text((x0 + x1) / 2, z + 0.05, txt, fontsize=5.8, color=color, ha="center", va="bottom")

def callout(ax, xy, xytext, txt, ha="left"):
    ax.annotate(txt, xy=xy, xytext=xytext, fontsize=5.8, color=NOIR, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=GRIS, lw=0.4, shrinkA=1, shrinkB=0), zorder=20,
                bbox=dict(fc="white", ec="none", pad=0.6, alpha=.9))

# =========================== PAGE 2 : ELEVATIONS ===============================
fig = page()
header(fig, "Façade et mur du fond — élévations de principe",
       "Esquisse V4  ·  Façade sud du RDC au 1/50  ·  Mur du fond de la salle de lecture au 1/25 (A3)")

# ---- façade sud, 1/50 ----
T(fig, 22, 38, "ELEVATION FACADE SUD — RDC  ·  1/50", 8.5, VERT)
ax = drawing_axes(fig, 22, 42, (-0.45, 7.05), (-0.30, 3.95), 50)
ax.add_patch(Rectangle((-0.45, -0.30), 0.36, 4.25, fc="white", ec=GRIS, lw=lw_fine, hatch="////", zorder=1))
ax.text(-0.27, 1.8, "MITOYEN", rotation=90, fontsize=5, color=GRIS, ha="center", va="center", zorder=2,
        bbox=dict(fc="white", ec="none", pad=0.6))
ax.add_patch(Rectangle((-0.09, 3.30), 6.78, 0.65, fc=GCLAIR, ec=GRIS, lw=lw_fine, zorder=1))
ax.text(3.3, 3.62, "ETAGE EXISTANT (NON MODIFIE)", fontsize=5, color=GRIS, ha="center", va="center", zorder=2)
ax.add_patch(Rectangle((-0.09, 0.0), 6.78, 3.30, fc=ENDUIT_BLANC, ec=NOIR, lw=lw_mid, zorder=2))
ax.plot([-0.45, 7.05], [0, 0], color=NOIR, lw=1.0, zorder=10)
ax.add_patch(Rectangle((-0.09, -0.10), 6.78, 0.10, fc=GRES, ec=NOIR, lw=lw_fine, zorder=9))
# baies cintrées à claustra
claustra(ax, arch_path(0.55, 1.75, 0.45, 1.95))
claustra(ax, pill_path(2.00, 2.70, 0.90, 2.40))
claustra(ax, pill_path(5.15, 6.25, 0.60, 2.50))
for pth in (arch_path(0.55, 1.75, 0.45, 1.95), pill_path(2.00, 2.70, 0.90, 2.40), pill_path(5.15, 6.25, 0.60, 2.50)):
    v = pth.vertices
    ax.plot(v[:, 0], v[:, 1], color=LED, lw=0.9, alpha=.8, zorder=6)     # LED en tableau
# portail d'entrée terre cuite
portal = rounded_box_path(3.20, 5.00, 0.0, 3.30, 0.45)
ax.add_patch(PathPatch(portal, fc=TERRA, ec=NOIR, lw=lw_mid, zorder=4))
door = arch_path(3.35, 4.85, 0.0, 2.05)
ax.add_patch(PathPatch(door, fc=VITRE, ec=ACIER, lw=1.6, zorder=5))
ax.plot(door.vertices[:, 0], door.vertices[:, 1], color=LED, lw=0.8, alpha=.8, zorder=6)
ax.plot([4.25, 4.25], [0.0, 2.05], color=ACIER, lw=1.3, zorder=6)                 # battement 0,90 / 0,60
ax.plot([3.35, 4.85], [2.05, 2.05], color=ACIER, lw=1.1, zorder=6)                # imposte
gridclip = PathPatch(arch_path(3.35, 4.85, 2.05, 2.05), fc="none", ec="none", zorder=6); ax.add_patch(gridclip)
for k in np.arange(-1.6, 1.7, 0.15):
    for sgn in (1, -1):
        l, = ax.plot([4.10 + k - 1.0, 4.10 + k + 1.0], [2.05 - sgn * 1.0, 2.05 + sgn * 1.0], color=ACIER, lw=0.5, zorder=6)
        l.set_clip_path(gridclip)
for xx in (4.18, 4.32):
    ax.plot([xx, xx], [0.95, 1.20], color=ACIER, lw=1.4, zorder=7)                # poignées
ax.text(4.10, 3.02, "DECIMO", fontsize=10, color="white", ha="center", va="center", zorder=7)
ax.text(4.10, 3.19, "BIBLIOTHEQUE", fontsize=4.2, color="white", ha="center", va="center", zorder=7)
# jardinières et végétation
for x0, x1 in ((0.35, 2.95), (5.05, 6.45)):
    ax.add_patch(Rectangle((x0, 0.0), x1 - x0, 0.45, fc=ENDUIT_BLANC, ec=NOIR, lw=lw_mid, zorder=8))
    ax.plot([x0, x1], [0.03, 0.03], color=LED, lw=0.8, alpha=.7, zorder=9)
    for xx in np.arange(x0 + 0.15, x1 - 0.05, 0.22):
        hgt = rng.uniform(0.35, 0.85)
        for k in range(7):
            a = np.radians(rng.uniform(35, 145))
            L = hgt * rng.uniform(0.6, 1.0)
            ax.add_patch(MPoly([(xx, 0.45), (xx + L * np.cos(a) * 0.5 - 0.03, 0.45 + L * np.sin(a) * 0.55),
                                (xx + L * np.cos(a), 0.45 + L * np.sin(a)),
                                (xx + L * np.cos(a) * 0.5 + 0.03, 0.45 + L * np.sin(a) * 0.45)],
                               closed=True, fc=VEGETAL, ec="#3F6332", lw=0.15, alpha=.9, zorder=9))
# pergola relevée (lames en coupe, transparente)
for xx in (0.25, 6.25):
    ax.add_patch(Rectangle((xx, 0.0), 0.08, 2.90, fc=IROKO, ec=NOIR, lw=lw_hair, alpha=.55, zorder=11))
ax.add_patch(Rectangle((-0.05, 2.90), 6.70, 0.10, fc=IROKO, ec=NOIR, lw=lw_hair, alpha=.45, zorder=11))
for xx in np.arange(0.0, 6.6, 0.11):
    hz = 0.10 + 0.16 * (0.5 + 0.5 * np.cos(2 * np.pi * (xx - 1.375) / 3.4))
    ax.add_patch(Rectangle((xx, 3.00), 0.034, hz, fc=IROKO, ec="none", alpha=.35, zorder=11))
# cotes
dim_v(ax, 6.85, 0.0, 3.30, "3,30")
dim_v(ax, 3.12, 0.0, 2.05, "passage 2,05", side=-1)
dim_v(ax, 5.07, 0.0, 2.80, "2,80", side=1)
dim_v(ax, 0.43, 0.45, 2.55, "2,10", side=-1)
dim_h(ax, 3.35, 4.85, -0.24, "1,50 (0,90 + 0,60)")
dim_h(ax, 0.55, 1.75, -0.24, "1,20")
dim_h(ax, 5.15, 6.25, -0.24, "1,10")
callout(ax, (1.15, 1.2), (0.70, 2.85), "Claustra terre cuite — motif anneaux", ha="center")
callout(ax, (2.35, 1.6), (2.35, 3.08), "Baie « pilule »", ha="center")
callout(ax, (3.6, 2.4), (5.80, 3.08), "Portail enduit terre cuite, angle arrondi", ha="center")
callout(ax, (6.0, 0.25), (6.30, 0.80), "Jardinière maçonnée", ha="center")

# ---- mur du fond, 1/25 ----
T(fig, 22, 136, "ELEVATION INTERIEURE — MUR DU FOND ET ARBRE A LIVRES  ·  1/25", 8.5, VERT)
bx = drawing_axes(fig, 22, 140, (2.80, 6.85), (-0.12, 3.40), 25)
bx.add_patch(Rectangle((2.91, -0.12), 0.18, 3.52, fc="#3A3F44", ec=NOIR, lw=lw_mid, zorder=2))
bx.add_patch(Rectangle((6.51, -0.12), 0.18, 3.52, fc="#3A3F44", ec=NOIR, lw=lw_mid, zorder=2))
bx.add_patch(Rectangle((3.09, 3.30), 3.42, 0.10, fc="#3A3F44", ec=NOIR, lw=lw_mid, zorder=2))
bx.add_patch(Rectangle((3.09, -0.12), 3.42, 0.12, fc=GRES, ec=NOIR, lw=lw_fine, zorder=2))
bx.add_patch(Rectangle((3.09, 0.0), 3.42, 3.30, fc=ENDUIT_SABLE, ec=NOIR, lw=lw_fine, zorder=1))
NICHES = [(3.20, 4.10, 1.95, "biblio"), (4.18, 5.43, 1.80, "banc"), (5.51, 6.41, 1.95, "biblio")]
for x0, x1, zs, kind in NICHES:
    pth = arch_path(x0, x1, 0.10, zs)
    clip = PathPatch(pth, fc="#7C5A3C", ec=NOIR, lw=lw_mid, zorder=3); bx.add_patch(clip)
    if kind == "biblio":
        for zz in np.arange(0.10, zs + 0.35, 0.36):
            s = bx.add_patch(Rectangle((x0, zz), x1 - x0, 0.025, fc=IROKO_C, ec=NOIR, lw=0.1, zorder=5)); s.set_clip_path(clip)
            books(bx, x0 + 0.01, x1 - 0.01, zz + 0.025, 0.30, z=4, clip=clip)
    else:
        for xx in np.arange(x0 + 0.02, x1, 0.05):                                    # fond en lames bois
            l, = bx.plot([xx, xx], [0.10, 2.5], color=IROKO_C, lw=1.1, zorder=4); l.set_clip_path(clip)
        bx.add_patch(Rectangle((x0, 0.10), x1 - x0, 0.33, fc=IROKO, ec=NOIR, lw=lw_fine, zorder=5))
        bx.add_patch(Rectangle((x0 + 0.03, 0.43), x1 - x0 - 0.06, 0.10, fc=TISSU, ec=NOIR, lw=lw_fine, zorder=5))
        bx.add_patch(Rectangle((x0 + 0.05, 0.53), x1 - x0 - 0.10, 0.30, fc="#C46A4E", ec=NOIR, lw=lw_hair, zorder=5))
        bx.add_patch(Rectangle((x0, 1.50), x1 - x0, 0.025, fc=IROKO_C, ec=NOIR, lw=0.1, zorder=5))
        books(bx, x0 + 0.05, x0 + 0.45, 1.525, 0.26, z=5)
    v = pth.vertices
    bx.plot(v[2:-2, 0], v[2:-2, 1] - 0.02, color=LED, lw=1.0, alpha=.85, zorder=6)
    bx.add_patch(Rectangle((x0, 0.0), x1 - x0, 0.10, fc=IROKO, ec=NOIR, lw=lw_fine, zorder=5))

# arbre à livres (devant la niche centrale)
CX = 4.75
for i, zz in enumerate(np.arange(0.10, 2.40, 0.33)):
    bx.add_patch(Rectangle((CX - 0.45, zz), 0.90, 0.03, fc=IROKO, ec=NOIR, lw=lw_fine, zorder=8))
    if zz + 0.33 <= 2.42:
        books(bx, CX - 0.43, CX + 0.43, zz + 0.03, 0.28, z=7)
bx.add_patch(Rectangle((CX - 0.40, 0.0), 0.80, 0.10, fc=IROKO, ec=NOIR, lw=lw_fine, zorder=8))
zc = np.linspace(2.40, 3.30, 40)
rc = 0.45 + 0.85 * ((zc - 2.40) / 0.90) ** 2.2
canopy = np.concatenate([np.c_[CX - rc, zc], np.c_[CX + rc[::-1], zc[::-1]]])
cp = bx.add_patch(MPoly(canopy, closed=True, fc=IROKO, ec=NOIR, lw=lw_mid, zorder=9))
for k in np.linspace(-1, 1, 17):                                                   # lamelles cintrées
    xs_ = CX + k * rc
    l, = bx.plot(xs_, zc, color=IROKO_C, lw=0.5, zorder=9); l.set_clip_path(cp)
bx.add_patch(Rectangle((CX - 0.47, 2.37), 0.94, 0.04, fc=IROKO_C, ec=NOIR, lw=lw_fine, zorder=9))
for xx in np.linspace(CX - 1.18, CX + 1.18, 9):
    bx.add_patch(Circle((xx, 3.28 - 0.0), 0.018, fc=LED, ec="none", zorder=10))
# cotes
dim_v(bx, 6.75, 0.0, 3.30, "3,30 plafond")

dim_v(bx, CX - 0.62, 0.0, 2.40, "2,40", side=-1)
dim_v(bx, 4.30, 0.0, 0.45, "0,45", side=-1)
dim_h(bx, 3.20, 4.10, -0.09, "0,90")
dim_h(bx, 5.51, 6.41, -0.09, "0,90")
dim_h(bx, CX - 0.45, CX + 0.45, -0.09, "Ø 0,90")
callout(bx, (3.65, 1.30), (3.15, 2.85), "Niche bibliothèque — iroko,\ntablettes tous les 36 cm", ha="left")
callout(bx, (5.30, 0.70), (6.05, 2.85), "Banquette de lecture,\ncoussin tissu terre cuite", ha="left")
callout(bx, (CX + 0.30, 2.90), (5.85, 3.20), "Canopée en lamelles d’iroko cintrées,\nanneau de spots LED 2700 K", ha="left")
callout(bx, (CX + 0.40, 1.20), (5.95, 1.65), "Arbre à livres :\n7 plateaux tournants Ø 0,90", ha="left")

# ---- texte de la page 2 ----
y = 50
T(fig, 236, y, "FACADE — PRINCIPES", 9, VERT); y += 7
for s in ["Un portail terre cuite signale l’entrée ; il intègre l’enseigne\nDECIMO et une double porte vitrée cintrée en acier noir.",
          "Entrée et sortie fluides : 1,50 m de passage (0,90 + 0,60),\nvantaux ouvrant vers l’extérieur, seuil plat, aire Ø 1,50.",
          "Les claustras ne ferment que les baies d’éclairage :\nl’arc A et la « pilule » B (coin lecture), la pilule C (accueil).",
          "Claustra terre cuite à motif d’anneaux : ombre, ventilation\net intimité, en écho à la référence fournie.",
          "Jardinières maçonnées au pied des baies, éclairage LED\nrasant en tableau des arcs et en pied de jardinière.",
          "La pergola est relevée à +2,90 (au lieu de +2,65) pour\ndégager l’arc de l’entrée (sommet à 2,80)."]:
    T(fig, 236, y, "—", 7.2, GRIS); T(fig, 241, y, s, 7.2, linespacing=1.3); y += 4.3 * (s.count("\n") + 1) + 2.6
y += 3
T(fig, 236, y, "INTERIEUR — PRINCIPES", 9, VERT); y += 7
for s in ["L’arbre à livres, inspiré de la référence, est placé au fond :\nc’est le seul endroit où l’on garde 0,90 m de passage tout autour.",
          "Sa canopée en bois cintré s’évase de Ø 0,90 à Ø 2,60 et\nporte l’éclairage ; 2,40 m libres sous la canopée.",
          "Le mur du fond devient 3 niches cintrées : 2 bibliothèques\net une banquette de lecture à fond en lames bois.",
          "Les arcs des niches répondent à ceux de la façade :\nune seule écriture cintrée, du dehors au dedans.",
          "Les rails lumineux s’arrêtent avant la canopée."]:
    T(fig, 236, y, "—", 7.2, GRIS); T(fig, 241, y, s, 7.2, linespacing=1.3); y += 4.3 * (s.count("\n") + 1) + 2.6
footer(fig, "ELEVATIONS — ESQ V4  ·  Octobre 2026")
fig.savefig(OUT + "_p2.pdf"); fig.savefig(OUT + "_p2.png", dpi=170)
plt.close(fig)

# =========================== PAGE 3 : MATERIAUX ================================
fig = page()
header(fig, "Matériaux, textures et références",
       "Esquisse V4  ·  Palette à reporter dans la maquette IFC (styles de surface et matériaux)")

def tex_noise(base, amp=0.035, n=140, seed=0):
    r = np.random.default_rng(seed)
    c = np.array(matplotlib.colors.to_rgb(base))
    img = c + (r.normal(0, amp, (n, n, 1)))
    return np.clip(img, 0, 1)

def tex_wood(base, n=200, seed=1):
    r = np.random.default_rng(seed)
    c = np.array(matplotlib.colors.to_rgb(base))
    y, x = np.mgrid[0:n, 0:n] / n
    g = (np.sin((x * 11 + 0.35 * np.sin(y * 2.3 + r.uniform(0, 6)) + 0.12 * np.sin(y * 9)) * np.pi) * 0.5 + 0.5) ** 3
    img = c * (0.82 + 0.22 * g[..., None]) + r.normal(0, 0.012, (n, n, 1))
    return np.clip(img, 0, 1)

def tex_tiles(base, n=200):
    img = tex_noise(base, 0.02, n, 3)
    for k in range(0, n, n // 3):
        img[k:k + 2, :] = 0.62; img[:, k:k + 2] = 0.62
    return img

def tex_weave(base, n=200):
    c = np.array(matplotlib.colors.to_rgb(base))
    y, x = np.mgrid[0:n, 0:n]
    g = ((x // 4 + y // 4) % 2) * 0.08
    return np.clip(c * (0.9 + g[..., None]), 0, 1)

def tex_led(n=200):
    y, x = np.mgrid[0:n, 0:n] / n
    d = np.exp(-((x - 0.5) ** 2 + (y - 0.5) ** 2) * 6)
    c1 = np.array(matplotlib.colors.to_rgb("#3A3530")); c2 = np.array(matplotlib.colors.to_rgb(LED))
    return c1 * (1 - d[..., None]) + c2 * d[..., None]

MATS = [
    ("Enduit à la chaux blanc cassé", "Façade RDC, jardinières", "Taloché fin, mat", "KDA - Enduit chaux blanc", lambda: tex_noise(ENDUIT_BLANC, 0.02)),
    ("Enduit terre cuite", "Portail d’entrée", "Teinté masse, mat", "KDA - Enduit terre cuite", lambda: tex_noise(TERRA, 0.035, seed=2)),
    ("Claustra terre cuite", "Baies cintrées A, B, C", "Motif anneaux, 20 x 20 cm", "KDA - Claustra terre cuite", None),
    ("Acier thermolaqué noir", "Menuiseries, porte d’entrée", "Noir mat, profils fins", "KDA - Acier noir mat", lambda: tex_noise(ACIER, 0.015, seed=4)),
    ("Iroko huilé", "Arbre à livres, niches, comptoir, M01", "Huile naturelle, teinte miel", "KDA - Bois iroko huilé", lambda: tex_wood(IROKO)),
    ("Enduit chaux sable", "Murs intérieurs, doublage des niches", "Ciré, aspect tadelakt", "KDA - Enduit chaux sable", lambda: tex_noise(ENDUIT_SABLE, 0.025, seed=5)),
    ("Grès cérame sable 60 x 60", "Sol intérieur et terrasse", "Mat, R10 en terrasse", "KDA - Grès cérame sable", lambda: tex_tiles(GRES)),
    ("Tissu terre cuite", "Coussins de la banquette", "Bouclette, non feu M1", "KDA - Tissu terre cuite", lambda: tex_weave(TISSU)),
    ("Végétal", "Jardinières de façade, plante", "Essences locales", "KDA - Végétal", lambda: tex_noise(VEGETAL, 0.06, seed=6)),
    ("LED 2700 K", "Arcs, niches, canopée, jardinières", "Rubans et spots, IRC > 90", "KDA - Lumière chaude", tex_led),
]
T(fig, 22, 38, "PALETTE MATERIAUX", 9, VERT)
cols, cw, chh, gx, gy = 5, 38, 30, 4, 25
for i, (nom, usage, fin, ifc, tex) in enumerate(MATS):
    r_, c_ = divmod(i, cols)
    x = 22 + c_ * (cw + gx); y = 44 + r_ * (chh + gy)
    sax = fig.add_axes([x / 420, (297 - y - chh) / 297, cw / 420, chh / 297]); sax.axis("off")
    if tex is None:
        sax.set_xlim(0, 0.8); sax.set_ylim(0, 0.63); sax.set_aspect("auto")
        claustra(sax, Path([(0, 0), (0.8, 0), (0.8, 0.63), (0, 0.63), (0, 0)], closed=True), s=0.2)
    else:
        sax.imshow(tex(), aspect="auto", interpolation="bilinear")
    sax.add_patch(Rectangle((0, 0), 1, 1, transform=sax.transAxes, fc="none", ec=GRIS, lw=0.4))
    T(fig, x, y + chh + 2.5, nom, 7.4)
    T(fig, x, y + chh + 7.0, usage, 6.2, GRIS)
    T(fig, x, y + chh + 10.6, fin, 6.2, GRIS)
    T(fig, x, y + chh + 14.2, ifc, 5.6, VERT)

y0 = 44 + 2 * (chh + gy) + 4
T(fig, 22, y0, "REFERENCES FOURNIES", 9, VERT)
for k, (pth, cap, w) in enumerate([(REF1, "Intérieur : arbre à livres, canopée bois, niches cintrées", 50),
                                    (REF2, "Façade : baies cintrées à claustra terre cuite, portail", 98)]):
    img = plt.imread(pth) if not pth.endswith(".webp") else np.asarray(__import__("PIL.Image", fromlist=["Image"]).open(pth).convert("RGB"))
    hmm = 75
    x = 22 + (0 if k == 0 else 58)
    rax = fig.add_axes([x / 420, (297 - y0 - 6 - hmm) / 297, w / 420, hmm / 297]); rax.axis("off")
    rax.imshow(img, aspect="auto")
    T(fig, x, y0 + 6 + hmm + 2.5, cap, 6.2, GRIS)

y = 50
T(fig, 236, y, "INTENTION", 9, VERT); y += 7
for s in ["Deux familles de matières, chaudes et locales : la terre cuite\nen façade, l’iroko et l’enduit sable à l’intérieur.",
          "La terre cuite passe du claustra au portail ; à l’intérieur,\nelle revient en touches (coussins, dos de livres).",
          "L’iroko, essence africaine durable, fédère le mobilier sur\nmesure : arbre à livres, niches, comptoir, console M01.",
          "Lumière chaude 2700 K intégrée aux formes cintrées,\nsans luminaire apparent hors rails existants."]:
    T(fig, 236, y, "—", 7.2, GRIS); T(fig, 241, y, s, 7.2, linespacing=1.3); y += 4.3 * (s.count("\n") + 1) + 2.6
y += 3
T(fig, 236, y, "REPORT DANS LA MAQUETTE IFC (ETAPE SUIVANTE)", 9, VERT); y += 7
for s in ["Chaque matière devient un IfcMaterial associé aux éléments\net un style de surface (couleur, réflectance) lisible par les\nvisionneuses ; les textures image sont jointes en option.",
          "Murs, sols et menuiseries existants reçoivent la palette ;\nles nouveaux éléments (arbre, niches, portail, claustras,\njardinières) sont modélisés avec leur matière.",
          "Les noms en vert sont les styles qui seront créés."]:
    T(fig, 236, y, "—", 7.2, GRIS); T(fig, 241, y, s, 7.2, linespacing=1.3); y += 4.3 * (s.count("\n") + 1) + 2.6
footer(fig, "MATERIAUX — ESQ V4  ·  Octobre 2026")
fig.savefig(OUT + "_p3.pdf"); fig.savefig(OUT + "_p3.png", dpi=170)
print("ok")
