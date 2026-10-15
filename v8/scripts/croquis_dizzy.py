"""Croquis de concept de Dizzy, V8 indice 0.

Dessins à main levée simulée. Géométrie : croquis de relevé du 14/10/2026
(bande gauche 3,00 m, grande salle 3,60 m, poteau 90 x 90 à 3,30 m de la façade,
parvis 2,75 m). Profondeur totale non cotée : 7,68 m repris de la V7, à relever.
Brief du 15/10 : cocon mid-century, peinture bleue supprimée, mur de la salle
de réunion remplacé par une baie vitrée.
Ils ne sont pas cotés. Au-delà du muret, les distances ne sont pas à l'échelle.

Usage, depuis la racine du dépôt :
    python3 v8/scripts/croquis_dizzy.py
Produit v8/croquis/*.svg (police Caveat intégrée, licence OFL).
"""
import base64
import math
import os
import random

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "..", "croquis")

INK = "#2a2622"
PAPIER = "#f6f1e7"
BOIS = "#c98a4b"
BLEU = "#8fc3cf"
INDIGO = "#2b4c7e"
VERT = "#3f7a4a"
AMBRE = "#f2b544"
NUIT = "#1d2a44"
GRIS = "#8b8a86"
NOYER = "#6e4325"
COGNAC = "#a85f2c"
OLIVE = "#56613a"
MOUTARDE = "#c9962e"
CREME = "#efe4cc"
TERRE = "#b5603a"

FONT = base64.b64encode(open(os.path.join(ICI, "caveat-latin.woff2"), "rb").read()).decode()


class Sk:
    def __init__(self, w, h, seed, fond=PAPIER):
        self.w, self.h, self.fond = w, h, fond
        self.R = random.Random(seed)
        self.calques = {"wash": [], "trait": [], "texte": []}

    def j(self, a):
        return self.R.uniform(-a, a)

    # ---------- traits ----------
    def line(self, p, q, w=1.5, col=INK, over=5, passes=2, jit=1.0, op=0.9):
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        for k in range(passes):
            o1, o2 = self.R.uniform(0, over), self.R.uniform(0, over)
            a = (p[0] - ux * o1 + self.j(jit), p[1] - uy * o1 + self.j(jit))
            b = (q[0] + ux * o2 + self.j(jit), q[1] + uy * o2 + self.j(jit))
            bow = self.j(min(L / 120 + 0.4, 3))
            m = ((a[0] + b[0]) / 2 - uy * bow, (a[1] + b[1]) / 2 + ux * bow)
            sw = w if k == 0 else w * 0.55
            self.calques["trait"].append(
                f'<path d="M{a[0]:.1f} {a[1]:.1f} Q{m[0]:.1f} {m[1]:.1f} {b[0]:.1f} {b[1]:.1f}" '
                f'stroke="{col}" stroke-width="{sw:.2f}" fill="none" stroke-linecap="round" opacity="{op if k == 0 else op * 0.55:.2f}"/>')

    def poly(self, pts, closed=True, **kw):
        n = len(pts)
        for i in range(n if closed else n - 1):
            self.line(pts[i], pts[(i + 1) % n], **kw)

    def wash(self, pts, col, op=0.35, couches=2):
        for k in range(couches):
            jp = [(x + self.j(3), y + self.j(3)) for x, y in pts]
            d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in jp) + "Z"
            self.calques["wash"].append(f'<path d="{d}" fill="{col}" opacity="{op / (k + 1):.2f}"/>')

    def blob(self, c, r, col, op=0.3):
        pts = []
        for i in range(18):
            a = i / 18 * 2 * math.pi
            rr = r * (1 + self.j(0.12))
            pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
        self.wash(pts, col, op, 1)

    def cercle(self, c, r, w=1.3, col=INK, tours=1.15):
        n = 28
        pts = []
        a0 = self.R.uniform(0, 6.28)
        for i in range(int(n * tours) + 1):
            a = a0 + i / n * 2 * math.pi
            rr = r * (1 + self.j(0.05))
            pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        self.calques["trait"].append(f'<path d="{d}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linejoin="round"/>')

    def courbe(self, pts, w=1.2, col=INK, op=0.9, dash=None):
        d = "M" + " L".join(f"{x + self.j(0.6):.1f} {y + self.j(0.6):.1f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.calques["trait"].append(f'<path d="{d}" stroke="{col}" stroke-width="{w}" fill="none" opacity="{op}" stroke-linecap="round"{da}/>')

    def hachures(self, pts, pas=7, angle=45, col=INK, w=0.7, op=0.5):
        """Hachures dans un polygone convexe."""
        a = math.radians(angle)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        ds = [x * nx + y * ny for x, y in pts]
        d = min(ds) + pas / 2
        while d < max(ds):
            hits = []
            for i in range(len(pts)):
                p, q = pts[i], pts[(i + 1) % len(pts)]
                dp, dq = p[0] * nx + p[1] * ny - d, q[0] * nx + q[1] * ny - d
                if dp * dq < 0:
                    t = dp / (dp - dq)
                    hits.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
            if len(hits) >= 2:
                self.line(hits[0], hits[1], w=w, col=col, over=1, passes=1, jit=0.6, op=op)
            d += pas

    def texte(self, x, y, t, taille=22, col=INK, ancre="start", poids=500, rot=0):
        tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
        t = t.replace("&", "&amp;")
        self.calques["texte"].append(
            f'<text x="{x:.0f}" y="{y:.0f}" font-family="Caveat, cursive" font-size="{taille}" '
            f'font-weight="{poids}" fill="{col}" text-anchor="{ancre}"{tr}>{t}</text>')

    def note(self, cible, pos, t, taille=22, col=INK, ancre="start"):
        """Annotation avec trait de rappel."""
        self.line(pos, cible, w=0.9, col=col, over=0, passes=1, jit=0.8, op=0.8)
        self.cercle(cible, 2.2, w=1, col=col, tours=1)
        dy = -6
        self.texte(pos[0] + (6 if ancre == "start" else -6), pos[1] + dy, t, taille, col, ancre)

    def personne(self, u, v, h, assis=False, col=INK, op=0.85):
        r = h * 0.075
        tete = (u, v - h + r)
        self.cercle(tete, r, w=1.1, col=col, tours=1.05)
        if assis:
            epaule, bassin = v - h + 2.4 * r, v - h * 0.48
            self.line((u, tete[1] + r), (u - h * 0.02, bassin), w=1.4, col=col, over=0, op=op)
            self.line((u - h * 0.02, bassin), (u + h * 0.22, bassin), w=1.3, col=col, over=0, op=op)
            self.line((u + h * 0.22, bassin), (u + h * 0.2, v), w=1.3, col=col, over=0, op=op)
            self.line((u, epaule), (u + h * 0.18, epaule + h * 0.14), w=1.1, col=col, over=0, op=op)
        else:
            bassin = v - h * 0.5
            self.wash([(u - h * 0.11, v - h + 2.3 * r), (u + h * 0.11, v - h + 2.3 * r), (u + h * 0.08, bassin), (u - h * 0.08, bassin)], col, 0.18, 1)
            self.line((u, tete[1] + r), (u, bassin), w=1.4, col=col, over=0, op=op)
            self.line((u, bassin), (u - h * 0.07, v), w=1.3, col=col, over=0, op=op)
            self.line((u, bassin), (u + h * 0.07, v), w=1.3, col=col, over=0, op=op)
            self.line((u, v - h + 2.6 * r), (u - h * 0.1, bassin + h * 0.02), w=1.1, col=col, over=0, op=op)
            self.line((u, v - h + 2.6 * r), (u + h * 0.1, bassin + h * 0.02), w=1.1, col=col, over=0, op=op)

    def cartouche(self, titre, sous_titre, num):
        self.calques["texte"].append(f'<rect x="0" y="{self.h - 92}" width="{self.w}" height="92" fill="{PAPIER}"/>')
        self.texte(40, self.h - 52, titre, 34, INK, poids=700)
        self.texte(40, self.h - 22, sous_titre, 21, GRIS)
        self.texte(self.w - 40, self.h - 22, f"Dizzy · croquis {num} · V8 indice 0 · non coté", 19, GRIS, "end")

    def svg(self):
        style = (f"<style>@font-face{{font-family:'Caveat';src:url(data:font/woff2;base64,{FONT}) format('woff2');"
                 "font-weight:400 700;}}</style>")
        corps = "".join(self.calques["wash"]) + "".join(self.calques["trait"]) + "".join(self.calques["texte"])
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">'
                f'{style}<rect width="{self.w}" height="{self.h}" fill="{self.fond}"/>{corps}</svg>')


