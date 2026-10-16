"""Fiches mobilier V8 (Désiré Akai) : six pièces signature du café-bibliothèque.

Chaque pièce est un modèle d'étude en volumes simples (boîtes et barres), en mètres :
x = largeur, y = profondeur (0 = face avant), z = hauteur. Les vues de dessus, de face et
de côté sont cotées ; l'axonométrie est calculée depuis les mêmes volumes.
Statut : modèles d'étude à prototyper avec les artisans, pas des plans de fabrication.

Usage : python3 v8/scripts/mobilier.py  ->  v8/mobilier/M01..M06_*.svg
"""
import math
import os

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "..", "mobilier")
FONT = "Archivo, Helvetica, Arial, sans-serif"
INK, GRIS, ORANGE = "#2a2622", "#8b8a86", "#b0582b"
C = {"noyer": "#7a4a2a", "noyer clair": "#a8754a", "cognac": "#a85f2c", "olive": "#56613a", "creme": "#efe4cc",
     "laiton": "#c9a227", "verre": "#9cc9d3", "canne": "#d9b878", "acier": "#2b2b2b", "corde": "#3f7a6a", "moutarde": "#c9962e", "contreplaque": "#d8b98a", "terre": "#b5603a", "livre1": "#2b4c7e", "livre2": "#8a3b2e", "livre3": "#c9962e", "feutre": "#56613a"}


def B(x0, y0, z0, x1, y1, z1, m):
    return ("b", min(x0, x1), min(y0, y1), min(z0, z1), max(x0, x1), max(y0, y1), max(z0, z1), m)


def R(p, q, m, e=0.035):
    return ("r", p, q, m, e)


# ------------------------------------------------------------------ pièces
def comptoir():
    W, D = 1.10, 0.65
    v = [B(0.02, 0.04, 0.15, W - 0.02, D, 1.01, "noyer"), B(-0.03, -0.02, 1.01, W + 0.03, D + 0.02, 1.05, "noyer clair"),
         B(0.02, D - 0.30, 0.15, W - 0.02, D, 0.75, "creme")]
    x = 0.04
    while x < W - 0.06:
        v.append(B(x, 0.0, 0.17, x + 0.028, 0.04, 0.99, "noyer clair"))
        x += 0.05
    for (px, py) in ((0.07, 0.10), (W - 0.12, 0.10), (0.07, D - 0.10), (W - 0.12, D - 0.10)):
        v.append(B(px, py, 0, px + 0.05, py + 0.05, 0.15, "noyer"))
    v.append(B(0.0, -0.03, 0.30, W, -0.01, 0.32, "laiton"))
    return v


def module_collection():
    W, D, H = 0.80, 0.35, 2.90
    v = [B(0, 0.02, 0, 0.025, D, H, "noyer"), B(W - 0.025, 0.02, 0, W, D, H, "noyer"), B(0.025, D - 0.015, 0.08, W - 0.025, D, H, "creme"),
         B(0.04, 0.06, 0, W - 0.04, D - 0.02, 0.08, "noyer")]
    for z in (0.08, 0.46, 0.84, 1.66, 2.08, 2.48, H - 0.025):
        v.append(B(0.025, 0.02, z, W - 0.025, D - 0.015, z + 0.025, "noyer clair"))
    # niche-vitrine fermée entre 0,86 et 1,66 : fond laiton, portes vitrées
    v.append(B(0.025, 0.02, 0.84, W - 0.025, D - 0.015, 0.865, "noyer clair"))
    v.append(B(0.03, D - 0.03, 0.865, W - 0.03, D - 0.015, 1.66, "laiton"))
    v.append(B(0.03, 0.0, 0.865, W / 2 - 0.005, 0.012, 1.66, "verre"))
    v.append(B(W / 2 + 0.005, 0.0, 0.865, W - 0.03, 0.012, 1.66, "verre"))
    return v


def banquette_table():
    v = []
    L = 2.80
    v += [B(0.05, 0.08, 0, L - 0.05, 0.50, 0.20, "noyer"), B(0, 0.0, 0.20, L, 0.50, 0.45, "cognac"), B(0, 0.38, 0.45, L, 0.50, 0.90, "cognac")]
    for k in range(1, 5):
        x = L * k / 5
        v.append(B(x - 0.006, 0.37, 0.48, x + 0.006, 0.38, 0.87, "noyer"))
    # table 2,50 x 0,80 posée devant la banquette (y négatif = vers la salle)
    tx0, tx1, ty0, ty1 = 0.15, 2.65, -0.85, -0.05
    v.append(B(tx0, ty0, 0.71, tx1, ty1, 0.75, "noyer clair"))
    for xa in (tx0 + 0.25, tx1 - 0.25):
        v.append(R((xa, ty0 + 0.08, 0), (xa, (ty0 + ty1) / 2, 0.71), "noyer", 0.045))
        v.append(R((xa, ty1 - 0.08, 0), (xa, (ty0 + ty1) / 2, 0.71), "noyer", 0.045))
        v.append(B(xa - 0.03, ty0 + 0.08, 0.66, xa + 0.03, ty1 - 0.08, 0.71, "noyer"))
    v.append(B(tx0 + 0.25, (ty0 + ty1) / 2 - 0.02, 0.40, tx1 - 0.25, (ty0 + ty1) / 2 + 0.02, 0.44, "noyer"))
    return v


def fauteuil():
    W, D = 0.66, 0.76
    v = []
    for x in (0.03, W - 0.03):
        v.append(R((x, 0.06, 0), (x, 0.44, 0.40), "noyer", 0.045))
        v.append(R((x, D - 0.04, 0), (x, 0.30, 0.40), "noyer", 0.045))
        v.append(R((x, 0.04, 0.40), (x, 0.64, 0.40), "noyer", 0.04))
        v.append(R((x, 0.02, 0.58), (x, 0.50, 0.58), "noyer", 0.035))
        v.append(R((x, 0.50, 0.58), (x, 0.40, 0.40), "noyer", 0.035))
        v.append(R((x, 0.62, 0.36), (x, D - 0.02, 0.80), "noyer", 0.04))
    v.append(B(0.05, 0.04, 0.36, W - 0.05, 0.62, 0.40, "canne"))
    v.append(B(0.07, 0.06, 0.40, W - 0.07, 0.60, 0.50, "cognac"))
    v.append(B(0.07, 0.60, 0.48, W - 0.07, 0.72, 0.80, "cognac"))
    return v


