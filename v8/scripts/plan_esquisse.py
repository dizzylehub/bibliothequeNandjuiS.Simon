"""Plan d'aménagement, esquisse V8 indice B (Désiré Akai, contrôle Manadja).

Repère : X de gauche à droite vu depuis la terrasse (0 = nu intérieur du mur gauche),
Y depuis la façade (0 = nu intérieur de façade) vers le fond, au nord.

Cotes mesurées par le client (croquis du 14/10 et précisions du 15/10) :
  bande gauche 3,00 m ; grande salle 3,60 m ; porte -> poteau 3,30 m ;
  poteau 0,90 x 0,90 m ; fond -> bloc WC 2,40 m ; parvis 2,75 m ; 5,50 m sur la terrasse.
Estimées (photos et proportions du croquis) : profondeur totale 7,60 m ; mur de séparation 0,15 m.
Proposées : tout le reste.

Usage : python3 v8/scripts/plan_esquisse.py  ->  v8/plans/E01_plan_amenagement.svg
"""
import os

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "..", "plans")

# ---------------------------------------------------------------- géométrie
L_G, EP_SEP, L_D = 3.00, 0.15, 3.60
X_SEP0, X_SEP1 = L_G, L_G + EP_SEP
X_FIN = X_SEP1 + L_D          # 6,75
PROF = 7.60                    # estimée
Y_WC = PROF - 2.40             # 5,20
EP_EXT = 0.20
POT = (X_FIN - 0.90, 3.30, X_FIN, 4.20)
Y_REU0, Y_REU1 = 2.30, Y_WC - 0.10
PARVIS = 2.75
Y_TER = -5.40                  # limite proposée de la terrasse prolongée
X_TER0, X_TER1 = -1.20, 8.00

S = 76
OX, OY = 110, 70
YMAX = PROF + 0.5


def px(x):
    return OX + (x - X_TER0 + 0.3) * S


def py(y):
    return OY + (YMAX - y) * S


INK, GRIS, FIN = "#2a2622", "#8b8a86", "#c9c3b8"
NOYER, VELOURS, OLIVE, MOUT = "#8a5a35", "#a85f2c", "#56613a", "#c9962e"
VERRE, DALLE, VEG = "#7fb3c4", "#ece5d6", "#5f8a55"
FONT = "Archivo, Helvetica, Arial, sans-serif"

el = []