class Cam:
    """Perspective centrale, regard vers +y."""

    def __init__(self, ex, ey, ez, f, cx, cy):
        self.e, self.f, self.c = (ex, ey, ez), f, (cx, cy)

    def P(self, x, y, z):
        d = max(y - self.e[1], 0.15)
        return (self.c[0] + self.f * (x - self.e[0]) / d, self.c[1] - self.f * (z - self.e[2]) / d)


def boite(s, C, x0, x1, y0, y1, z0, z1, w=1.4, col=INK, wash=None, op=0.35, faces="tous"):
    P = C.P
    if wash:
        s.wash([P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], wash, op * 0.8)
        s.wash([P(x0, y0, z0), P(x1, y0, z0), P(x1, y0, z1), P(x0, y0, z1)], wash, op)
    for a, b in [((x0, y0, z0), (x1, y0, z0)), ((x1, y0, z0), (x1, y0, z1)), ((x1, y0, z1), (x0, y0, z1)), ((x0, y0, z1), (x0, y0, z0)),
                 ((x0, y0, z1), (x0, y1, z1)), ((x1, y0, z1), (x1, y1, z1)), ((x0, y1, z1), (x1, y1, z1))]:
        s.line(P(*a), P(*b), w=w, col=col, over=3)
    cx = C.e[0]
    xs = x0 if cx < x0 else (x1 if cx > x1 else None)
    if xs is not None:
        s.line(P(xs, y0, z0), P(xs, y1, z0), w=w, col=col, over=3)
        s.line(P(xs, y1, z0), P(xs, y1, z1), w=w, col=col, over=3)


def epines(s, C, mur, fixe, a0, a1, z0, hmax, col=INK, pas=0.045):
    """Dos de livres sur une tablette : mur 'x' (x fixe, y varie) ou 'y'."""
    t = a0
    while t < a1:
        h = hmax * s.R.uniform(0.6, 1.0)
        if s.R.random() < 0.12:
            t += pas * 3
            continue
        p = (fixe, t, z0) if mur == "x" else (t, fixe, z0)
        q = (fixe, t, z0 + h) if mur == "x" else (t, fixe, z0 + h)
        s.line(C.P(*p), C.P(*q), w=0.9, col=col, over=0, passes=1, jit=0.3, op=0.6)
        t += pas * s.R.uniform(0.7, 1.5)


