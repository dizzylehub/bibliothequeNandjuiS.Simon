"""Habillage « façon Photoshop » du plan et des coupes rendus par Blender (rendu_blender.py) :
ciel en dégradé, terre, logements existants au-dessus, arbres, silhouettes, étiquettes, niveaux,
lignes de coupe, nord et échelle graphique.

Usage : python3 v8/scripts/habillage_ortho.py  ->  v8/rendus/H_PLAN.png, H_COUPE_AA.png, H_COUPE_BB.png
Les cadrages reprennent ORTHO de rendu_blender.py (à garder identiques).
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
REN = os.path.join(ICI, "..", "rendus")
POL = os.path.expanduser("~/.fonts")


def police(nom, taille):
    for f in (os.path.join(POL, nom), "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, taille)
    return ImageFont.load_default()


SERIF = lambda t: police("CormorantGaramond-Bold.ttf", t)      # noqa: E731
SERIF_I = lambda t: police("CormorantGaramond-Italic.ttf", t)  # noqa: E731
SANS = lambda t: police("Jost-Regular.ttf", t)                 # noqa: E731
SANS_B = lambda t: police("Jost-Bold.ttf", t)                  # noqa: E731

ENCRE = (35, 28, 23)
PAPIER = (244, 239, 230)

# mêmes cadrages que rendu_blender.ORTHO
ORTHO = {
    "PLAN": dict(centre=(3.2, 0.55), largeur=11.4, px=(1700, 2500)),
    "COUPE_AA": dict(centre=(1.0, 2.6), largeur=16.0, px=(2600, 1300)),
    "COUPE_BB": dict(centre=(3.4, 2.4), largeur=11.0, px=(2400, 1440)),
}


class Repere:
    """Passage mètres -> pixels pour une vue orthographique (u horizontal, v vertical)."""

    def __init__(self, vue):
        d = ORTHO[vue]
        self.W, self.H = d["px"]
        self.k = self.W / d["largeur"]
        self.u0 = d["centre"][0] - d["largeur"] / 2
        self.v1 = d["centre"][1] + self.H / self.k / 2

    def __call__(self, u, v):
        return ((u - self.u0) * self.k, (self.v1 - v) * self.k)

    def m(self, d):
        return d * self.k


def texte_espace(dr, xy, s, f, fill, esp=0.12, ancre="la"):
    """Texte en capitales espacées (sans accents sur les mots tout en capitales)."""
    x, y = xy
    largeur = sum(dr.textlength(c, font=f) for c in s) + esp * f.size * (len(s) - 1)
    if ancre[0] == "m":
        x -= largeur / 2
    for c in s:
        dr.text((x, y), c, font=f, fill=fill)
        x += dr.textlength(c, font=f) + esp * f.size


def degrade(W, H, haut, bas):
    im = Image.new("RGB", (W, H))
    dr = ImageDraw.Draw(im)
    for y in range(H):
        t = y / max(H - 1, 1)
        dr.line([(0, y), (W, y)], fill=tuple(int(haut[i] + (bas[i] - haut[i]) * t) for i in range(3)))
    return im.convert("RGBA")


def arbre(calque, cx, sol, R, haut, couleur, graine):
    """Arbre en silhouette translucide : tronc et houppier fait de disques."""
    rnd = random.Random(graine)
    dr = ImageDraw.Draw(calque)
    dr.rectangle([cx - R * 0.05, sol - haut * 0.62, cx + R * 0.05, sol], fill=couleur[:3] + (150,))
    for _ in range(46):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0, R * 0.85)
        r = rnd.uniform(R * 0.22, R * 0.42)
        x, y = cx + d * math.cos(a), sol - haut * 0.68 + d * math.sin(a) * 0.55
        dr.ellipse([x - r, y - r, x + r, y + r], fill=couleur)


def personne(dr, x, sol, k, couleur, pose=0, h=1.70):
    """Silhouette stylisée de h mètres, x et sol en pixels, k pixels par mètre."""
    m = lambda d: d * k  # noqa: E731
    tete = m(0.115)
    yt = sol - m(h) + tete
    dr.ellipse([x - tete, yt - tete, x + tete, yt + tete], fill=couleur)
    dec = m(0.04) * (1 if pose % 2 else -1)
    corps = [(x - m(0.21), sol - m(1.43)), (x + m(0.21), sol - m(1.43)), (x + m(0.17) + dec, sol - m(0.86)), (x - m(0.17) + dec, sol - m(0.86))]
    dr.polygon(corps, fill=couleur)
    ec = m(0.12 + 0.08 * (pose % 3))
    dr.polygon([(x - m(0.16) + dec, sol - m(0.88)), (x - m(0.01) + dec, sol - m(0.88)), (x - ec / 2 + m(0.03), sol), (x - ec / 2 - m(0.07), sol)], fill=couleur)
    dr.polygon([(x + m(0.01) + dec, sol - m(0.88)), (x + m(0.16) + dec, sol - m(0.88)), (x + ec / 2 + m(0.07), sol), (x + ec / 2 - m(0.03), sol)], fill=couleur)


def personne_assise(dr, x, sol, k, couleur, sens=1):
    m = lambda d: d * k  # noqa: E731
    tete = m(0.11)
    dr.ellipse([x - tete, sol - m(1.30) - tete, x + tete, sol - m(1.30) + tete], fill=couleur)
    dr.polygon([(x - m(0.19), sol - m(1.12)), (x + m(0.19), sol - m(1.12)), (x + m(0.17), sol - m(0.50)), (x - m(0.17), sol - m(0.50))], fill=couleur)
    dr.polygon([(x - m(0.12), sol - m(0.52)), (x + sens * m(0.48), sol - m(0.52)), (x + sens * m(0.48), sol - m(0.40)), (x - m(0.12), sol - m(0.40))], fill=couleur)
    dr.polygon([(x + sens * m(0.36), sol - m(0.48)), (x + sens * m(0.48), sol - m(0.48)), (x + sens * m(0.47), sol), (x + sens * m(0.37), sol)], fill=couleur)


def niveau(dr, R, u, z, libelle, couleur=ENCRE):
    x, y = R(u, z)
    dr.polygon([(x, y), (x - 9, y - 14), (x + 9, y - 14)], outline=couleur, fill=None, width=2)
    dr.line([(x - 9, y - 14), (x + 70, y - 14)], fill=couleur, width=2)
    dr.text((x + 14, y - 40), libelle, font=SANS(22), fill=couleur)


def echelle(dr, x, y, k, couleur=ENCRE):
    pas = [0, 1, 2, 5]
    for i in range(len(pas) - 1):
        x0, x1 = x + pas[i] * k, x + pas[i + 1] * k
        dr.rectangle([x0, y, x1, y + 10], fill=couleur if i % 2 == 0 else None, outline=couleur, width=2)
    for p in pas:
        dr.text((x + p * k - 6, y + 16), str(p), font=SANS(20), fill=couleur)
    dr.text((x + 5 * k + 14, y + 12), "m", font=SANS(20), fill=couleur)


def titre(dr, x, y, t, sous, couleur=ENCRE):
    dr.text((x, y), t, font=SERIF(64), fill=couleur)
    dr.text((x, y + 74), sous, font=SANS(24), fill=couleur)


# ------------------------------------------------------------------ coupes
def coupe(vue, ambiance, etiquettes, personnes, assis, arbres, batiment_u, titre_txt, sous_txt, niveaux_u):
    src = os.path.join(REN, f"R_{vue}_{ambiance}.png")
    if not os.path.exists(src):
        print("absent :", src)
        return
    R = Repere(vue)
    W, H = R.W, R.H
    soir = ambiance == "soir"
    fond = degrade(W, H, (29, 38, 56) if soir else (196, 214, 222), (201, 140, 96) if soir else (246, 238, 224))
    dr = ImageDraw.Draw(fond, "RGBA")
    # logements existants au-dessus du local (volume figuré, non relevé)
    u0, u1 = batiment_u
    x0, y0 = R(u0, 3.45)
    x1, _ = R(u1, 3.45)
    dr.rectangle([x0, 0, x1, y0], fill=(58, 52, 50, 255) if soir else (222, 214, 201, 255))
    rnd = random.Random(3)
    for niv in range(2):
        zb = 3.45 + 1.0 + niv * 3.0
        u = u0 + 0.5
        while u + 1.2 < u1:
            a = R(u, zb + 1.35)
            b = R(u + 1.0, zb)
            allume = soir and rnd.random() < 0.55
            dr.rectangle([a[0], a[1], b[0], b[1]], fill=(240, 196, 120, 255) if allume else ((40, 44, 50, 255) if soir else (170, 180, 186, 255)))
            u += 2.0
    texte_espace(dr, (R((u0 + u1) / 2, 0)[0], R(0, 3.95)[1]), "LOGEMENTS EXISTANTS (FIGURES)", SANS(22), (230, 220, 205) if soir else (110, 100, 90), 0.25, "ma")
    # arbres derrière
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for (u, Rm, hm, g) in arbres:
        x, sol = R(u, -0.15)
        arbre(calque, x, sol, R.m(Rm), R.m(hm), (34, 50, 40, 150) if soir else (96, 128, 86, 120), g)
    fond.alpha_composite(calque.filter(ImageFilter.GaussianBlur(1.2)))
    # rendu
    rendu = Image.open(src).convert("RGBA")
    ombre = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ombre.putalpha(rendu.getchannel("A").point(lambda a: int(a * 0.35)))
    fond.alpha_composite(ombre.filter(ImageFilter.GaussianBlur(14)), (10, 12))
    fond.alpha_composite(rendu)
    dr = ImageDraw.Draw(fond, "RGBA")
    # terre sous le niveau du sol
    _, ys = R(0, -0.17)
    dr.rectangle([0, ys, W, H], fill=(64, 50, 40, 255) if soir else (188, 168, 138, 255))
    for i in range(0, W, 26):
        dr.line([(i, ys + 10), (i - 40, ys + 50)], fill=(0, 0, 0, 30), width=2)
    dr.line([(0, ys), (W, ys)], fill=ENCRE + (255,), width=4)
    # silhouettes
    teinte = (28, 22, 18, 120) if soir else (40, 34, 30, 95)
    for i, u in enumerate(personnes):
        x, sol = R(u, 0)
        personne(dr, x, sol, R.k, teinte, i)
    for (u, sens) in assis:
        x, sol = R(u, 0)
        personne_assise(dr, x, sol, R.k, teinte, sens)
    # étiquettes et niveaux
    clair = (246, 238, 226) if soir else ENCRE
    for (u, z, s) in etiquettes:
        x, y = R(u, z)
        texte_espace(dr, (x, y), s, SANS_B(24), clair, 0.22, "ma")
    for (u, z, s) in niveaux_u:
        niveau(dr, R, u, z, s, clair)
    titre(dr, 70, 60, titre_txt, sous_txt, clair)
    echelle(dr, 70, H - 80, R.k, (246, 238, 226) if soir else ENCRE)
    sortie = os.path.join(REN, f"H_{vue}_{ambiance}.png")
    fond.convert("RGB").save(sortie, quality=92)
    print(sortie)


# ------------------------------------------------------------------ plan
def plan():
    src = os.path.join(REN, "R_PLAN_jour.png")
    if not os.path.exists(src):
        print("absent :", src)
        return
    R = Repere("PLAN")
    W, H = R.W, R.H
    fond = Image.new("RGBA", (W, H), PAPIER + (255,))
    # sol du quartier et ombres d'arbres, très doux
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dc = ImageDraw.Draw(calque)
    rnd = random.Random(11)
    for (cx, cy, r) in ((-3.0, -6.6, 2.6), (9.6, -7.2, 2.2), (10.0, 4.0, 1.8)):
        for _ in range(30):
            a, d = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, r * 0.8)
            rr = rnd.uniform(0.5, 1.0) * R.k
            x, y = R(cx + d * math.cos(a), cy + d * math.sin(a))
            dc.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(92, 120, 80, 70))
    fond.alpha_composite(calque.filter(ImageFilter.GaussianBlur(6)))
    rendu = Image.open(src).convert("RGBA")
    ombre = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ombre.putalpha(rendu.getchannel("A").point(lambda a: int(a * 0.4)))
    fond.alpha_composite(ombre.filter(ImageFilter.GaussianBlur(16)), (14, 18))
    fond.alpha_composite(rendu)
    dr = ImageDraw.Draw(fond, "RGBA")
    pieces = [(1.5, 1.05, "ACCUEIL CAFE", "Secrétaire · comptoir"), (1.5, 4.55, "SALLE DE REUNION", "9 places · 8,4 m²"),
              (0.62, 6.35, "WC", "salle louée"), (2.17, 6.35, "WC", "public"), (4.85, 1.0, "BIBLIOTHEQUE", "table d’hôtes · Kente"),
              (5.1, 6.55, "SALON DE LECTURE", "4 fauteuils"), (3.4, -3.0, "TERRASSE SOUS PERGOLA", "≈ 50 m² · deux salons")]
    for (x, y, nom, sous) in pieces:
        px, py = R(x, y)
        f1, f2 = SANS_B(24), SERIF_I(26)
        l1 = sum(dr.textlength(c, font=f1) for c in nom) + 0.22 * 24 * (len(nom) - 1)
        l = max(l1, dr.textlength(sous, font=f2)) + 30
        dr.rounded_rectangle([px - l / 2, py - 10, px + l / 2, py + 64], radius=10, fill=(250, 246, 238, 215))
        texte_espace(dr, (px, py), nom, f1, ENCRE, 0.22, "ma")
        w2 = dr.textlength(sous, font=f2)
        dr.text((px - w2 / 2, py + 28), sous, font=f2, fill=(90, 70, 55))
    # lignes de coupe A et B
    for (p, q, lettre) in (((4.2, -5.9), (4.2, 7.9), "A"), ((-1.6, 3.2), (8.3, 3.2), "B")):
        a, b = R(*p), R(*q)
        dr.line([a, b], fill=(176, 88, 43, 230), width=4)
        for (c, autre) in ((a, b), (b, a)):
            dr.ellipse([c[0] - 26, c[1] - 26, c[0] + 26, c[1] + 26], fill=(176, 88, 43, 255))
            w = dr.textlength(lettre, font=SANS_B(30))
            dr.text((c[0] - w / 2, c[1] - 21), lettre, font=SANS_B(30), fill=(255, 255, 255))
    # nord (façade sur la terrasse vers le sud, hypothèse)
    nx, ny = W - 140, 150
    dr.polygon([(nx, ny - 70), (nx - 26, ny + 30), (nx, ny + 10), (nx + 26, ny + 30)], fill=ENCRE)
    texte_espace(dr, (nx, ny + 40), "N", SANS_B(28), ENCRE, 0, "ma")
    dr.text((nx - 70, ny + 80), "orientation à confirmer", font=SANS(18), fill=(110, 100, 90))
    titre(dr, 70, 50, "Plan rendu", "coupé à 1,30 m · aménagement, mobilier et ombres portées")
    echelle(dr, 70, H - 90, R.k)
    sortie = os.path.join(REN, "H_PLAN_jour.png")
    fond.convert("RGB").save(sortie, quality=92)
    print(sortie)


if __name__ == "__main__":
    plan()
    # coupe AA : longitudinale dans la bibliothèque, regard vers l'ouest (accueil, salle de réunion)
    for amb in ("soir", "jour"):
        coupe("COUPE_AA", amb,
              etiquettes=[(-2.6, 3.35, "TERRASSE"), (1.2, 3.25, "ACCUEIL"), (3.7, 3.25, "SALLE DE REUNION"), (6.4, 3.25, "WC")],
              personnes=[-4.3, 0.9, 5.4], assis=[(-2.0, 1), (2.6, -1)],
              arbres=[(-6.6, 3.0, 7.0, 4), (8.6, 2.2, 5.5, 9)], batiment_u=(-0.3, 7.75),
              titre_txt="Coupe A", sous_txt="longitudinale, vers l’ouest · terrasse, accueil, salle de réunion, WC",
              niveaux_u=[(-5.0, 0.0, "± 0,00"), (7.4, 3.0, "+ 3,00 plafond"), (-0.6, 2.9, "+ 2,90 pergola")])
    coupe("COUPE_BB", "jour",
          etiquettes=[(1.5, 3.25, "SALLE DE REUNION"), (4.9, 3.25, "BIBLIOTHEQUE"), (6.4, 3.6, "")],
          personnes=[3.6], assis=[(1.0, 1), (4.6, -1)],
          arbres=[(-1.6, 1.6, 4.5, 2), (8.3, 1.6, 4.0, 5)], batiment_u=(-0.15, 6.9),
          titre_txt="Coupe B", sous_txt="transversale, vers le nord · salle de réunion vitrée et bibliothèque",
          niveaux_u=[(-1.0, 0.0, "± 0,00"), (6.95, 3.0, "+ 3,00")])