def chaise():
    W, D = 0.48, 0.50
    v = []
    for x in (0.02, W - 0.02):
        v.append(R((x, 0.02, 0), (x, 0.04, 0.44), "noyer", 0.035))
        v.append(R((x, D - 0.02, 0), (x, D - 0.06, 0.78), "noyer", 0.035))
    v.append(B(0.0, 0.0, 0.42, W, D - 0.04, 0.45, "noyer"))
    v.append(B(0.03, 0.03, 0.445, W - 0.03, D - 0.07, 0.46, "canne"))
    v.append(B(0.0, D - 0.08, 0.66, W, D - 0.04, 0.76, "noyer"))
    v.append(R((W / 2, D - 0.06, 0.46), (W / 2, D - 0.06, 0.66), "noyer", 0.04))
    return v


def fauteuil_exterieur():
    W, D = 0.72, 0.74
    v = []
    for x in (0.02, W - 0.02):
        v.append(R((x, 0.04, 0), (x, 0.10, 0.36), "acier", 0.022))
        v.append(R((x, D - 0.04, 0), (x, 0.58, 0.36), "acier", 0.022))
        v.append(R((x, 0.04, 0.36), (x, 0.62, 0.36), "acier", 0.022))
        v.append(R((x, 0.62, 0.36), (x, D - 0.02, 0.74), "acier", 0.022))
        v.append(R((x, 0.10, 0.58), (x, 0.66, 0.58), "acier", 0.022))
    # tressage de cordelette (nylon d'extérieur) : assise et dossier
    for k in range(9):
        y = 0.08 + k * 0.06
        v.append(R((0.03, y, 0.36), (W - 0.03, y, 0.36), "corde", 0.012))
    for k in range(6):
        t = (k + 0.5) / 6
        v.append(R((0.03, 0.62 + 0.10 * t, 0.36 + 0.38 * t), (W - 0.03, 0.62 + 0.10 * t, 0.36 + 0.38 * t), "corde", 0.012))
    v.append(B(0.06, 0.08, 0.37, W - 0.06, 0.58, 0.45, "creme"))
    return v


def overallt():
    """Volume d'encombrement seulement : la géométrie réelle du modèle n'est pas relevée."""
    W, D = 0.70, 0.65
    v = [B(0, 0, 0, 0.018, D, 0.50, "contreplaque"), B(W - 0.018, 0, 0, W, D, 0.50, "contreplaque"),
         B(0.018, 0.04, 0.27, W - 0.018, 0.55, 0.30, "contreplaque"), B(0.018, 0.52, 0.30, W - 0.018, 0.56, 0.63, "contreplaque"),
         B(0.05, 0.06, 0.30, W - 0.05, 0.50, 0.38, "creme"), B(0.05, 0.44, 0.38, W - 0.05, 0.52, 0.60, "creme")]
    return v


# ------------------------------------------------------------------ variantes (indice B, 16/10)
LIVRES = ("livre1", "livre2", "livre3", "noyer clair", "creme")


def _livres(x0, x1, y0, z0, h, graine, remplissage=0.8):
    """Rangée de livres vus de dos, en blocs de couleur."""
    v, x, k = [], x0 + 0.01, graine
    while x < x0 + (x1 - x0) * remplissage:
        w = 0.025 + (k * 7 % 5) * 0.008
        hh = h * (0.72 + (k * 3 % 4) * 0.07)
        v.append(B(x, y0 + 0.03, z0, x + w, y0 + 0.24, z0 + hh, LIVRES[k % len(LIVRES)]))
        x += w + 0.003
        k += 1
    return v


def bibli_kente(n=3, W=0.80, H=2.90, echelle=True, livres=True):
    """Modules de 0,80 : tablettes décalées d'un module à l'autre et fonds colorés en bandes, comme un pagne tissé."""
    D = 0.35
    pas = 0.42
    niv = {}
    for i in range(n):
        dec = 0.21 if i % 2 else 0.0
        zs = [0.08] + [z for z in (0.08 + dec + pas * k for k in range(1, 8)) if z < H - 0.28]
        niv[i] = zs
    fonds = ["creme", "moutarde", "creme", "olive", "creme", "cognac", "creme"]
    v = []
    for i in range(n):
        x0 = i * W
        v.append(B(x0, 0.02, 0, x0 + 0.025, D, H, "noyer"))
        zs = niv[i] + [H - 0.025]
        for j, z in enumerate(zs):
            v.append(B(x0 + 0.025, 0.02, z, x0 + W, D - 0.015, z + 0.025, "noyer clair"))
            if j < len(zs) - 1:
                z1 = zs[j + 1]
                v.append(B(x0 + 0.025, D - 0.015, z + 0.025, x0 + W, D, z1, fonds[(j + i * 2) % len(fonds)]))
                if livres and (i + j) % 3 != 1 and z1 - z > 0.25:
                    v += _livres(x0 + 0.03, x0 + W - 0.01, 0.02, z + 0.025, min(0.30, z1 - z - 0.06), i * 7 + j)
    v.append(B(n * W - 0.025, 0.02, 0, n * W, D, H, "noyer"))
    v.append(B(0, 0.06, 0, n * W, D - 0.02, 0.08, "noyer"))
    if not echelle:
        return v
    # échelle en laiton sur rail
    v.append(R((0.0, -0.03, 2.72), (n * W, -0.03, 2.72), "laiton", 0.02))
    for x in (1.05, 1.45):
        v.append(R((x, -0.55, 0), (x, -0.04, 2.72), "laiton", 0.03))
    for k in range(1, 8):
        t = k / 8
        v.append(R((1.05, -0.55 + 0.51 * t, 2.72 * t), (1.45, -0.55 + 0.51 * t, 2.72 * t), "noyer", 0.025))
    return v


