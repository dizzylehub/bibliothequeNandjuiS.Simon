"""Plans techniques d'esquisse T01 à T03 (Le Génie), sur le fond du plan E01.

T01 électricité et éclairage, T02 plomberie (AEP, EU, EV), T03 climatisation et ventilation.
Niveau : principe d'esquisse. Puissances et débits sont des ordres de grandeur à confirmer
par un électricien, un plombier et un frigoriste, après relevé des réseaux existants.

Usage : python3 v8/scripts/plans_techniques.py  ->  v8/plans/T01..T03_*.svg
"""
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import plan_esquisse as G  # noqa: E402

px, py, S = G.px, G.py, G.S
FONT = G.FONT
INK, GRIS = G.INK, G.GRIS


class Calque:
    def __init__(self):
        self.el = []

    def add(self, s):
        self.el.append(s)

    def t(self, x, y, s, taille=10, col=INK, ancre="middle", poids=400, rot=0):
        X, Y = px(x), py(y)
        tr = f' transform="rotate({rot} {X:.1f} {Y:.1f})"' if rot else ""
        self.add(f'<text x="{X:.1f}" y="{Y:.1f}" font-family="{FONT}" font-size="{taille}" font-weight="{poids}" fill="{col}" '
                 f'text-anchor="{ancre}"{tr}>{s}</text>')

    def trace(self, pts, col, sw=2.0, dash=None):
        d = "M" + " L".join(f"{px(x):.1f} {py(y):.1f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"{da}/>')

    def pt(self, x, y, col, r=5, forme="rond", plein=True):
        X, Y = px(x), py(y)
        f = col if plein else "#ffffff"
        if forme == "rond":
            self.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="{f}" stroke="{col}" stroke-width="1.4"/>')
        elif forme == "croix":
            self.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="#ffffff" stroke="{col}" stroke-width="1.4"/>'
                     f'<path d="M{X - r * .7:.1f} {Y - r * .7:.1f} L{X + r * .7:.1f} {Y + r * .7:.1f} M{X - r * .7:.1f} {Y + r * .7:.1f} '
                     f'L{X + r * .7:.1f} {Y - r * .7:.1f}" stroke="{col}" stroke-width="1.2"/>')
        elif forme == "carre":
            self.add(f'<rect x="{X - r:.1f}" y="{Y - r:.1f}" width="{2 * r}" height="{2 * r}" fill="{f}" stroke="{col}" stroke-width="1.4"/>')
        elif forme == "tri":
            self.add(f'<path d="M{X:.1f} {Y - r:.1f} L{X + r:.1f} {Y + r:.1f} L{X - r:.1f} {Y + r:.1f} Z" fill="{f}" stroke="{col}" stroke-width="1.4"/>')
        elif forme == "losange":
            self.add(f'<path d="M{X:.1f} {Y - r:.1f} L{X + r:.1f} {Y:.1f} L{X:.1f} {Y + r:.1f} L{X - r:.1f} {Y:.1f} Z" fill="{f}" stroke="{col}" stroke-width="1.4"/>')

    def boite(self, x0, y0, x1, y1, col, plein="#ffffff", sw=1.4, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{px(min(x0, x1)):.1f}" y="{py(max(y0, y1)):.1f}" width="{abs(x1 - x0) * S:.1f}" height="{abs(y1 - y0) * S:.1f}" '
                 f'fill="{plein}" stroke="{col}" stroke-width="{sw}"{da}/>')


def fond():
    G.el.clear()
    G.construire()
    return '<g style="filter:grayscale(1)" opacity="0.32">' + "".join(G.el) + "</g>"