def rect(x0, y0, x1, y1, fill="none", stroke=INK, sw=1.0, dash=None, op=1, rx=0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    el.append(f'<rect x="{px(min(x0, x1)):.1f}" y="{py(max(y0, y1)):.1f}" width="{abs(x1 - x0) * S:.1f}" '
              f'height="{abs(y1 - y0) * S:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}" rx="{rx}"{d}/>')


def ligne(x0, y0, x1, y1, stroke=INK, sw=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    el.append(f'<line x1="{px(x0):.1f}" y1="{py(y0):.1f}" x2="{px(x1):.1f}" y2="{py(y1):.1f}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def cercle(x, y, r, fill="none", stroke=INK, sw=1.0):
    el.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="{r * S:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def texte(x, y, t, taille=12, col=INK, ancre="middle", poids=400, rot=0, brut=False):
    X, Y = (x, y) if brut else (px(x), py(y))
    tr = f' transform="rotate({rot} {X:.1f} {Y:.1f})"' if rot else ""
    el.append(f'<text x="{X:.1f}" y="{Y:.1f}" font-family="{FONT}" font-size="{taille}" font-weight="{poids}" '
              f'fill="{col}" text-anchor="{ancre}"{tr}>{t}</text>')


def arc_porte(xg, y, larg, sens=1, vers=1, axe="x"):
    """Porte battante : charnière en (xg, y), vantail de largeur larg."""
    if axe == "x":
        x1 = xg + sens * larg
        ligne(xg, y, xg, y + vers * larg, sw=1.2)
        el.append(f'<path d="M{px(x1):.1f} {py(y):.1f} A{larg * S:.1f} {larg * S:.1f} 0 0 {1 if sens * vers > 0 else 0} '
                  f'{px(xg):.1f} {py(y + vers * larg):.1f}" fill="none" stroke="{GRIS}" stroke-width="0.8"/>')
    else:
        y1 = y + sens * larg
        ligne(xg, y, xg + vers * larg, y, sw=1.2)
        el.append(f'<path d="M{px(xg):.1f} {py(y1):.1f} A{larg * S:.1f} {larg * S:.1f} 0 0 {0 if sens * vers > 0 else 1} '
                  f'{px(xg + vers * larg):.1f} {py(y):.1f}" fill="none" stroke="{GRIS}" stroke-width="0.8"/>')


def cote_h(x0, x1, y, t, dec=0.0, statut=""):
    ligne(x0, y, x1, y, stroke=INK, sw=0.7)
    for x in (x0, x1):
        el.append(f'<line x1="{px(x) - 4:.1f}" y1="{py(y) + 4:.1f}" x2="{px(x) + 4:.1f}" y2="{py(y) - 4:.1f}" stroke="{INK}" stroke-width="1"/>')
    col = "#b0582b" if statut else INK
    texte((x0 + x1) / 2, y + 0.08 + dec, t + statut, 11, col)


def cote_v(x, y0, y1, t, statut=""):
    ligne(x, y0, x, y1, stroke=INK, sw=0.7)
    for y in (y0, y1):
        el.append(f'<line x1="{px(x) - 4:.1f}" y1="{py(y) + 4:.1f}" x2="{px(x) + 4:.1f}" y2="{py(y) - 4:.1f}" stroke="{INK}" stroke-width="1"/>')
    col = "#b0582b" if statut else INK
    X, Y = px(x) - 6, py((y0 + y1) / 2)
    texte(X, Y, t + statut, 11, col, rot=-90, brut=True)


def chaise(x, y, ori):
    """Chaise 0,45 x 0,45 ; ori = côté du dossier (n, s, e, o)."""
    rect(x - 0.22, y - 0.22, x + 0.22, y + 0.22, fill="#ffffff", sw=0.8, rx=3)
    d = {"n": (x - 0.22, y + 0.17, x + 0.22, y + 0.22), "s": (x - 0.22, y - 0.22, x + 0.22, y - 0.17),
         "e": (x + 0.17, y - 0.22, x + 0.22, y + 0.22), "o": (x - 0.22, y - 0.22, x - 0.17, y + 0.22)}[ori]
    rect(*d, fill=INK, sw=0)


def fauteuil(x, y, ori, col):
    rect(x - 0.38, y - 0.38, x + 0.38, y + 0.38, fill=col, sw=0.9, op=0.85, rx=10)
    d = {"n": (x - 0.38, y + 0.22, x + 0.38, y + 0.38), "s": (x - 0.38, y - 0.38, x + 0.38, y - 0.22),
         "e": (x + 0.22, y - 0.38, x + 0.38, y + 0.38), "o": (x - 0.38, y - 0.38, x - 0.22, y + 0.38)}[ori]
    rect(*d, fill=INK, sw=0, op=0.55)


def plante(x, y, r=0.32):
    cercle(x, y, r, fill=VEG, stroke=VEG, sw=0.6)
    el.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="{r * S * 0.55:.1f}" fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.7"/>')


def construire():
    el.clear()
    # ---------------- terrasse prolongée (proposée)
    rect(X_TER0, Y_TER, X_TER1, 0, fill=DALLE, stroke="none")
    for i in range(int((X_TER1 - X_TER0) / 0.6) + 1):
        x = X_TER0 + i * 0.6
        ligne(x, Y_TER, x, -EP_EXT, stroke="#ffffff", sw=0.8)
    for j in range(int(-Y_TER / 0.6) + 1):
        y = Y_TER + j * 0.6
        ligne(X_TER0, y, X_TER1, y, stroke="#ffffff", sw=0.8)
    # limite actuelle du muret (déposé) et nouvelle limite en claustra
    ligne(-EP_EXT, -PARVIS, X_FIN + EP_EXT, -PARVIS, stroke=GRIS, sw=1.2, dash="5 4")
    texte(3.5, -PARVIS - 0.22, "muret actuel déposé", 9, GRIS, "start")
    rect(X_TER0, Y_TER - 0.12, 3.40, Y_TER, fill="#d9c9a8", sw=0.8)
    rect(5.40, Y_TER - 0.12, X_TER1, Y_TER, fill="#d9c9a8", sw=0.8)
    for x0, x1 in ((X_TER0, 3.40), (5.40, X_TER1)):
        x = x0 + 0.15
        while x < x1:
            ligne(x, Y_TER - 0.12, x, Y_TER, stroke=INK, sw=0.5)
            x += 0.15
    rect(X_TER0, Y_TER, X_TER0 + 0.12, -0.3, fill="#d9c9a8", sw=0.8)
    rect(X_TER1 - 0.12, Y_TER, X_TER1, -0.3, fill="#d9c9a8", sw=0.8)
    arc_porte(3.40, Y_TER - 0.06, 1.0, sens=1, vers=1)
    texte(4.4, Y_TER - 0.45, "portillon", 10, GRIS)
    texte((X_TER0 + X_TER1) / 2, Y_TER - 0.75, "nouvelle limite : claustra bas et jardinières · emprise à autoriser", 11, "#b0582b")
    # pergola (projection)
    rect(-0.9, -4.9, 7.7, -0.05, stroke=INK, sw=1.0, dash="7 4")
    for x in (-0.9, 1.25, 3.40, 5.55, 7.7):
        rect(x - 0.08, -4.98, x + 0.08, -4.82, fill=INK, sw=0)
    i = 0
    y = -0.3
    while y > -4.9:
        ligne(-0.9, y, 7.7, y, stroke=GRIS, sw=0.4, dash="2 3")
        y -= 0.3
    texte(7.6, -5.18, "pergola en projection : lames bois, poteaux acier", 10, GRIS, "end")
    # salon extérieur gauche
    rect(-0.75, -4.6, -0.2, -1.0, fill=NOYER, sw=0.8, op=0.8, rx=4)
    rect(-0.75, -4.6, 2.6, -4.05, fill=NOYER, sw=0.8, op=0.8, rx=4)
    rect(0.4, -3.4, 1.6, -2.6, fill="#ffffff", sw=0.9, rx=30)
    fauteuil(2.2, -2.3, "e", VELOURS)
    fauteuil(1.0, -1.7, "s", OLIVE)
    cercle(2.2, -3.3, 0.24, fill=MOUT, sw=0.8)
    texte(1.0, -3.95, "banquette en L, coussins", 10, INK)
    # salon extérieur droit
    rect(7.05, -4.6, 7.6, -1.2, fill=NOYER, sw=0.8, op=0.8, rx=4)
    rect(5.9, -3.2, 6.6, -2.5, fill="#ffffff", sw=0.9, rx=30)
    fauteuil(6.25, -1.9, "s", VELOURS)
    fauteuil(5.75, -3.9, "o", OLIVE)
    cercle(6.4, -4.2, 0.22, fill=MOUT, sw=0.8)
    for (x, y) in ((-0.55, -0.45), (7.4, -0.45), (2.9, -4.55)):
        plante(x, y, 0.28)
    # allée d'entrée
    texte(4.4, -3.7, "allée", 11, GRIS)
    el.append(f'<path d="M{px(4.4):.1f} {py(-4.9):.1f} L{px(4.4):.1f} {py(-0.4):.1f}" stroke="{GRIS}" stroke-width="1" '
              f'marker-end="url(#fl)" stroke-dasharray="4 3"/>')
    texte(1.55, -0.85, "TERRASSE COUVERTE · SALONS DU SOIR", 12, INK, poids=700)

    # ---------------- intérieur : sols
    rect(0, 0, X_FIN, PROF, fill="#fbf8f2", stroke="none")
    rect(0, 0, L_G, Y_REU0 - 0.05, fill="#f3ead9", stroke="none")
    rect(0, Y_REU0, L_G, Y_REU1, fill="#efe2cc", stroke="none")
    # tapis du salon
    rect(3.7, 4.55, 6.05, 6.75, fill=MOUT, stroke="none", op=0.35)
    # murs existants conservés
    for r in ((-EP_EXT, -EP_EXT, 0, PROF + EP_EXT), (X_FIN, -EP_EXT, X_FIN + EP_EXT, PROF + EP_EXT),
              (-EP_EXT, PROF, X_FIN + EP_EXT, PROF + EP_EXT)):
        rect(*r, fill=INK, stroke="none")
    for x0, x1 in ((-EP_EXT, 0.6), (2.4, 3.60), (5.20, 5.60), (6.40, X_FIN + EP_EXT)):
        rect(x0, -EP_EXT, x1, 0, fill=INK, stroke="none")
    rect(X_SEP0, Y_WC, X_SEP1, PROF, fill=INK, stroke="none")
    # poteau
    rect(*POT[:2], *POT[2:], fill=INK, stroke="none")
    texte(6.3, 3.70, "poteau", 9, "#ffffff")
    # mur démoli
    rect(X_SEP0, 0, X_SEP1, Y_REU1, stroke="#b0582b", sw=0.9, dash="4 3")
    texte(X_SEP0 + 0.07, 1.05, "mur démoli · avis structure", 9, "#b0582b", rot=-90)
    # baies de façade
    for x0, x1 in ((0.6, 2.4), (5.6, 6.4)):
        rect(x0, -EP_EXT, x1, 0, fill="#ffffff", sw=0.8)
        ligne(x0, -0.1, x1, -0.1, stroke=VERRE, sw=2)
    texte(1.5, -0.42, "vitrine (ancienne porte)", 9, GRIS)
    # grande porte d'entrée, deux vantaux
    rect(3.60, -EP_EXT, 5.20, 0, fill="#ffffff", stroke="none")
    arc_porte(3.60, 0.0, 0.80, sens=1, vers=1)
    arc_porte(5.20, 0.0, 0.80, sens=-1, vers=1)
    texte(4.4, -0.42, "grande porte d'entrée 1,60 m", 9, GRIS)
    # ---------------- salle de réunion vitrée
    ligne(0, Y_REU0, X_SEP1, Y_REU0, stroke=VERRE, sw=3)
    ligne(X_SEP0 + 0.07, Y_REU0, X_SEP0 + 0.07, 4.05, stroke=VERRE, sw=3)
    for y in (Y_REU0, 3.2, 4.05):
        rect(X_SEP0 + 0.02, y - 0.03, X_SEP0 + 0.12, y + 0.03, fill=INK, sw=0)
    arc_porte(X_SEP0 + 0.07, 4.05, 0.95, sens=1, vers=1, axe="y")
    for x in (0.75, 1.5, 2.25):
        rect(x - 0.03, Y_REU0 - 0.03, x + 0.03, Y_REU0 + 0.03, fill=INK, sw=0)
    rect(0.95, 2.80, 2.05, 4.60, fill=NOYER, sw=1, op=0.85, rx=6)
    for y in (3.15, 3.70, 4.25):
        chaise(0.62, y, "o")
        chaise(2.38, y, "e")
    ligne(1.35, Y_REU1 - 0.04, 2.75, Y_REU1 - 0.04, stroke=INK, sw=3)
    texte(2.05, Y_REU1 - 0.25, "écran", 9, GRIS)
    texte(1.5, 2.55, "SALLE DE RÉUNION", 12, INK, poids=700)
    texte(1.5, 2.40, "location · 6 places · rideaux en lin", 9, GRIS)
    # ---------------- bloc WC (deux cabines côte à côte)
    rect(0, Y_REU1, X_SEP0, Y_WC, fill=INK, stroke="none")
    rect(1.45, Y_WC, 1.55, PROF, fill=INK, stroke="none")
    rect(0, Y_WC, 1.45, PROF, fill="#eef0ee", stroke="none")
    rect(1.55, Y_WC, X_SEP0, PROF, fill="#eef0ee", stroke="none")
    rect(0.30, Y_REU1, 1.10, Y_WC, fill="#ffffff", stroke="none")
    arc_porte(0.30, Y_WC, 0.80, sens=1, vers=1)
    rect(X_SEP0, 5.45, X_SEP1, 6.35, fill="#ffffff", stroke="none")
    arc_porte(X_SEP1, 5.45, 0.90, sens=1, vers=-1, axe="y")
    for x in (0.72, 2.27):
        el.append(f'<ellipse cx="{px(x):.1f}" cy="{py(PROF - 0.42):.1f}" rx="{0.19 * S:.1f}" ry="{0.30 * S:.1f}" fill="#ffffff" stroke="{INK}" stroke-width="0.9"/>')
        rect(x - 0.22, PROF - 0.15, x + 0.22, PROF, fill="#ffffff", sw=0.9)
    rect(0.05, 6.0, 0.35, 6.45, fill="#ffffff", sw=0.8)
    rect(2.65, 6.6, 2.95, 7.05, fill="#ffffff", sw=0.8)
    texte(0.72, 6.3, "WC", 11, INK, poids=700, )
    texte(0.72, 6.15, "réunion", 9, GRIS)
    texte(2.27, 6.3, "WC", 11, INK, poids=700)
    texte(2.27, 6.15, "public adapté", 9, GRIS)
    texte(1.5, PROF + 0.32, "réserve haute existante au-dessus des WC (à vérifier)", 9, GRIS)
    # ---------------- accueil-café ouvert
    rect(0, 0.25, 0.62, 2.0, fill=NOYER, sw=0.9, op=0.75)
    texte(0.31, 1.12, "arrière-bar", 8, "#ffffff", rot=-90)
    rect(1.55, 0.45, 2.20, 2.0, fill=NOYER, sw=1, op=0.95, rx=4)
    texte(1.875, 1.22, "comptoir", 9, "#ffffff", rot=-90)
    cercle(1.15, 1.25, 0.2, fill="#ffffff", sw=0.9)
    texte(1.5, 0.12, "ACCUEIL-CAFÉ OUVERT", 11, INK, poids=700)
    for y in (0.75, 1.55):
        cercle(2.55, y, 0.2, fill=VELOURS, sw=0.8)
    # ---------------- bibliothèque
    # mur de la collection
    for r in ((X_FIN - 0.35, 0.25, X_FIN, POT[1]), (X_FIN - 0.35, POT[3], X_FIN, PROF - 0.35),
              (X_SEP1, PROF - 0.35, X_FIN, PROF), (X_SEP1, 6.45, X_SEP1 + 0.35, PROF - 0.35)):
        rect(*r, fill=NOYER, sw=0.8, op=0.9)
    for y in (0.25 + 0.75 * k for k in range(1, 5)):
        ligne(X_FIN - 0.35, y, X_FIN, y, stroke="#ffffff", sw=0.8)
    for y in (POT[3] + 0.8 * k for k in range(1, 4)):
        ligne(X_FIN - 0.35, y, X_FIN, y, stroke="#ffffff", sw=0.8)
    for x in (X_SEP1 + 0.8 * k for k in range(1, 5)):
        ligne(x, PROF - 0.35, x, PROF, stroke="#ffffff", sw=0.8)
    texte(X_FIN - 0.6, 2.0, "MUR DE LA COLLECTION", 10, NOYER, poids=700, rot=-90)
    # banquette de fenêtre
    rect(5.6, 0.0, 6.4, 0.5, fill=VELOURS, sw=0.8, op=0.8)
    texte(6.0, 0.62, "banquette de fenêtre", 9, GRIS)
    # table d'hôtes
    rect(4.05, 1.80, 5.65, 2.70, fill=NOYER, sw=1, op=0.85, rx=6)
    for x in (4.45, 5.25):
        chaise(x, 1.48, "s")
        chaise(x, 3.02, "n")
    texte(4.85, 2.18, "table d'hôtes", 10, "#ffffff")
    texte(4.85, 2.04, "6 places", 9, "#ffffff")
    # postes individuels le long de la baie de la salle de réunion ? non : tablettes au poteau
    rect(POT[0] - 0.55, POT[1], POT[0], POT[3], fill=NOYER, sw=0.8, op=0.7)
    chaise(POT[0] - 0.85, 3.52, "o")
    chaise(POT[0] - 0.85, 4.0, "o")
    texte(POT[0] - 0.3, 4.38, "2 postes", 9, GRIS)
    # salon de lecture
    for (x, y, o, c) in ((4.20, 5.05, "s", VELOURS), (5.55, 5.05, "s", OLIVE), (4.20, 6.30, "n", OLIVE), (5.55, 6.30, "n", VELOURS)):
        fauteuil(x, y, o, c)
    rect(4.55, 5.40, 5.20, 5.95, fill="#ffffff", sw=0.9, rx=20)
    cercle(3.75, 5.65, 0.16, fill=MOUT, sw=0.8)
    cercle(6.05, 5.65, 0.16, fill=MOUT, sw=0.8)
    texte(4.88, 6.95, "SALON DE LECTURE", 12, INK, poids=700)
    texte(4.85, 1.02, "BIBLIOTHÈQUE", 12, INK, poids=700)
    el.append(f'<path d="M{px(4.4):.1f} {py(0.15):.1f} L{px(3.55):.1f} {py(1.2):.1f} L{px(3.55):.1f} {py(3.9):.1f}" '
              f'stroke="{GRIS}" stroke-width="1" fill="none" stroke-dasharray="4 3" marker-end="url(#fl)"/>')

    # ---------------- cotes
    cote_h(0, L_G, PROF + 0.75, "3,00")
    cote_h(X_SEP1, X_FIN, PROF + 0.75, "3,60")
    cote_h(0, X_FIN, PROF + 1.05, "6,75 intérieur", statut=" · 3,00 + 0,15 estimé + 3,60")
    cote_v(X_FIN + 0.55, 0, POT[1], "3,30")
    cote_v(X_FIN + 0.55, POT[1], POT[3], "0,90")
    cote_v(X_FIN + 0.55, POT[3], PROF, "3,40", statut=" estimé")
    cote_v(X_FIN + 1.0, 0, PROF, "7,60", statut=" estimé (photos)")
    cote_v(-0.65, Y_WC, PROF, "2,40")
    cote_v(-0.65, Y_REU0, Y_WC, "2,90")
    cote_v(-0.65, 0, Y_REU0, "2,30")
    cote_v(X_TER1 + 0.25, -PARVIS, 0, "2,75")
    cote_v(X_TER1 + 0.25, Y_TER, -PARVIS, "2,65", statut=" proposé")

    # ---------------- surfaces
    surf = {
        "Accueil-café ouvert": L_G * Y_REU0,
        "Salle de réunion": L_G * (Y_REU1 - Y_REU0),
        "WC réunion": 1.45 * 2.40,
        "WC public adapté": 1.45 * 2.40,
        "Bibliothèque et salon": L_D * PROF - 0.81 + EP_SEP * Y_REU1,
    }
    return surf


def cartouche(surf):
    x0 = 1010
    out = []
    t = lambda x, y, s, taille=13, col=INK, poids=400, ancre="start": out.append(
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{taille}" font-weight="{poids}" fill="{col}" text-anchor="{ancre}">{s}</text>')
    t(x0, 90, "CAFÉ-BIBLIOTHÈQUE NANDJUI", 20, poids=700)
    t(x0, 116, "E01 · Plan d'aménagement · esquisse", 15)
    t(x0, 138, "V8 indice B · 15 octobre 2026 · non coté pour exécution", 11, GRIS)
    t(x0, 175, "Direction retenue : A, le salon de Madame", 12, poids=700)
    t(x0, 193, "cocon mid-century et terrasse-salon sous pergola", 12)
    y = 235
    t(x0, y, "SURFACES INTÉRIEURES (ESTIMÉES)", 11, GRIS, 700)
    y += 22
    total = 0
    for k, v in surf.items():
        t(x0, y, k, 12)
        t(x0 + 330, y, f"{v:.1f} m²".replace(".", ","), 12, ancre="end")
        total += v
        y += 20
    out.append(f'<line x1="{x0}" y1="{y - 12}" x2="{x0 + 330}" y2="{y - 12}" stroke="{INK}"/>')
    t(x0, y + 4, "Total intérieur", 12, poids=700)
    t(x0 + 330, y + 4, f"{total:.1f} m²".replace(".", ","), 12, poids=700, ancre="end")
    y += 26
    t(x0, y, f"Terrasse couverte proposée : {(X_TER1 - X_TER0) * -Y_TER:.0f} m² environ".replace(".", ","), 12)
    y += 40
    t(x0, y, "STATUT DES COTES", 11, GRIS, 700)
    y += 22
    for s in ("Noir : mesuré par vous (croquis et précisions)",
              "Orange : estimé ou proposé, à mesurer",
              "Profondeur 7,60 m : estimée d'après les photos",
              "et les proportions du croquis (fourchette 7,2 à 8,0 m)",
              "Votre 5,50 m sur la terrasse : lu comme la longueur",
              "du muret, l'intérieur restant à 6,75 m (à vérifier)"):
        t(x0, y, s, 11, "#b0582b" if s.startswith(("Orange", "Profondeur", "et les", "Votre", "du muret")) else INK)
        y += 17
    y += 22
    t(x0, y, "LÉGENDE", 11, GRIS, 700)
    y += 18
    items = [(INK, "mur existant conservé"), ("#b0582b", "mur démoli (pointillé)"), (VERRE, "baie vitrée"),
             (NOYER, "menuiserie bois (noyer)"), (VELOURS, "assises velours"), (DALLE, "terrasse dallée")]
    for c, s in items:
        out.append(f'<rect x="{x0}" y="{y - 10}" width="22" height="12" fill="{c}" stroke="{INK}" stroke-width="0.5"/>')
        t(x0 + 32, y, s, 12)
        y += 20
    y += 20
    t(x0, y, "Désiré Akai : aménagement et mobilier", 11, GRIS)
    t(x0, y + 16, "Manadja : contrôle DAO · Le Génie : avis technique", 11, GRIS)
    t(x0, y + 32, "Esquisse générée par script, à recaler après relevé", 11, GRIS)
    # nord
    nx, ny = x0 + 360, 70
    out.append(f'<path d="M{nx} {ny - 26} L{nx + 10} {ny + 6} L{nx} {ny} L{nx - 10} {ny + 6} Z" fill="{INK}"/>')
    t(nx, ny + 22, "N", 12, poids=700, ancre="middle")
    # échelle
    sx, sy = 120, 1215
    for i in range(5):
        out.append(f'<rect x="{sx + i * S}" y="{sy}" width="{S}" height="6" fill="{INK if i % 2 == 0 else "#ffffff"}" stroke="{INK}" stroke-width="0.6"/>')
        t(sx + i * S, sy + 22, f"{i}", 10, ancre="middle")
    t(sx + 5 * S, sy + 22, "5 m", 10, ancre="middle")
    return out


def svg():
    surf = construire()
    w, h = 1400, 1260
    defs = (f'<defs><marker id="fl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{GRIS}"/></marker></defs>')
    corps = "".join(el) + "".join(cartouche(surf))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{defs}'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>{corps}</svg>'), surf


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    s, surf = svg()
    chemin = os.path.join(SORTIE, "E01_plan_amenagement.svg")
    open(chemin, "w", encoding="utf-8").write(s)
    print(chemin)
    for k, v in surf.items():
        print(f"  {k}: {v:.2f} m²")