def bibli_claustra():
    """Grille de casiers de 0,40 : certaines cases fermées par du cannage ou un claustra en terre cuite."""
    v = []
    cols, rows, c = 6, 7, 0.40
    D = 0.35
    for i in range(cols + 1):
        v.append(B(i * c, 0.02, 0.08, i * c + 0.02, D, 0.08 + rows * c + 0.02, "noyer"))
    for j in range(rows + 1):
        v.append(B(0, 0.02, 0.08 + j * c, cols * c + 0.02, D, 0.08 + j * c + 0.02, "noyer"))
    v.append(B(0, D - 0.015, 0.08, cols * c + 0.02, D, 0.08 + rows * c, "creme"))
    for i in range(cols):
        for j in range(rows):
            x0, z0 = i * c + 0.02, 0.08 + j * c + 0.02
            k = (i * 5 + j * 3) % 7
            if k == 0:
                v.append(B(x0 + 0.01, 0.0, z0 + 0.01, x0 + c - 0.03, 0.015, z0 + c - 0.03, "canne"))
            elif k == 3:
                v.append(B(x0 + 0.01, 0.0, z0 + 0.01, x0 + c - 0.03, 0.015, z0 + c - 0.03, "terre"))
            elif k in (1, 4, 6):
                v += _livres(x0, x0 + c - 0.02, 0.02, z0, 0.28, i + j)
    v.append(B(0.02, 0.06, 0, cols * c, D - 0.02, 0.08, "noyer"))
    return v


def bibli_lutrin():
    """Rayonnage continu, bandeau-lutrin à hauteur des yeux pour présenter les livres de face, niches-vitrines."""
    W, D, H = 2.40, 0.35, 2.90
    v = [B(0, 0.02, 0, 0.025, D, H, "noyer"), B(W - 0.025, 0.02, 0, W, D, H, "noyer"), B(1.19, 0.02, 0, 1.215, D, H, "noyer"),
         B(0.025, D - 0.015, 0.08, W - 0.025, D, H, "creme"), B(0.04, 0.06, 0, W - 0.04, D - 0.02, 0.08, "noyer")]
    for z in (0.08, 0.48, 0.88, 1.75, 2.15, 2.55, H - 0.025):
        v.append(B(0.025, 0.02, z, W - 0.025, D - 0.015, z + 0.025, "noyer clair"))
        if z < 2.8:
            v += _livres(0.03, W - 0.03, 0.02, z + 0.025, 0.30, int(z * 10))
    # bandeau-lutrin incliné (approché par deux gradins) avec couvertures de face
    v.append(B(0.025, -0.10, 1.10, W - 0.025, 0.02, 1.14, "noyer"))
    v.append(B(0.025, -0.04, 1.40, W - 0.025, 0.02, 1.44, "noyer"))
    for k in range(7):
        x = 0.10 + k * 0.32
        v.append(B(x, -0.07, 1.14, x + 0.22, -0.05, 1.42, LIVRES[k % 3]))
    v.append(B(0.03, 0.0, 1.46, 1.18, 0.012, 1.74, "verre"))
    v.append(B(1.225, 0.0, 1.46, W - 0.03, 0.012, 1.74, "verre"))
    return v


def accueil_enfilade():
    return comptoir()


def accueil_secretaire():
    """Comptoir avec gradin à livres côté client et cabinet à rideau à lattes qui ferme le café le soir."""
    W, D = 1.10, 0.65
    v = [B(0.02, 0.04, 0.15, W - 0.02, D, 1.01, "noyer"), B(-0.03, -0.02, 1.01, W + 0.03, D + 0.02, 1.05, "noyer clair")]
    x = 0.04
    while x < W - 0.06:
        v.append(B(x, 0.0, 0.17, x + 0.028, 0.04, 0.99, "noyer clair"))
        x += 0.05
    for (px, py) in ((0.07, 0.10), (W - 0.12, 0.10), (0.07, D - 0.10), (W - 0.12, D - 0.10)):
        v.append(B(px, py, 0, px + 0.05, py + 0.05, 0.15, "noyer"))
    v.append(B(0.0, -0.03, 0.30, W, -0.01, 0.32, "laiton"))
    # gradin à livres « le livre du jour »
    v.append(B(0.05, -0.02, 1.05, 0.72, 0.16, 1.09, "noyer"))
    v.append(B(0.05, 0.10, 1.09, 0.72, 0.16, 1.26, "noyer"))
    for k in range(3):
        x = 0.09 + k * 0.21
        v.append(B(x, 0.06, 1.09, x + 0.16, 0.09, 1.31, LIVRES[k]))
    # cabinet à rideau à lattes au bout du comptoir (machine à café)
    v.append(B(0.76, 0.20, 1.05, W + 0.03, D + 0.02, 1.62, "noyer"))
    x = 0.78
    while x < W:
        v.append(B(x, 0.185, 1.08, x + 0.022, 0.20, 1.58, "noyer clair"))
        x += 0.026
    v.append(B(0.76, 0.19, 1.60, W + 0.03, 0.20, 1.62, "laiton"))
    return v


def accueil_bibliotheque():
    """Comptoir en L dont la façade client est une bibliothèque ouverte."""
    v = [B(0, 0.04, 0, 1.10, 0.65, 1.01, "noyer"), B(-0.03, -0.02, 1.01, 1.13, 0.67, 1.05, "noyer clair"),
         B(1.10, 0.04, 0, 1.70, 0.45, 0.86, "noyer"), B(1.10, 0.02, 0.86, 1.73, 0.47, 0.90, "noyer clair")]
    for k in range(3):
        x0 = 0.04 + k * 0.355
        v.append(B(x0, 0.0, 0.10, x0 + 0.33, 0.04, 0.95, "creme"))
        for z in (0.12, 0.54):
            v += _livres(x0, x0 + 0.33, -0.20, z, 0.36, k * 3 + int(z * 10), 0.95)
    for z in (0.12, 0.47):
        v += _livres(1.13, 1.68, -0.20, z, 0.30, 5 + int(z * 10), 0.95)
    return v