def rayonnage(s, C, mur, fixe, a0, a1, z0, z1, prof, niv=6, col_bois=BOIS, livres=True, saut=None):
    P = C.P
    if mur == "x":
        av = fixe - prof if fixe > C.e[0] else fixe + prof
        face = [P(av, a0, z0), P(av, a1, z0), P(av, a1, z1), P(av, a0, z1)]
    else:
        av = fixe - prof
        face = [P(a0, av, z0), P(a1, av, z0), P(a1, av, z1), P(a0, av, z1)]
    s.wash(face, col_bois, 0.22)
    s.poly(face, w=1.5)
    hs = [z0 + (z1 - z0) * i / niv for i in range(1, niv)]
    for z in hs:
        if mur == "x":
            s.line(P(av, a0, z), P(av, a1, z), w=1.1)
        else:
            s.line(P(a0, av, z), P(a1, av, z), w=1.1)
    n = max(1, int(round((a1 - a0) / 0.8)))
    for i in range(1, n):
        t = a0 + (a1 - a0) * i / n
        if mur == "x":
            s.line(P(av, t, z0), P(av, t, z1), w=1.0)
        else:
            s.line(P(t, av, z0), P(t, av, z1), w=1.0)
    if livres:
        for i, z in enumerate([z0] + hs):
            if saut and i in saut:
                continue
            ht = (z1 - z0) / niv * 0.8
            epines(s, C, mur, av, a0 + 0.03, a1 - 0.03, z + 0.02, ht)