def page(nom, titre, sous, calque, legende, notes, bilan=None):
    x0 = 1010
    out = []

    def t(x, y, s, taille=13, col=INK, poids=400, ancre="start"):
        out.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{taille}" font-weight="{poids}" fill="{col}" text-anchor="{ancre}">{s}</text>')

    t(x0, 90, "CAFÉ-BIBLIOTHÈQUE NANDJUI", 20, poids=700)
    t(x0, 116, titre, 15)
    t(x0, 138, sous, 11, GRIS)
    y = 180
    t(x0, y, "LÉGENDE", 11, GRIS, 700)
    y += 22
    for col, forme, lib in legende:
        c = Calque()
        X, Y = x0 + 10, y - 4
        if forme == "trait":
            out.append(f'<line x1="{x0}" y1="{Y}" x2="{x0 + 22}" y2="{Y}" stroke="{col}" stroke-width="3"/>')
        elif forme == "tirets":
            out.append(f'<line x1="{x0}" y1="{Y}" x2="{x0 + 22}" y2="{Y}" stroke="{col}" stroke-width="2.4" stroke-dasharray="5 3"/>')
        else:
            c.pt(0, 0, col, forme=forme)
            out.append(f'<g transform="translate({X - px(0):.1f} {Y - py(0):.1f})">{"".join(c.el)}</g>')
        t(x0 + 32, y, lib, 12)
        y += 20
    y += 16
    if bilan:
        t(x0, y, bilan[0], 11, GRIS, 700)
        y += 20
        for a, b in bilan[1]:
            gras = 700 if a.startswith("Total") else 400
            t(x0, y, a, 12, poids=gras)
            t(x0 + 360, y, b, 12, poids=gras, ancre="end")
            y += 18
        y += 16
    t(x0, y, "NOTES DU GÉNIE", 11, GRIS, 700)
    y += 20
    for n in notes:
        for ligne in n:
            t(x0, y, ligne, 11, "#b0582b" if ligne.startswith("!") else INK)
            y += 15
        y += 6
    y += 14
    t(x0, y, "Le Génie : études techniques · Manadja : coordination DAO", 11, GRIS)
    t(x0, y + 16, "Esquisse de principe, pas un plan d'exécution", 11, GRIS)
    w, h = 1400, 1260
    corps = fond() + "".join(calque.el) + "".join(o.replace(">!", ">") for o in out)
    defs = (f'<defs><marker id="fl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{GRIS}"/></marker></defs>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{defs}'
           f'<rect width="{w}" height="{h}" fill="#ffffff"/>{corps}</svg>')
    chemin = os.path.join(ICI, "..", "plans", nom)
    open(chemin, "w", encoding="utf-8").write(svg)
    print(chemin)