def table_compas():
    v = []
    tx0, tx1, ty0, ty1 = 0.0, 2.50, 0.0, 0.80
    v.append(B(tx0, ty0, 0.71, tx1, ty1, 0.75, "noyer clair"))
    for xa in (0.25, 2.25):
        v.append(R((xa, 0.08, 0), (xa, 0.40, 0.71), "noyer", 0.045))
        v.append(R((xa, 0.72, 0), (xa, 0.40, 0.71), "noyer", 0.045))
        v.append(B(xa - 0.03, 0.08, 0.66, xa + 0.03, 0.72, 0.71, "noyer"))
    v.append(B(0.25, 0.38, 0.40, 2.25, 0.42, 0.44, "noyer"))
    return v


def table_pirogue():
    """Plateau 2,50 x 0,80 aux extrémités effilées comme une pirogue de la lagune, filet de laiton, divisible en deux."""
    v = []
    z0, z1 = 0.71, 0.75
    v.append(B(0.35, 0.0, z0, 2.15, 0.80, z1, "noyer clair"))
    for a, b, y0, y1 in ((0.20, 0.35, 0.05, 0.75), (0.08, 0.20, 0.13, 0.67), (0.0, 0.08, 0.24, 0.56)):
        v.append(B(a, y0, z0, b, y1, z1, "noyer clair"))
        v.append(B(2.50 - b, y0, z0, 2.50 - a, y1, z1, "noyer clair"))
    v.append(B(0.10, 0.392, z1, 2.40, 0.408, z1 + 0.003, "laiton"))
    v.append(B(1.247, 0.0, z0 - 0.001, 1.253, 0.80, z1 + 0.002, "noyer"))
    for x in (0.42, 1.12, 1.38, 2.08):
        v.append(B(x - 0.025, 0.18, 0, x + 0.025, 0.62, z0, "noyer"))
        v.append(B(x - 0.04, 0.14, 0, x + 0.04, 0.66, 0.03, "laiton"))
    v.append(B(0.45, 0.36, 0.60, 2.05, 0.44, 0.66, "laiton"))
    return v


def table_treteaux():
    """Deux tables de 1,25 x 0,80 sur tréteaux, à assembler en long, en T ou en salle de classe."""
    v = []
    for dx in (0.0, 1.26):
        v.append(B(dx, 0.0, 0.71, dx + 1.24, 0.80, 0.75, "noyer clair"))
        for xa in (dx + 0.15, dx + 1.09):
            v.append(R((xa, 0.10, 0), (xa, 0.40, 0.71), "acier", 0.03))
            v.append(R((xa, 0.70, 0), (xa, 0.40, 0.71), "acier", 0.03))
            v.append(R((xa, 0.20, 0.30), (xa, 0.60, 0.30), "acier", 0.02))
    return v


def poste_poteau(chaises=True):
    """Le poteau de 90 x 90 habillé de lattes de noyer devient un « arbre à travail » : tablette pour deux, lampe et étagère."""
    v = [B(0.0, 0.55, 0, 0.90, 1.45, 2.90, "noyer")]
    x = 0.01
    while x < 0.90:
        v.append(B(x, 0.53, 0.10, x + 0.03, 0.55, 2.80, "noyer clair"))
        x += 0.05
    v.append(B(-0.15, 0.0, 0.72, 1.05, 0.55, 0.76, "noyer clair"))
    v.append(B(-0.15, 0.05, 0.68, -0.12, 0.50, 0.72, "noyer"))
    v.append(B(1.02, 0.05, 0.68, 1.05, 0.50, 0.72, "noyer"))
    v.append(B(0.43, 0.20, 0.76, 0.47, 0.55, 1.18, "feutre"))
    v.append(B(-0.15, 0.40, 1.30, 1.05, 0.55, 1.33, "noyer"))
    for xl in (0.15, 0.75):
        v.append(R((xl, 0.50, 1.33), (xl, 0.32, 1.55), "laiton", 0.015))
        v.append(B(xl - 0.07, 0.25, 1.48, xl + 0.07, 0.39, 1.56, "laiton"))
    v.append(B(0.30, 0.48, 0.80, 0.40, 0.55, 0.86, "creme"))
    if not chaises:
        return v
    for xc in (0.15, 0.75):
        for b in chaise():
            if b[0] == "b":
                v.append(B(b[1] + xc - 0.24, b[2] - 0.62, b[3], b[4] + xc - 0.24, b[5] - 0.62, b[6], b[7]))
            else:
                p, q = b[1], b[2]
                v.append(R((p[0] + xc - 0.24, p[1] - 0.62, p[2]), (q[0] + xc - 0.24, q[1] - 0.62, q[2]), b[3], b[4]))
    return v


def poste_oreilles():
    """Petit bureau mid-century à oreilles en feutre pour s'isoler, étagère et lampe."""
    v = [B(0, 0, 0.71, 0.90, 0.55, 0.75, "noyer clair")]
    for (x, y) in ((0.05, 0.05), (0.81, 0.05), (0.05, 0.46), (0.81, 0.46)):
        v.append(R((x + 0.02, y + 0.02, 0), (x + 0.02, y + 0.02, 0.71), "noyer", 0.035))
    v.append(B(0, 0.05, 0.75, 0.02, 0.55, 1.20, "feutre"))
    v.append(B(0.88, 0.05, 0.75, 0.90, 0.55, 1.20, "feutre"))
    v.append(B(0, 0.53, 0.75, 0.90, 0.55, 1.20, "feutre"))
    v.append(B(0.02, 0.40, 1.00, 0.88, 0.53, 1.02, "noyer"))
    v.append(B(0.70, 0.42, 1.02, 0.80, 0.50, 1.25, "laiton"))
    return v