# ====================================================================
def croquis_A1():
    s = Sk(1400, 900, 11)
    C = Cam(4.2, -1.1, 1.55, 430, 640, 400)
    P = C.P
    YB = 7.59
    # sol et plafond de la grande salle
    for x, z, y0 in [(6.75, 0, 0.0), (6.75, 3.0, 0.0), (3.15, 3.0, 0.0), (3.15, 0, 2.45)]:
        s.line(P(x, y0, z), P(x, YB, z), w=1.6)
    s.poly([P(3.15, YB, 0), P(6.75, YB, 0), P(6.75, YB, 3), P(3.15, YB, 3)], w=1.6)
    s.wash([P(3.15, 0.0, 0), P(6.75, 0.0, 0), P(6.75, YB, 0), P(3.15, YB, 0)], "#d9cbb4", 0.35)
    # ouverture vers l'accueil, puis vitrage du salon bleu, puis mur WC
    s.line(P(3.15, 2.75, 0), P(3.15, 2.75, 3.0), w=1.6)
    s.wash([P(3.15, 2.8, 0), P(3.15, 5.25, 0), P(3.15, 5.25, 3.0), P(3.15, 2.8, 3.0)], AMBRE, 0.18)
    for y in (2.8, 3.62, 4.43, 5.25):
        s.line(P(3.15, y, 0), P(3.15, y, 2.75), w=1.3, col=INK)
    s.line(P(3.15, 2.8, 2.75), P(3.15, 5.25, 2.75), w=1.3, col=INK)
    s.line(P(3.15, 2.8, 0.05), P(3.15, 5.25, 0.05), w=1.0, col=INK)
    # table de réunion et suspension entrevues derrière la baie
    s.blob(P(1.7, 4.0, 2.0), 30, AMBRE, 0.4)
    # buffet-café de Madame
    boite(s, C, 0.45, 1.0, 0.6, 2.1, 0, 0.95, wash=NOYER, op=0.5)
    boite(s, C, 0.6, 0.85, 1.0, 1.3, 0.95, 1.38, w=1.0)
    s.blob(P(0.72, 1.15, 1.5), 50, AMBRE, 0.3)
    # le mur de la collection (U)
    rayonnage(s, C, "x", 6.75, 0.3, 3.25, 0, 2.9, 0.32, niv=7, col_bois=NOYER)
    rayonnage(s, C, "x", 6.75, 4.25, 7.25, 0, 2.9, 0.32, niv=7, saut={2, 3}, col_bois=NOYER)
    # niches-vitrines fermées sur la travée 4-5,5 m
    for y0, y1 in [(4.5, 5.25), (5.7, 6.45)]:
        q = [P(6.43, y0, 0.83), P(6.43, y1, 0.83), P(6.43, y1, 1.66), P(6.43, y0, 1.66)]
        s.wash(q, "#ffffff", 0.5)
        s.poly(q, w=1.3, col="#9a6a2c")
        s.line(q[0], q[2], w=0.6, col=GRIS, op=0.5)
    rayonnage(s, C, "y", YB, 3.45, 6.43, 0, 2.9, 0.3, niv=7, col_bois=NOYER)
    rayonnage(s, C, "x", 3.15, 5.35, 7.29, 0, 2.9, 0.3, niv=7, col_bois=NOYER)
    # poteau
    boite(s, C, 5.85, 6.75, 3.30, 4.20, 0, 3.0, w=2.2, wash="#b9ae9c", op=0.9)
    s.note(P(5.85, 3.3, 1.0), (760, 640), "poteau 90 × 90", 22)
    # tapis tissé
    tapis = [P(3.75, 2.15, 0.01), P(5.85, 2.15, 0.01), P(5.85, 4.25, 0.01), P(3.75, 4.25, 0.01)]
    s.wash(tapis, MOUTARDE, 0.3)
    s.poly(tapis, w=0.9, col=TERRE, op=0.7)
    for k in range(1, 6):
        y = 2.15 + 2.1 * k / 6
        s.line(P(3.75, y, 0.01), P(5.85, y, 0.01), w=0.6, col=TERRE, op=0.45)
    # fauteuils
    for (x, y), col in zip([(4.03, 3.64), (5.2, 3.64), (4.03, 2.5), (5.2, 2.5)], [COGNAC, OLIVE, OLIVE, COGNAC]):
        boite(s, C, x - 0.36, x + 0.36, y - 0.36, y + 0.36, 0.18, 0.42, wash=col, op=0.45)
        boite(s, C, x - 0.36, x + 0.36, y + 0.28, y + 0.36, 0.42, 0.9, w=1.2, wash=col, op=0.45)
        for dx in (-0.3, 0.3):
            s.line(P(x + dx, y - 0.3, 0.18), P(x + dx * 1.15, y - 0.34, 0), w=1.1)
    boite(s, C, 4.35, 4.85, 2.85, 3.3, 0, 0.42, wash=NOYER, op=0.5)
    # lampadaires et suspensions
    for x, y in [(5.95, 4.15), (3.6, 2.2)]:
        s.line(P(x, y, 0), P(x, y, 1.45), w=1.3)
        s.line(P(x, y, 1.45), P(x - 0.25, y, 1.6), w=1.3)
        s.blob(P(x - 0.25, y, 1.5), 34, AMBRE, 0.35)
    for x, y in [(4.7, 1.2), (4.7, 3.1), (4.7, 5.6)]:
        s.line(P(x, y, 3.0), P(x, y, 2.35), w=0.8)
        c = P(x, y, 2.3)
        s.cercle(c, 9, w=1.2)
        s.blob(c, 40, AMBRE, 0.25)
    # table d'hôtes près de l'entrée
    boite(s, C, 3.55, 5.55, 0.9, 1.55, 0.72, 0.78, wash=NOYER, op=0.45)
    for x in (3.65, 5.45):
        for y in (0.98, 1.47):
            s.line(P(x, y, 0), P(x, y, 0.72), w=1.2)
    # lecteurs
    u, v = P(5.2, 3.64, 0)
    s.personne(u, v, P(5.2, 3.64, 0)[1] - P(5.2, 3.64, 1.25)[1], assis=True)
    u, v = P(4.9, 1.75, 0)
    s.personne(u, v, P(4.9, 1.75, 0)[1] - P(4.9, 1.75, 1.25)[1], assis=True)
    u, v = P(4.4, 5.4, 0)
    s.personne(u, v, v - P(4.4, 5.4, 1.7)[1])
    # plafond en lames de bois et corniche lumineuse
    for k in range(13):
        x = 3.3 + 3.3 * k / 12
        s.line(P(x, 0.4, 3.0), P(x, YB, 3.0), w=0.7, col=NOYER, op=0.6)
    s.wash([P(3.15, 0.4, 3.0), P(6.75, 0.4, 3.0), P(6.75, YB, 3.0), P(3.15, YB, 3.0)], NOYER, 0.25)
    s.wash([(0, 0), (s.w, 0), (s.w, s.h), (0, s.h)], AMBRE, 0.07, 1)
    # baie haute du fond
    q = [P(4.4, YB, 2.2), P(5.3, YB, 2.2), P(5.3, YB, 2.75), P(4.4, YB, 2.75)]
    s.wash(q, "#ffffff", 0.7)
    s.poly(q, w=1.2)
    # annotations
    s.note(P(6.53, 1.2, 2.3), (1040, 120), "le mur de la collection, du sol au plafond", 26)
    s.note(P(6.43, 4.9, 1.25), (1000, 330), "niches-vitrines fermées : livres rares", 22)
    s.note(P(4.8, 3.6, 0.3), (930, 760), "fauteuils mid-century en velours cognac et olive, tapis", 24)
    s.note(P(4.2, 1.2, 0.76), (420, 790), "table d'hôtes (premier plan)", 24, ancre="end")
    s.note(P(0.75, 1.4, 0.95), (110, 540), "le buffet-café de Madame", 24)
    s.note(P(3.15, 3.8, 1.8), (40, 150), "salle de réunion : le mur devient baie vitrée", 24)
    s.note(P(4.85, YB, 2.5), (700, 120), "baie haute du fond", 20)
    s.note(P(5.0, 2.0, 3.0), (720, 60), "plafond en lames de noyer, lumière tamisée", 24)
    s.cartouche("A · Le salon de Madame — un cocon mid-century",
                "Vue depuis le seuil vers le fond. Largeurs et poteau d'après votre croquis de relevé ; profondeur à relever.", "A1")
    return s