# =================================================================== T01
def t01():
    ECL, PC, CMD, SEC, TER = "#e08a1e", "#2f6fb0", "#3f8a4a", "#c0392b", "#7a4bb0"
    c = Calque()
    # tableau
    c.boite(0.0, 2.02, 0.22, 2.24, SEC, plein=SEC)
    c.t(0.30, 2.08, "TD", 10, SEC, "start", 700)
    # éclairage : lignes LED dans le plafond en lames (bibliothèque)
    for x in (3.75, 4.85, 5.95):
        c.trace([(x, 0.6), (x, 3.2)], ECL, 3)
        c.trace([(x, 4.4), (x, 7.0)], ECL, 3)
    # rail lumineux sur le mur de la collection
    c.trace([(6.30, 0.4), (6.30, 3.2)], ECL, 2, "6 3")
    c.trace([(6.30, 4.3), (6.30, 7.15), (3.3, 7.15)], ECL, 2, "6 3")
    # suspensions globe : table d'hôtes, comptoir, salle de réunion
    for (x, y) in ((4.45, 2.25), (5.25, 2.25), (1.88, 1.2), (1.88, 1.8), (1.0, 3.0), (1.0, 3.8)):
        c.pt(x, y, ECL, 7, "rond")
    # lampadaires du salon et de la banquette (prises de sol commandées)
    for (x, y) in ((4.30, 5.65), (6.30, 5.65), (6.15, 0.75)):
        c.pt(x, y, ECL, 6, "croix")
    # WC : plafonnier + détection
    for x in (0.62, 2.17):
        c.pt(x, 6.9, ECL, 6, "croix")
        c.pt(x, 5.55, CMD, 4, "tri")
    # terrasse : globes sous pergola, guirlande, balisage du claustra
    for x in (0.2, 2.3, 4.5, 6.6):
        for y in (-1.6, -3.6):
            c.pt(x, y, TER, 7, "rond")
    c.trace([(-0.9, -4.9), (1.25, -4.6), (3.4, -4.9), (5.55, -4.6), (7.7, -4.9)], TER, 1.6, "2 4")
    for x in (-0.6, 1.4, 5.8, 7.6):
        c.pt(x, -5.25, TER, 4, "losange")
    # prises
    PCs = [(0.65, 0.55, "café 20 A"), (0.65, 1.0, "moulin"), (0.65, 1.95, "froid"), (2.2, 1.0, "caisse"),
           (0.35, 3.1, ""), (0.35, 4.0, ""), (2.0, 5.02, "écran"), (2.95, 3.4, ""),
           (5.35, 3.45, "USB"), (5.35, 4.05, "USB"), (4.85, 2.25, "boîte de sol"),
           (3.3, 6.9, ""), (3.3, 0.4, "ménage"), (6.55, 0.2, ""),
           (-0.6, -2.0, "IP55"), (7.5, -2.5, "IP55")]
    for x, y, lib in PCs:
        c.pt(x, y, PC, 5, "carre")
        if lib:
            c.t(x + 0.12, y - 0.04, lib, 8, PC, "start")
    # commandes : scènes d'éclairage
    c.boite(2.30, 0.05, 2.50, 0.25, CMD, plein=CMD)
    c.t(2.40, 0.32, "scènes jour / soir / fermeture", 8, CMD)
    c.pt(3.05, 5.15, CMD, 4, "tri")
    c.pt(3.25, 0.25, CMD, 4, "tri")
    # sécurité : blocs autonomes
    for (x, y) in ((4.4, 0.12), (3.25, 2.4), (0.25, 4.5), (4.4, 7.4)):
        c.pt(x, y, SEC, 5, "losange", plein=False)
    # alimentation des groupes extérieurs (renvoi T03)
    c.trace([(0.22, 2.12), (0.22, 5.15), (3.0, 5.15)], PC, 1, "3 3")
    leg = [(ECL, "trait", "ligne LED 2 700 K gradable (plafond en lames)"), (ECL, "tirets", "rail lumineux du mur de la collection"),
           (ECL, "rond", "suspension globe opaline"), (ECL, "croix", "lampadaire ou plafonnier"),
           (TER, "rond", "globe d'extérieur IP44 sous pergola"), (TER, "losange", "balise basse du claustra"),
           (PC, "carre", "prise 16 A (sauf mention)"), (CMD, "tri", "commande ou détecteur"),
           (SEC, "losange", "bloc autonome d'éclairage de sécurité"), (SEC, "carre", "tableau divisionnaire")]
    bilan = ("BILAN DE PUISSANCE · ORDRE DE GRANDEUR", [
        ("Éclairage intérieur et terrasse (LED)", "0,9 kW"), ("Machine à café et moulin", "3,5 kW"),
        ("Froid, caisse, prises diverses", "2,0 kW"), ("Climatisation (voir T03)", "3,5 kW"),
        ("Ventilation des WC, brasseurs d'air", "0,4 kW"), ("Total installé", "10,3 kW"),
        ("Foisonné (coef. 0,7)", "≈ 7 kW")])
    notes = [["Tableau neuf avec différentiels 30 mA par groupe :", "éclairage, prises, café, climatisation, extérieur."],
             ["Trois scènes : jour (plein), soir (tamisé 30 %),", "fermeture (sécurité seule)."],
             ["!Abonnement à adapter avec la CIE après relevé du", "!compteur et de la mise à la terre existants."],
             ["!Installation existante non réutilisée : fils nus", "!et appareillage vétustes vus sur les photos."]]
    page("T01_electricite_eclairage.svg", "T01 · Électricité et éclairage · esquisse", "V8 indice B · courants forts, éclairage tamisé, sécurité",
         c, leg, notes, bilan)