def poste_abattant():
    """Module du mur de la collection avec un abattant : un poste de travail qui se replie dans la bibliothèque."""
    W, D, H = 0.80, 0.35, 2.20
    v = [B(0, 0.02, 0, 0.025, D, H, "noyer"), B(W - 0.025, 0.02, 0, W, D, H, "noyer"), B(0.025, D - 0.015, 0.08, W - 0.025, D, H, "creme")]
    for z in (0.08, 0.46, 1.10, 1.50, 1.90, H - 0.025):
        v.append(B(0.025, 0.02, z, W - 0.025, D - 0.015, z + 0.025, "noyer clair"))
        if z > 1.0 and z < 2.1:
            v += _livres(0.03, W - 0.03, 0.02, z + 0.025, 0.30, int(z * 10))
    v.append(B(0.03, -0.45, 0.72, W - 0.03, 0.02, 0.75, "noyer clair"))
    v.append(R((0.04, -0.40, 0.75), (0.04, 0.02, 1.08), "laiton", 0.01))
    v.append(R((W - 0.04, -0.40, 0.75), (W - 0.04, 0.02, 1.08), "laiton", 0.01))
    v.append(B(0.03, 0.02, 0.76, W - 0.03, 0.30, 1.08, "feutre"))
    for b in chaise():
        if b[0] == "b":
            v.append(B(b[1] + 0.16, b[2] - 0.75, b[3], b[4] + 0.16, b[5] - 0.75, b[6], b[7]))
        else:
            p, q = b[1], b[2]
            v.append(R((p[0] + 0.16, p[1] - 0.75, p[2]), (q[0] + 0.16, q[1] - 0.75, q[2]), b[3], b[4]))
    return v


def banquette_pirogue():
    v = [B(0.05, 0.08, 0, 2.75, 0.50, 0.20, "noyer"), B(0, 0.0, 0.20, 2.80, 0.50, 0.45, "cognac"), B(0, 0.38, 0.45, 2.80, 0.50, 0.90, "cognac")]
    for k in range(1, 5):
        x = 2.80 * k / 5
        v.append(B(x - 0.006, 0.37, 0.48, x + 0.006, 0.38, 0.87, "noyer"))
    for b in table_pirogue():
        v.append(B(b[1] + 0.15, b[2] - 0.85, b[3], b[4] + 0.15, b[5] - 0.85, b[6], b[7]))
    return v


PIECES = [
    dict(code="M01", fichier="M01_accueil_secretaire", nom="Meuble d'accueil « Secrétaire »", f=accueil_secretaire, ech=0.36,
         cotes=[("W", 1.13), ("D", 0.67), ("H", 1.62)],
         idee="L'enfilade de Madame devient un secrétaire des années 60 : un gradin présente « le livre du jour » aux visiteurs, un cabinet à rideau à lattes cache la machine à café et se ferme le soir.",
         mat=["Caisson en contreplaqué marine plaqué noyer (ou bois local : iroko, bété)", "Façade client en tasseaux cannelés de 28 mm, plateau en noyer massif",
              "Rideau à lattes (tambour) en noyer clair sur toile, guidé en rainure", "Jonc de laiton en repose-pieds, pieds fuselés"],
         fab=["Ébéniste à Abidjan ; rideau à lattes monté sur gabarit", "Cabinet : machine à café, moulin, prise 20 A, aération en partie haute",
              "Hauteur de plan 1,05 côté client, 0,90 côté service (à tester sur gabarit)", "Variantes non retenues : Enfilade, Comptoir-bibliothèque (planche V2)"],
         refs=["R01", "R02"]),
    dict(code="M02", fichier="M02_bibliotheque_kente", nom="Bibliothèque « Kente » du mur de la collection", f=bibli_kente, ech=0.20,
         cotes=[("W", 2.40), ("D", 0.35), ("H", 2.90)],
         idee="Des modules de 0,80 m dont les tablettes se décalent d'un module à l'autre, et des fonds en bandes crème, moutarde, olive et cognac : le mur se lit comme un pagne tissé. Une échelle en laiton sur rail dessert le haut.",
         mat=["Montants et tablettes en noyer (ou bois local) de 25 mm", "Fonds peints en quatre teintes, laque mate lavable",
              "Niches-vitrines fermées pour les livres rares (module M02 d'origine)", "Échelle et rail en laiton brossé, barreaux en noyer"],
         fab=["Trois types de modules (A, B, A) répétés sur environ 9 m", "Fixation au mur contre le basculement ; 30 à 40 kg par tablette",
              "Variantes non retenues : Claustra, Lutrin (planche V1) ; un module lutrin près de l'entrée"],
         refs=["R03", "R04"]),
    dict(code="M03", fichier="M03_banquette_table_pirogue", nom="Banquette et table de réunion « Pirogue »", f=banquette_pirogue, ech=0.20,
         cotes=[("W", 2.80), ("D", 1.35), ("H", 0.90)],
         idee="Pour 9 personnes dans 8,4 m² : une banquette de 5 places contre la baie, et une table de 2,50 × 0,80 m aux extrémités effilées comme une pirogue de la lagune Ébrié. Un filet de laiton cache la jonction : la table se divise en deux pour les ateliers.",
         mat=["Banquette : mousse haute résilience, velours cognac, coutures tous les 0,56 m", "Plateau en noyer massif ou lamellé, extrémités effilées",
              "Filet et goulotte à câbles en laiton, pieds-lames en noyer sur sabots laiton", "Deux demi-tables de 1,25 m, ferrures de jonction invisibles"],
         fab=["Menuisier pour la table, tapissier pour la banquette", "Boîte de sol et goulotte pour les ordinateurs",
              "Variantes non retenues : Compas, Tréteaux (planche V3)"],
         refs=["R05", "R06"]),
    dict(code="M04", fichier="M04_fauteuil_lecture", nom="Fauteuil de lecture « Madame »", f=fauteuil, ech=0.36,
         cotes=[("W", 0.66), ("D", 0.76), ("H", 0.80)],
         idee="Un fauteuil bas pour lire longtemps : les jambes en compas et le cannage des chaises de Chandigarh, le confort enveloppant du coussin brésilien.",
         mat=["Structure en bois dur local (teck de Côte d'Ivoire, iroko)", "Assise cannée ou en rotin tressé",
              "Coussins en velours cognac ou olive, déhoussables", "Accoudoirs en bois massif, finition huilée"],
         fab=["Ébéniste pour la structure, vannier pour le cannage", "Assise à 0,40 m, profondeur utile 0,55 m",
              "Prototype d'un exemplaire avant la série de quatre"],
         refs=["R07", "R08"]),
    dict(code="M05", fichier="M05_chaise", nom="Chaise de table d'hôtes et de réunion", f=chaise, ech=0.40,
         cotes=[("W", 0.48), ("D", 0.50), ("H", 0.78)],
         idee="Une chaise légère, empilable dans l'idée, au dossier en bandeau : la sobriété des chaises danoises, l'assise tressée des artisans d'ici.",
         mat=["Bois dur local massif, assemblages tenon-mortaise", "Assise tressée (corde de papier, raphia ou fibre plastique)",
              "Dossier en bandeau courbe", "Finition huile dure"],
         fab=["Série de 10 à 12 chaises (table d'hôtes, réunion, postes)", "Assise à 0,45 m pour des tables à 0,75 m",
              "Vannerie confiée à un atelier local"],
         refs=["R09", "R10"]),
    dict(code="M06", fichier="M06_fauteuil_terrasse", nom="Fauteuil bas de terrasse", f=fauteuil_exterieur, ech=0.36,
         cotes=[("W", 0.72), ("D", 0.74), ("H", 0.74)],
         idee="Dehors, une assise basse et ajourée qui sèche vite : l'acier peint et la cordelette tressée, savoir-faire courant des ateliers d'Afrique de l'Ouest.",
         mat=["Cadre en tube d'acier Ø 20 mm, thermolaqué noir", "Tressage en cordelette nylon d'extérieur, vert profond",
              "Coussin d'assise en toile d'extérieur crème", "Patins réglables"],
         fab=["Soudeur pour le cadre, tresseur pour l'assise", "Matériaux résistants aux UV et à la pluie",
              "Rangement de nuit : empilable par deux, ou chaîné"],
         refs=["R11", "R12"]),
    dict(code="M07", fichier="M07_chaise_overallt_issa_diabate", avert="Volume d'encombrement seulement : la découpe réelle du modèle n'est pas relevée ; à dessiner d'après un exemplaire ou les plans de l'auteur.", nom="Chaise ÖVERALLT d'Issa Diabaté (IKEA, 2019)", f=overallt, ech=0.36,
         cotes=[("W", 0.70), ("D", 0.65), ("H", 0.63)],
         idee="Retenue pour la terrasse-salon : un fauteuil bas découpé dans un seul panneau de contreplaqué, sans vis ni colle, dessiné par Issa Diabaté pour inviter à converser. Cinq exemplaires autour des tables basses.",
         mat=["Contreplaqué d'une seule plaque (bouleau à l'origine ; ici contreplaqué marine CTBX)", "Pièces emboîtées sans vis, clou ni colle",
              "Vernis ou peinture d'extérieur, coussins en toile crème", "Volume dessiné d'après les mesures d'une revente : à vérifier sur un exemplaire"],
         fab=["Découpe à la commande numérique, ou à la scie sauteuse sur gabarit", "Atelier de menuiserie à Abidjan ; série de 5 à 6 chaises",
              "Œuvre protégée par le droit d'auteur : accord d'Issa Diabaté, de Kevin Gouriou et d'IKEA avant toute fabrication locale", "Rentrées la nuit ou protégées de la pluie"],
         refs=["R13", "R14", "R15", "R16"]),
    dict(code="M08", fichier="M08_poste_arbre_a_travail", nom="Poste de travail « Arbre à travail »", f=poste_poteau, ech=0.30,
         cotes=[("W", 1.20), ("D", 1.45), ("H", 2.90)],
         idee="Le poteau existant de 0,90 × 0,90 m est habillé de lattes de noyer et devient un meuble : une tablette pour deux, un séparateur en feutre, une étagère et deux lampes en laiton. Deux à trois abattants dans le mur de la collection ajoutent des places les jours d'affluence.",
         mat=["Habillage du poteau en lattes de noyer de 30 mm sur tasseaux", "Tablette en noyer de 1,20 × 0,55 m à 0,75 m",
              "Séparateur en feutre de laine, étagère en noyer", "Lampes en laiton orientables, prises et USB intégrées"],
         fab=["Menuisier ; habillage démontable pour l'accès au poteau", "Deux places de 0,60 m, chaises M05",
              "Variantes : Bureau à oreilles (non retenu), Abattant (complément, planche V4)"],
         refs=["R07", "R09"]),
]