def croquis_A2():
    s = Sk(1400, 900, 22, fond=PAPIER)
    C = Cam(3.0, -9.0, 1.5, 560, 640, 470)
    P = C.P
    # ciel du soir et immeuble
    s.wash([(0, 0), (1400, 0), (1400, 380), (0, 380)], NUIT, 0.25)
    imm = [P(-0.6, 0, 0), P(7.6, 0, 0), P(7.6, 0, 9), P(-0.6, 0, 9)]
    s.wash(imm, "#b9b2a6", 0.45)
    s.poly([P(-0.6, 0, 0), P(-0.6, 0, 9)], closed=False, w=1.3)
    s.poly([P(7.6, 0, 0), P(7.6, 0, 9)], closed=False, w=1.3)
    s.line(P(-0.6, 0, 3.4), P(7.6, 0, 3.4), w=1.6)
    for z in (4.6, 7.4):
        for x0 in (0.4, 2.9, 5.4):
            q = [P(x0, 0, z), P(x0 + 1.2, 0, z), P(x0 + 1.2, 0, z + 1.1), P(x0, 0, z + 1.1)]
            s.wash(q, AMBRE if (x0 == 2.9 and z == 4.6) else NUIT, 0.4)
            s.poly(q, w=1.0, op=0.7)
    s.texte(P(6.9, 0, 6.2)[0], P(6.9, 0, 6.2)[1], "logements au-dessus", 22, GRIS, "end")
    # façade du local, éclairée
    s.wash([P(0, 0, 0), P(6.78, 0, 0), P(6.78, 0, 0.5), P(0, 0, 0.5)], TERRE, 0.4)
    s.line(P(3.07, 0, 0), P(3.07, 0, 3.4), w=1.4)
    for x0, x1, z0 in [(0.9, 1.9, 0), (4.6, 5.6, 0)]:
        q = [P(x0, 0, z0), P(x1, 0, z0), P(x1, 0, 2.5), P(x0, 0, 2.5)]
        s.wash(q, AMBRE, 0.75)
        s.poly(q, w=1.5)
        t = x0 + 0.12
        while t < x1:
            s.line(P(t, 0, z0 + 0.1), P(t, 0, z0 + s.R.uniform(0.25, 0.45)), w=0.7, op=0.5)
            t += 0.07
    # véranda à créer
    for x in (0.3, 3.4, 6.5):
        s.line(P(x, -2.4, 0), P(x, -2.4, 2.75), w=1.3)
        s.line(P(x, -2.4, 2.75), P(x, 0, 2.75), w=1.0)
    s.line(P(0.3, -2.4, 2.75), P(6.5, -2.4, 2.75), w=1.4)
    for k in range(10):
        x = 0.3 + 6.2 * k / 9
        s.line(P(x, -2.4, 2.78), P(x, 0, 2.78), w=0.6, op=0.5)
    s.note(P(5.0, -2.4, 2.75), (1170, 300), "véranda légère, à créer", 22)
    # muret et grille, portillon ouvert
    mur = [P(-0.4, -2.66, 0), P(3.3, -2.66, 0), P(3.3, -2.66, 1.0), P(-0.4, -2.66, 1.0)]
    s.wash(mur, "#d8d2c6", 0.8)
    s.poly(mur, w=1.6)
    mur2 = [P(4.4, -2.66, 0), P(7.2, -2.66, 0), P(7.2, -2.66, 1.0), P(4.4, -2.66, 1.0)]
    s.wash(mur2, "#d8d2c6", 0.8)
    s.poly(mur2, w=1.6)
    # banc maçonné côté cour
    boite(s, C, -0.4, 3.0, -3.1, -2.66, 0, 0.45, wash="#d8d2c6", op=0.6)
    # grande table familiale et bancs
    boite(s, C, 0.6, 5.2, -5.0, -4.15, 0.72, 0.78, wash=NOYER, op=0.6)
    for x in (0.7, 5.1):
        for y in (-4.95, -4.2):
            s.line(P(x, y, 0), P(x, y, 0.72), w=1.3)
    boite(s, C, 0.6, 5.2, -5.6, -5.25, 0.42, 0.46, wash=BOIS, op=0.5)
    # convives
    for x in (1.0, 1.9, 2.8, 3.8, 4.7):
        u, v = P(x, -3.9, 0.0)
        s.personne(u, v, v - P(x, -3.9, 1.3)[1], assis=True)
    for x in (1.4, 3.3, 4.3):
        u, v = P(x, -5.4, 0.0)
        s.personne(u, v, v - P(x, -5.4, 1.3)[1], assis=True, op=0.95)
    u, v = P(-0.4, -4.4, 0)
    s.personne(u, v, v - P(-0.4, -4.4, 1.65)[1])
    u, v = P(-0.75, -4.4, 0)
    s.personne(u, v, v - P(-0.75, -4.4, 1.1)[1])
    # bougies / lampes de table
    for x in (1.5, 2.9, 4.3):
        c = P(x, -4.6, 0.85)
        s.blob(c, 18, AMBRE, 0.6)
    # l'arbre
    tronc = P(8.6, -3.6, 0)
    s.line(tronc, P(8.6, -3.6, 3.2), w=4)
    s.line(P(8.6, -3.6, 2.6), P(7.0, -3.6, 4.0), w=2.5)
    s.line(P(8.6, -3.6, 3.0), P(9.8, -3.6, 4.6), w=2.5)
    for i in range(16):
        c = P(8.3 + s.j(2.8), -3.6, 4.6 + s.j(1.1))
        s.blob(c, s.R.uniform(55, 95), VERT, 0.18)
        s.cercle(c, s.R.uniform(30, 55), w=0.8, col=VERT, tours=0.6)
    # guirlandes
    for (a, b) in [((0.0, -2.4, 2.75), (7.4, -4.0, 3.6)), ((-0.3, -2.66, 1.0), (7.6, -4.6, 3.2)), ((3.4, -2.4, 2.75), (-0.5, -6.0, 2.2))]:
        pa, pb = P(*a), P(*b)
        pts = []
        for k in range(21):
            t = k / 20
            pts.append((pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t + 60 * math.sin(math.pi * t)))
        s.courbe(pts, w=1.0)
        for p in pts[1:-1:2]:
            s.blob(p, 7, AMBRE, 0.9)
    # sol
    for k in range(9):
        y = -2.7 - k * 0.7
        s.line(P(-1.5, y, 0), P(7.8, y, 0), w=0.6, op=0.35)
    s.texte(200, 380, "♪ musique douce", 30, INK)
    s.note(P(2.9, -4.6, 0.78), (300, 700), "la grande table familiale", 26)
    s.note(P(-0.2, -2.9, 0.45), (40, 430), "banc maçonné contre le muret", 22)
    s.note(P(3.85, -2.66, 0.5), (640, 840 - 70), "portillon : la cour ferme à clé", 22)
    s.note(P(2.0, 0, 2.0), (90, 220), "la façade éclairée, lumière tamisée", 24)
    s.texte(P(8.6, -3.6, 0)[0], P(8.6, -3.6, 0)[1] + 28, "arbre existant (essence à confirmer)", 20, GRIS, "middle")
    s.cartouche("A · Le salon de Madame — la cour du soir",
                "Espace devant le muret : accord écrit à obtenir. La direction doit aussi fonctionner dans le seul parvis clos.", "A2")
    return s