# =================================================================== T02
def t02():
    AEP, EU, EV, EC = "#2f6fb0", "#3f8a4a", "#8a5a35", "#c0392b"
    c = Calque()
    # arrivée d'eau supposée au fond (hypothèse) et nourrice
    c.boite(1.30, 7.38, 1.50, 7.58, AEP, plein=AEP)
    c.t(1.55, 7.40, "compteur / nourrice (hypothèse)", 8, AEP, "start")
    c.trace([(1.40, 7.45), (0.62, 7.45), (0.62, 7.3)], AEP, 2)
    c.trace([(1.40, 7.45), (2.17, 7.45), (2.17, 7.3)], AEP, 2)
    c.trace([(0.62, 7.45), (0.10, 7.45), (0.10, 6.2)], AEP, 2)
    c.trace([(2.17, 7.45), (2.85, 7.45), (2.85, 6.8)], AEP, 2)
    c.trace([(0.10, 6.2), (0.10, 5.25), (-0.05, 5.25), (-0.05, 1.65), (0.3, 1.65)], AEP, 2, "6 3")
    c.t(-0.12, 3.6, "alimentation en plinthe vers le café", 8, AEP, rot=-90)
    # eau chaude : petit ballon sous évier
    c.boite(0.08, 0.35, 0.50, 0.75, EC)
    c.t(0.29, 0.58, "ECS 15 L", 7, EC)
    # EV : cuvettes vers descente supposée au fond
    c.pt(1.30, PROF_EV, EV, 7, "rond", plein=False)
    c.t(1.30, PROF_EV + 0.25, "descente EV (à localiser)", 8, EV)
    c.trace([(0.62, 7.25), (0.62, 7.55), (1.30, 7.55)], EV, 3)
    c.trace([(2.17, 7.25), (2.17, 7.55), (1.30, 7.55)], EV, 3)
    # EU : lave-mains et évier
    c.trace([(0.20, 6.2), (0.20, 7.5), (1.30, 7.5)], EU, 2)
    c.trace([(2.80, 6.8), (2.80, 7.5), (1.30, 7.5)], EU, 2)
    c.trace([(0.30, 1.65), (0.15, 1.65), (0.15, 5.1)], EU, 2, "6 3")
    c.trace([(0.15, 5.1), (0.15, 6.0)], EU, 2, "6 3")
    c.t(0.32, 3.0, "EU évier en chape, pente ≥ 1,5 %", 8, EU, "start", rot=-90)
    c.boite(0.05, 1.45, 0.55, 1.85, EU)
    c.t(0.30, 1.40, "évier", 8, EU)
    # condensats de climatisation
    for (x, y) in ((3.3, 6.95), (0.2, 4.9), (6.55, 3.25)):
        c.pt(x, y, EU, 3, "rond")
    c.t(4.6, 6.95, "condensats → EU (T03)", 8, EU)
    # terrasse : robinet de puisage et évacuation des eaux pluviales
    c.pt(7.6, -0.3, AEP, 5, "carre")
    c.t(7.45, -0.55, "robinet de puisage", 8, AEP, "end")
    c.trace([(-1.1, -5.3), (8.0, -5.3)], EU, 1.4, "2 3")
    c.t(3.4, -5.15, "caniveau des eaux pluviales, pente 1,5 % vers l'extérieur", 8, EU)
    leg = [(AEP, "trait", "eau froide (AEP)"), (EC, "carre", "production d'eau chaude"),
           (EU, "trait", "eaux usées (EU)"), (EV, "trait", "eaux vannes (EV)"),
           (EV, "rond", "descente existante supposée"), (AEP, "tirets", "tracé en plinthe ou en chape")]
    notes = [["Les deux WC partagent le mur du fond : une seule", "sortie EV vers la descente existante."],
             ["!Position du compteur SODECI, de la descente et", "!des pentes à relever avant tout tracé."],
             ["!L'évier du café est à 5,5 m de la descente : chape", "!à reprendre ou pompe de relevage à prévoir."],
             ["Évier et ballon : seulement si l'exploitation", "du café le demande (à confirmer avec Madame)."]]
    page("T02_plomberie.svg", "T02 · Plomberie · esquisse", "V8 indice B · eau froide, eau chaude, eaux usées et vannes", c, leg, notes)


PROF_EV = 7.75