REFS = {
    "R01": ("Credenza en noyer à pieds fuselés, Drexel « Declaration » (K. Stewart et S. MacDougall)", "https://www.chairish.com/product/35992971/drexel-declaration-walnut-credenza-by-kipp-stewart-and-stewart-macdougall",
            "Proportions d'enfilade (≈ 1,83 × 0,51 × 0,79 m), noyer, pieds fuselés"),
    "R02": ("Credenza en noyer des années 1960, restaurée (Chairish)", "https://www.chairish.com/product/28904384/1960s-mid-century-modern-walnut-credenza-fully-restored",
            "Pieds fuselés, chaleur du noyer, façade rythmée"),
    "R03": ("Charlotte Perriand, étagère Nuage à plots (Cassina)", "https://www.cassina.com/gb/en/products/nuage-a-plots.html",
            "Rythme de plots et de tablettes, profondeur de 33,5 cm"),
    "R04": ("Charlotte Perriand, étagère Nuage, vers 1958, bois et acier (Phillips)", "https://www.phillips.com/detail/夏洛特·佩里安/222084",
            "Alternance de cases ouvertes et fermées, mur habité"),
    "R05": ("George Nakashima, Conoid Bench, 1960 (Baltimore Museum of Art)", "https://artbma.org/artwork/conoid-bench/",
            "Banc long en noyer, assise d'un seul tenant, dossier léger"),
    "R06": ("Pierre Jeanneret, fauteuil à jambes en compas PJ-SI-29-A (Merit)", "https://merit-la.com/products/pierre-jeanneret-easy-chairs-1",
            "Le piètement en V repris pour la table de réunion"),
    "R07": ("Pierre Jeanneret, Office Cane Chair, bibliothèque de Chandigarh, 1955-1956 (Vitra Design Museum)", "https://collection.design-museum.de/en/collection/item/40354/",
            "Teck et cannage dans une bibliothèque publique : la référence la plus proche du programme"),
    "R08": ("Sergio Rodrigues, fauteuil Mole, 1957 (Metropolitan Museum of Art)", "https://www.metmuseum.org/art/collection/search/772912",
            "Fauteuil bas, coussins généreux : le confort pour lire longtemps"),
    "R09": ("Hans J. Wegner, CH24 Wishbone Chair, 1949 (Skandium)", "https://skandium.com/products/ch24-wishbone-chair-oak",
            "Assise tressée, 55 × 51 × 76 cm, assise à 45 cm"),
    "R10": ("Jean Servais Somian, ébéniste et designer ivoirien (Forbes Afrique)", "https://forbesafrique.com/jean-servais-somian-lartiste-qui-donne-vie-au-cocotier/",
            "Bois local (cocotier) travaillé à Abidjan : une collaboration possible pour une pièce signature"),
    "R11": ("Cheick Diallo, fauteuil tissé à la main, 2019 (InCollect)", "https://www.incollect.com/listings/furniture/seating/cheick-diallo-hand-woven-armchair-2019-707566",
            "Cadre métallique et fil tressé à la main : design contemporain d'Afrique de l'Ouest"),
    "R13": ("IKEA et Design Indaba, collection ÖVERALLT, 2019 (Dezeen)", "https://www.dezeen.com/2019/02/28/ikea-design-indaba-african-designers-overallt-furniture-homeware/",
            "La chaise d'Issa Diabaté : une plaque de contreplaqué, sans fixation, basse pour la conversation"),
    "R14": ("Fauteuil ÖVERALLT, I. Diabaté et K. Gouriou pour IKEA, 2019 (Chairish)", "https://www.chairish.com/product/26745064/overallt-armchair-by-i-diabate-and-k-gouriou-for-ikea-2019",
            "Mesures d'une revente : assise à 30 cm, hauteur 63 cm, 70 × 65 cm au sol"),
    "R15": ("IKEA lance sa collection made in Africa, Design Indaba 2019 (Domus)", "https://domusweb.it/en/speciali/design-indaba/2019/ikea-launches-its-new-collection-made-in-africa-at-design-indaba-2019.html",
            "Contreplaqué de bouleau, co-conception avec Kevin Gouriou"),
    "R16": ("Exposition « Local Art Brut », Macline Hien et Issa Diabaté (galerie Louis Simone Guirandou, Abidjan)", "https://www.louisimoneguirandou.gallery/en/exhibitions/12-local-art-brut-macline-hien-issa-diabate/overview/",
            "Meubles inspirés des tabourets en bois, trônes et chaises de gardien : piste pour les tabourets"),
    "R12": ("Pieter Peulen chez lui, avec le fauteuil F300 de Pierre Paulin (Gubi)", "https://gubi.com/en/us/inspiration/editorials/at-home-with-pieter-peulen",
            "Référence de l'équipe : pièces vintage choisies comme des œuvres dans un intérieur sobre"),
}