def croquis_B1():
    s = Sk(1500, 820, 33)
    k = 62

    def U(y):  # profondeur -> abscisse ; au-delà de -3,4 m : distances non à l'échelle
        if y < -3.4:
            y = -3.4 + (y + 3.4) * 0.75
        return 90 + (7.68 - y) * k

    def V(z):
        return 600 - z * k

    def Q(y, z):
        return (U(y), V(z))

    def rect(y0, y1, z0, z1, **kw):
        return [Q(y0, z0), Q(y1, z0), Q(y1, z1), Q(y0, z1)]

    # sol, dalle haute, logements
    cut = rect(7.68, -0.09, -0.25, 0)
    s.wash(cut, INK, 0.75, 1)
    s.line(Q(-0.09, 0), Q(-14, 0), w=1.6)
    s.hachures([Q(-0.09, 0), Q(-14, 0), Q(-14, -0.3), Q(-0.09, -0.3)], pas=9, op=0.35)
    dal = rect(7.68, -0.6, 3.3, 3.5)
    s.wash(dal, INK, 0.75, 1)
    s.poly(rect(7.68, -0.6, 3.5, 6.4), w=1.0, op=0.45)
    for y0 in (6.5, 3.8, 1.2):
        s.poly(rect(y0, y0 - 1.3, 4.4, 5.6), w=0.8, op=0.45)
    s.texte(U(3.6), V(6.0), "logements au-dessus : musique douce, horaires fixés", 24, GRIS, "middle")
    # mur du fond et façade coupés
    s.wash(rect(7.68, 7.59, 0, 3.3), INK, 0.75, 1)
    s.wash(rect(0.0, -0.09, 2.6, 3.3), INK, 0.75, 1)
    s.wash(rect(0.0, -0.09, 0, 0.35), INK, 0.75, 1)
    # le ruban : rayonnage le long du mur est (élévation au-delà)
    ruban = rect(7.3, 4.25, 0, 2.6)
    s.wash(ruban, VERT, 0.22)
    s.poly(ruban, w=1.6, col=VERT)
    ruban2 = rect(3.25, 0.35, 0, 2.6)
    s.wash(ruban2, VERT, 0.22)
    s.poly(ruban2, w=1.6, col=VERT)
    for (a, b) in [(7.3, 4.25), (3.25, 0.35)]:
        for i in range(1, 7):
            z = 2.6 * i / 7
            s.line(Q(a, z), Q(b, z), w=0.9, col=VERT)
        y = a
        while y > b + 0.1:
            for i in range(7):
                z = 2.6 * i / 7 + 0.03
                yy = y
                while yy > max(y - 0.8, b) + 0.05:
                    h = s.R.uniform(0.18, 0.3)
                    s.line(Q(yy, z), Q(yy, z + h), w=0.7, over=0, passes=1, jit=0.2, op=0.5)
                    yy -= s.R.uniform(0.04, 0.07)
            s.line(Q(y - 0.8, 0), Q(y - 0.8, 2.6), w=0.9, col=VERT)
            y -= 0.8
    s.poly(rect(4.2, 3.3, 0, 3.3), w=1.2)
    s.texte(U(3.75), V(1.6), "poteau", 18, GRIS, "middle", rot=-90)
    # vitrine qui traverse la façade
    vit = rect(0.35, -0.45, 0.45, 2.3)
    s.wash(vit, VERT, 0.35)
    s.poly(vit, w=1.8, col=VERT)
    for i in range(1, 4):
        z = 0.45 + 1.85 * i / 4
        s.line(Q(0.35, z), Q(-0.45, z), w=1.0, col=VERT)
    # claustra de la façade-lanterne
    for i in range(9):
        z = 0.4 + i * 0.24
        s.line(Q(-0.12, z), Q(-0.12, z + 0.16), w=2.2, col=INK)
    s.blob(Q(0.1, 1.4), 70, AMBRE, 0.35)
    # auvent à créer
    s.line(Q(-0.09, 2.75), Q(-2.5, 2.65), w=1.6)
    s.line(Q(-2.5, 2.65), Q(-2.5, 0), w=1.3)
    # banc-ruban
    banc = [Q(-0.45, 0.45), Q(-2.55, 0.45), Q(-2.55, 0), Q(-0.45, 0)]
    s.wash(banc, VERT, 0.4)
    s.poly(banc, w=1.6, col=VERT)
    # muret + assise
    s.poly(rect(-2.6, -2.8, 0, 1.0), w=1.5)
    s.hachures(rect(-2.6, -2.8, 0, 1.0), pas=6, op=0.5)
    s.wash(rect(-2.4, -3.0, 1.0, 1.08), VERT, 0.6, 1)
    s.line(Q(-2.4, 1.08), Q(-3.0, 1.08), w=1.6, col=VERT)
    # coupure d'échelle
    yb = -3.4
    pts = [(U(yb), V(-0.4)), (U(yb) - 8, V(0.2)), (U(yb) + 8, V(0.5)), (U(yb), V(1.2))]
    s.courbe(pts, w=1.3)
    s.texte(U(yb), V(-1.45), "coupure : non à l'échelle au-delà", 18, GRIS, "middle")
    # scène en option
    sc = [Q(-4.2, 0.2), Q(-6.0, 0.2), Q(-6.0, 0), Q(-4.2, 0)]
    s.wash(sc, BOIS, 0.4)
    s.poly(sc, w=1.2)
    u, v = Q(-5.1, 0.2)
    s.personne(u, v, 1.7 * k)
    s.line((u + 14, v - 70), (u + 30, v - 60), w=1.6, col=BOIS)
    # gradins bas tournés vers la musique, à l'ombre de l'arbre
    marches = [(-6.8, -7.6, 0.4), (-7.6, -8.4, 0.8), (-8.4, -9.2, 1.2)]
    for y0, y1, z in marches:
        r = rect(y0, y1, 0, z)
        s.wash(r, VERT, 0.35)
        s.poly(r, w=1.6, col=VERT)
    for (y, z) in [(-7.2, 0.4), (-8.0, 0.8), (-8.8, 1.2)]:
        u, v = Q(y, z)
        s.personne(u, v, 1.3 * k, assis=True)
    # arbre
    yt = -11.0
    s.line(Q(yt, 0), Q(yt, 3.4), w=5)
    s.line(Q(yt, 2.8), Q(yt + 2.6, 4.6), w=3)
    s.line(Q(yt, 3.2), Q(yt - 2.0, 4.9), w=3)
    for i in range(18):
        c = Q(yt + s.j(4.2), 5.4 + s.j(1.2))
        s.blob(c, s.R.uniform(35, 70), VERT, 0.2)
        s.cercle(c, s.R.uniform(20, 38), w=0.8, col=VERT, tours=0.6)
    # guirlandes
    pa, pb = Q(-3.0, 2.2), Q(yt + 1.5, 4.4)
    pts = [(pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t + 40 * math.sin(math.pi * t)) for t in [i / 20 for i in range(21)]]
    s.courbe(pts)
    for p in pts[1:-1:2]:
        s.blob(p, 6, AMBRE, 0.9)
    # numérotation du ruban
    for n, (y, z, t) in enumerate([(5.4, 2.9, "rayonnage"), (0.0, 2.95, "vitrine"), (-1.5, 0.8, "banc"),
                                    (-2.7, 1.35, "assise du muret"), (-8.0, 1.6, "gradins")], 1):
        u, v = Q(y, z)
        s.cercle((u, v - 14), 13, w=1.4, col=VERT)
        s.texte(u, v - 6, str(n), 22, VERT, "middle", 700)
        s.texte(u + 18, v - 6, t, 24, INK)
    s.texte(U(5.4), V(-0.9), "la salle de lecture", 24, GRIS, "middle")
    s.texte(U(-1.5), V(-0.9), "parvis + auvent à créer", 22, GRIS, "middle")
    s.texte(U(-5.1), V(-0.9), "musique (scène en option)", 22, GRIS, "middle")
    s.texte(U(-9.5), V(-0.9), "sous l'arbre", 22, GRIS, "middle")
    s.cartouche("B · Sous le badamier — un seul ruban, du fond de la salle à l'arbre",
                "Coupe de principe développée. Ruban en teck, modules droits. Au-delà du muret : espace commun, accord écrit à obtenir.", "B1")
    return s