# =================================================================== T03
def t03():
    CLIM, VMC, BR, GE = "#2f6fb0", "#6b6660", "#7a4bb0", "#c0392b"
    c = Calque()
    # unités intérieures murales
    for (x0, y0, x1, y1, lib) in ((3.2, 6.6, 3.4, 7.3, "split 18 000 BTU"), (0.05, 4.2, 0.25, 4.9, "split 9 000 BTU"),
                                  (6.38, 2.4, 6.58, 3.1, "")):
        c.boite(x0, y0, x1, y1, CLIM, plein=CLIM)
        if lib:
            c.t(x1 + 0.08, (y0 + y1) / 2, lib, 8, CLIM, "start")
    c.t(6.2, 2.75, "split 12 000 BTU", 8, CLIM, "end")
    # liaisons frigorifiques vers groupes extérieurs (au fond, hypothèse)
    c.trace([(3.3, 7.3), (3.3, 7.62)], CLIM, 2, "5 3")
    c.trace([(0.15, 4.9), (0.15, 5.2), (0.15, 7.62)], CLIM, 2, "5 3")
    c.trace([(6.48, 3.1), (6.48, 3.25), (6.62, 3.25), (6.62, 7.62)], CLIM, 2, "5 3")
    for x in (0.4, 3.3, 6.2):
        c.boite(x - 0.35, PROF_EV + 0.08, x + 0.35, PROF_EV + 0.38, GE, plein="#ffffff")
    c.t(3.3, PROF_EV + 0.6, "groupes extérieurs sur le mur nord (accès à vérifier)", 9, GE)
    # extraction WC
    for x in (0.62, 2.17):
        c.pt(x, 6.4, VMC, 6, "croix")
    c.trace([(0.62, 6.4), (0.62, 7.0), (2.17, 7.0)], VMC, 2)
    c.trace([(2.17, 6.4), (2.17, 7.0), (2.6, 7.0), (2.6, 7.62)], VMC, 2)
    c.t(2.65, 7.2, "extraction 2 × 30 m³/h", 8, VMC, "start")
    # air neuf : grilles en façade et imposte
    for (x, y) in ((1.5, 0.05), (5.95, 0.05), (1.5, 2.3)):
        c.pt(x, y, VMC, 5, "carre", plein=False)
    c.t(1.5, 2.55, "transfert d'air (imposte)", 8, VMC)
    # brasseurs d'air
    for (x, y) in ((4.85, 2.3), (5.35, 5.7), (1.9, 1.5), (1.3, -2.8), (5.55, -2.8)):
        c.pt(x, y, BR, 9, "croix")
    leg = [(CLIM, "carre", "unité intérieure de climatisation (split)"), (CLIM, "tirets", "liaisons frigorifiques et condensats"),
           (GE, "carre", "groupe extérieur"), (VMC, "croix", "bouche d'extraction"), (VMC, "carre", "entrée d'air neuf / transfert"),
           (BR, "croix", "brasseur d'air (pales bois, style mid-century)")]
    bilan = ("CHARGES DE FROID · ORDRE DE GRANDEUR", [
        ("Bibliothèque et salon, 27 m² (2 unités)", "≈ 9 kW froid"), ("Salle de réunion, 8 m² (6 pers.)", "≈ 2,6 kW froid"),
        ("Accueil-café ouvert : servi par la bibliothèque", "—"), ("Total froid", "≈ 11,5 kW"),
        ("Puissance électrique absorbée (COP ≈ 3,3)", "≈ 3,5 kW")])
    notes = [["Base de calcul : environ 300 W/m² de froid en climat", "chaud et humide, apports des occupants inclus."],
             ["WC aveugles : extraction mécanique obligatoire,", "temporisée sur l'éclairage."],
             ["Terrasse : brasseurs d'air sous la pergola, sans clim."],
             ["!Emplacement des groupes extérieurs, bruit pour les", "!logements et accord de la copropriété à valider."]]
    page("T03_climatisation_ventilation.svg", "T03 · Climatisation et ventilation · esquisse",
         "V8 indice B · confort d'été, renouvellement d'air", c, leg, notes, bilan)


if __name__ == "__main__":
    t01()
    t02()
    t03()