# ------------------------------------------------------------------ dessin
def esc(s):
    # typographie française : apostrophe courbe
    return s.replace("&", "&amp;").replace("<", "&lt;").replace("'", "’")


def vues(piece):
    vol = piece["f"]()
    el = []
    # bornes
    pts = []
    for v in vol:
        if v[0] == "b":
            pts += [(v[1], v[2], v[3]), (v[4], v[5], v[6])]
        else:
            pts += [v[1], v[2]]
    xs, ys, zs = [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts]
    X0, X1, Y0, Y1, Z0, Z1 = min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)
    E = 520 / max(X1 - X0, Y1 - Y0 + 0.001, Z1 - Z0) * 0.62

    def proj(nom, ox, oy, axes):
        # axes : ("x","y") dessus, ("x","z") face, ("y","z") côté
        a, b = axes
        lo = {"x": X0, "y": Y0, "z": Z0}
        hi = {"x": X1, "y": Y1, "z": Z1}
        def P(p):
            d = {"x": p[0], "y": p[1], "z": p[2]}
            u = ox + (d[a] - lo[a]) * E
            w = oy - (d[b] - lo[b]) * E if b == "z" else oy + (d[b] - lo[b]) * E
            return u, w
        prof = {"x": "y", "y": "x", "z": "z"}
        cachee = {("x", "y"): "z", ("x", "z"): "y", ("y", "z"): "x"}[axes]
        ordre = sorted(vol, key=lambda v: (v[3 + "xyz".index(cachee)] if v[0] == "b" else min(v[1]["xyz".index(cachee)], v[2]["xyz".index(cachee)])) * (-1 if cachee == "z" else 1))
        for v in ordre:
            if v[0] == "b":
                u0, w0 = P((v[1], v[2], v[3]))
                u1, w1 = P((v[4], v[5], v[6]))
                op = 0.45 if v[7] == "verre" else 0.9
                el.append(f'<rect x="{min(u0, u1):.1f}" y="{min(w0, w1):.1f}" width="{abs(u1 - u0):.1f}" height="{abs(w1 - w0):.1f}" '
                          f'fill="{C[v[7]]}" fill-opacity="{op}" stroke="{INK}" stroke-width="0.8"/>')
            else:
                u0, w0 = P(v[1]); u1, w1 = P(v[2])
                el.append(f'<line x1="{u0:.1f}" y1="{w0:.1f}" x2="{u1:.1f}" y2="{w1:.1f}" stroke="{C[v[3]]}" stroke-width="{max(v[4] * E, 1.2):.1f}" stroke-linecap="round"/>')
        u0, w0 = P((X0, Y0, Z0)); u1, w1 = P((X1, Y1, Z1))
        ua, ub = min(u0, u1), max(u0, u1)
        wa, wb = min(w0, w1), max(w0, w1)
        L = {"x": X1 - X0, "y": Y1 - Y0, "z": Z1 - Z0}
        el.append(f'<text x="{ox}" y="{wa - 34}" font-family="{FONT}" font-size="12" font-weight="700" fill="{GRIS}" letter-spacing="1">{nom}</text>')
        # cote horizontale
        yy = wb + 22
        el.append(f'<line x1="{ua}" y1="{yy}" x2="{ub}" y2="{yy}" stroke="{INK}" stroke-width="0.8"/>')
        for u in (ua, ub):
            el.append(f'<line x1="{u - 4}" y1="{yy + 4}" x2="{u + 4}" y2="{yy - 4}" stroke="{INK}"/><line x1="{u}" y1="{wb + 4}" x2="{u}" y2="{yy + 6}" stroke="{GRIS}" stroke-width="0.5"/>')
        el.append(f'<text x="{(ua + ub) / 2}" y="{yy + 16}" font-family="{FONT}" font-size="12" text-anchor="middle" fill="{INK}">' + f"{L[a]:.2f}".replace(".", ",") + "</text>")
        # cote verticale
        xx = ub + 22
        el.append(f'<line x1="{xx}" y1="{wa}" x2="{xx}" y2="{wb}" stroke="{INK}" stroke-width="0.8"/>')
        for w in (wa, wb):
            el.append(f'<line x1="{xx - 4}" y1="{w + 4}" x2="{xx + 4}" y2="{w - 4}" stroke="{INK}"/>')
        el.append(f'<text x="{xx + 8}" y="{(wa + wb) / 2 + 4}" font-family="{FONT}" font-size="12" fill="{INK}">' + f"{L[b]:.2f}".replace(".", ",") + "</text>")
        return ub - ua, wb - wa

    # positions
    wx, hy = (X1 - X0) * E, (Y1 - Y0) * E
    hz = (Z1 - Z0) * E
    proj("FACE", 70, 160 + hz, ("x", "z"))
    proj("CÔTÉ", 70 + wx + 110, 160 + hz, ("y", "z"))
    proj("DESSUS", 70, 160 + hz + 110, ("x", "y"))
    bas = 160 + hz + 110 + hy
    # axonométrie
    a30 = math.cos(math.radians(30))
    ex = 280 / max(X1 - X0 + Y1 - Y0, (Z1 - Z0) * 1.6 + 0.3)
    def I(p):
        return (1150 + (p[0] - p[1]) * a30 * ex, 150 + (Z1 + 0.05 + (X1 + Y1) * 0.5) * ex + (-(p[0] + p[1]) * 0.5 - p[2]) * ex)
    def cle(v):
        if v[0] == "b":
            return (v[1] + v[4]) / 2 + (v[2] + v[5]) / 2 - (v[3] + v[6]) / 2 * 0.2
        return (v[1][0] + v[2][0]) / 2 + (v[1][1] + v[2][1]) / 2
    for v in sorted(vol, key=cle, reverse=True):
        if v[0] == "b":
            x0, y0, z0, x1, y1, z1, m = v[1:]
            faces = [([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], 1.0),
                     ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], 0.85),
                     ([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], 0.68)]
            for pts, k in faces:
                d = " ".join(f"{I(p)[0]:.1f},{I(p)[1]:.1f}" for p in pts)
                col = C[m]
                op = 0.4 if m == "verre" else 1
                el.append(f'<polygon points="{d}" fill="{col}" fill-opacity="{op}" stroke="{INK}" stroke-width="0.6" style="filter:brightness({k})"/>')
        else:
            a, b = I(v[1]), I(v[2])
            el.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{C[v[3]]}" stroke-width="{max(v[4] * ex, 1.5):.1f}" stroke-linecap="round"/>')
    return el, bas