def croquis_B2():
    s = Sk(1300, 900, 44)
    k = 110
    ox, oz = 280, 690

    def Q(x, z):
        return (ox + x * k, oz - z * k)

    def rect(x0, x1, z0, z1):
        return [Q(x0, z0), Q(x1, z0), Q(x1, z1), Q(x0, z1)]

    s.wash([(0, 0), (1300, 0), (1300, 760), (0, 760)], NUIT, 0.55)
    s.wash(rect(-0.8, 7.6, 3.3, 6.2), "#3b4660", 0.6)
    for x0 in (0.3, 2.9, 5.4):
        q = rect(x0, x0 + 1.3, 4.3, 5.5)
        s.wash(q, AMBRE if x0 == 5.4 else NUIT, 0.5)
        s.poly(q, w=1.0, col="#d9d4c7", op=0.6)
    s.texte(Q(3.4, 5.9)[0], Q(3.4, 5.9)[1], "logements au-dessus", 22, "#d9d4c7", "middle")
    fac = rect(0, 6.78, 0, 3.3)
    s.wash(fac, "#e6dfd2", 0.85)
    s.poly(fac, w=1.8)
    s.wash(rect(0, 6.78, 0, 0.5), TERRE, 0.5)
    s.line(Q(-0.8, 3.3), Q(7.6, 3.3), w=1.6)
    # claustra-livres dans les trois baies
    s.wash(rect(3.0, 3.15, 0, 3.3), "#cfc6b5", 0.9, 1)
    s.poly(rect(3.0, 3.15, 0, 3.3), w=1.2)
    for x0, x1, z0 in [(0.7, 2.1, 0.0), (4.6, 5.6, 0.0)]:
        r = rect(x0, x1, z0, 2.6)
        s.wash(r, AMBRE, 0.9)
        s.blob(Q((x0 + x1) / 2, 1.5), 120, AMBRE, 0.35)
        x = x0 + 0.04
        while x < x1 - 0.04:
            wv = s.R.uniform(0.04, 0.11)
            h0 = z0 + s.R.uniform(0.05, 0.25)
            h1 = 2.6 - s.R.uniform(0.05, 0.3)
            s.wash(rect(x, x + wv, h0, h1), INK, 0.85, 1)
            x += wv + s.R.uniform(0.05, 0.12)
        s.poly(r, w=2)
        for z in (z0 + 0.65 * (2.6 - z0), ):
            s.line(Q(x0, z), Q(x1, z), w=2.4)
    # vitrine du ruban, visible derrière la baie droite
    s.wash(rect(0.75, 2.05, 0.9, 1.0), VERT, 0.8, 1)
    s.wash(rect(0.75, 2.05, 1.6, 1.7), VERT, 0.8, 1)
    # enseigne
    s.texte(Q(3.4, 3.07)[0], Q(3.4, 3.07)[1], "[nom à venir] · café-bibliothèque", 28, INK, "middle", 700)
    # auvent à créer
    s.wash(rect(-0.2, 7.0, 2.72, 2.84), INK, 0.8, 1)
    s.line(Q(-0.2, 2.72), Q(7.0, 2.72), w=2.0)
    for x in (0.0, 3.4, 6.8):
        s.line(Q(x, 2.72), Q(x, 0), w=1.0, op=0.5)
    # banc-ruban devant
    b = rect(2.3, 4.4, 0, 0.45)
    s.wash(b, VERT, 0.7)
    s.poly(b, w=1.6)
    # personnes en contre-jour
    for x, assis in [(0.4, False), (2.6, True), (3.4, True), (5.1, False), (6.2, False)]:
        u, v = Q(x, 0.45 if assis else 0)
        s.personne(u, v, (1.25 if assis else 1.72) * k, assis=assis, col=INK, op=1)
    # branche de l'arbre et guirlande
    s.line((1300, 120), (1050, 200), w=4, col="#13241a")
    s.line((1120, 180), (980, 140), w=2.5, col="#13241a")
    for i in range(10):
        s.blob((1180 + s.j(140), 120 + s.j(90)), s.R.uniform(40, 80), VERT, 0.35)
    pts = [(Q(6.9, 3.0)[0] + (1080 - Q(6.9, 3.0)[0]) * t, Q(6.9, 3.0)[1] + (200 - Q(6.9, 3.0)[1]) * t + 50 * math.sin(math.pi * t)) for t in [i / 16 for i in range(17)]]
    s.courbe(pts, col="#d9d4c7")
    for p in pts[1:-1]:
        s.blob(p, 6, AMBRE, 0.95)
    # sol
    s.line(Q(-1.2, 0), Q(8.2, 0), w=1.8)
    s.hachures([Q(-1.2, 0), Q(8.2, 0), Q(8.2, -0.25), Q(-1.2, -0.25)], pas=8, op=0.4)
    s.note(Q(5.1, 1.9), (40, 160), "claustra de dos de livres : l'héritage du modernisme tropical d'Abidjan", 26, "#f6f1e7")
    s.note(Q(1.4, 1.65), (840, 300), "la porte barrée devient la vitrine du ruban", 24, "#f6f1e7")
    s.note(Q(3.9, 0.3), (1000, 640), "banc-ruban", 24, "#f6f1e7")
    s.note(Q(0.2, 2.78), (40, 260), "auvent léger à créer", 22, "#f6f1e7")
    s.cartouche("B · Sous le badamier — la façade-lanterne, la nuit",
                "Élévation de principe : deux portes d'après votre croquis ; hauteurs de la maquette V7, à relever.", "B2")
    return s


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    for nom, f in [("A1_cocon_mid_century", croquis_A1), ("A2_la_cour_du_soir", croquis_A2),
                   ("B1_le_ruban_coupe", croquis_B1), ("B2_facade_lanterne", croquis_B2)]:
        chemin = os.path.join(SORTIE, nom + ".svg")
        open(chemin, "w", encoding="utf-8").write(f().svg())
        print(chemin)