def fiche(piece):
    el, bas = vues(piece)
    w, h = 1600, max(1000, int(bas + 120))
    t = []
    def tx(x, y, s, taille=13, col=INK, poids=400, ancre="start"):
        t.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{taille}" font-weight="{poids}" fill="{col}" text-anchor="{ancre}">{esc(s)}</text>')
    def para(x, y, s, larg=58, taille=13, col=INK, inter=18):
        mots, ligne, lignes = s.split(), "", []
        for m in mots:
            if len(ligne) + len(m) + 1 > larg:
                lignes.append(ligne); ligne = m
            else:
                ligne = (ligne + " " + m).strip()
        lignes.append(ligne)
        for i, l in enumerate(lignes):
            tx(x, y + i * inter, l, taille, col)
        return y + len(lignes) * inter
    tx(70, 52, f'{piece["code"]} · {piece["nom"]}', 26, poids=700)
    tx(70, 78, "Désiré Akai (rôle IA) · fiche mobilier · V8 indice B · modèle d'étude à prototyper, cotes en mètres", 13, GRIS)
    if piece.get("avert"):
        tx(70, 100, piece["avert"], 13, ORANGE, 700)
    X = 920
    y = 620
    y = para(X, y, piece["idee"], 66, 15, INK, 21) + 14
    tx(X, y, "MATIÈRES", 11, GRIS, 700); y += 20
    for m in piece["mat"]:
        y = para(X + 12, y, "· " + m, 72, 13) + 2
    y += 10
    tx(X, y, "FABRICATION LOCALE", 11, GRIS, 700); y += 20
    for m in piece["fab"]:
        y = para(X + 12, y, "· " + m, 72, 13) + 2
    y += 10
    tx(X, y, "RÉFÉRENCES ÉTUDIÉES", 11, GRIS, 700); y += 20
    for r in piece["refs"]:
        titre, url, apport = REFS[r]
        y = para(X + 12, y, f"{r} · {titre}", 72, 12, INK, 16)
        y = para(X + 24, y, "→ " + apport, 74, 12, ORANGE, 16) + 4
    h = max(h, y + 40)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
           f'<rect width="{w}" height="{h}" fill="#fbf8f2"/>' + "".join(el) + "".join(t) + "</svg>")
    nom = piece["fichier"] + ".svg"
    os.makedirs(SORTIE, exist_ok=True)
    open(os.path.join(SORTIE, nom), "w", encoding="utf-8").write(svg)
    print(nom)


def index_csv():
    lignes = ["id;titre;url;source;date_consultation;apport_retenu;pieces"]
    for k, (titre, url, apport) in REFS.items():
        pieces = ",".join(p["code"] for p in PIECES if k in p["refs"])
        src = url.split("/")[2]
        lignes.append(f"{k};{titre};{url};{src};2026-10-16;{apport};{pieces}")
    open(os.path.join(SORTIE, "REFERENCES.csv"), "w", encoding="utf-8").write("\n".join(lignes) + "\n")


if __name__ == "__main__":
    for p in PIECES:
        fiche(p)
    index_csv()
