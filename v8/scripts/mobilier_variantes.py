"""Planches de variantes mobilier (Désiré Akai) : trois propositions par meuble, une recommandée.

Usage : python3 v8/scripts/mobilier_variantes.py  ->  v8/mobilier/V_*.svg
"""
import math
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import mobilier as M  # noqa: E402

FONT, INK, GRIS, ORANGE, C = M.FONT, M.INK, M.GRIS, M.ORANGE, M.C
A30 = math.cos(math.radians(30))


def axo(vol, cx, cy, bw, bh):
    """Axonométrie isométrique d'un ensemble de volumes, centrée dans un cadre bw x bh."""
    def iso(p):
        return ((p[0] - p[1]) * A30, -(p[0] + p[1]) * 0.5 - p[2])
    pts = []
    for v in vol:
        if v[0] == "b":
            for x in (v[1], v[4]):
                for y in (v[2], v[5]):
                    for z in (v[3], v[6]):
                        pts.append(iso((x, y, z)))
        else:
            pts += [iso(v[1]), iso(v[2])]
    us, ws = [p[0] for p in pts], [p[1] for p in pts]
    ex = min(bw / (max(us) - min(us)), bh / (max(ws) - min(ws)))
    ou = cx - (max(us) + min(us)) / 2 * ex
    ow = cy - (max(ws) + min(ws)) / 2 * ex

    def I(p):
        u, w = iso(p)
        return ou + u * ex, ow + w * ex

    def cle(v):
        if v[0] == "b":
            return (v[1] + v[4]) / 2 + (v[2] + v[5]) / 2 - (v[3] + v[6]) / 2 * 0.2
        return (v[1][0] + v[2][0]) / 2 + (v[1][1] + v[2][1]) / 2
    el = []
    for v in sorted(vol, key=cle, reverse=True):
        if v[0] == "b":
            x0, y0, z0, x1, y1, z1, m = v[1:]
            for pts4, k in (([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], 1.0),
                            ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], 0.86),
                            ([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], 0.7)):
                d = " ".join(f"{I(p)[0]:.1f},{I(p)[1]:.1f}" for p in pts4)
                op = 0.45 if m == "verre" else 1
                el.append(f'<polygon points="{d}" fill="{C[m]}" fill-opacity="{op}" stroke="{INK}" stroke-width="0.5" style="filter:brightness({k})"/>')
        else:
            a, b = I(v[1]), I(v[2])
            el.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{C[v[3]]}" '
                      f'stroke-width="{max(v[4] * ex, 1.4):.1f}" stroke-linecap="round"/>')
    return el


def texte(x, y, s, taille=13, col=INK, poids=400, larg=None, inter=None):
    out = []
    if larg is None:
        out.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{taille}" font-weight="{poids}" fill="{col}">{M.esc(s)}</text>')
        return out, y + (inter or taille * 1.4)
    mots, ligne, lignes = s.split(), "", []
    for m in mots:
        if len(ligne) + len(m) + 1 > larg:
            lignes.append(ligne)
            ligne = m
        else:
            ligne = (ligne + " " + m).strip()
    lignes.append(ligne)
    inter = inter or taille * 1.42
    for i, l in enumerate(lignes):
        out.append(f'<text x="{x}" y="{y + i * inter:.0f}" font-family="{FONT}" font-size="{taille}" font-weight="{poids}" fill="{col}">{M.esc(l)}</text>')
    return out, y + len(lignes) * inter


PLANCHES = [
    dict(fichier="V1_bibliotheque", titre="La bibliothèque : trois modèles pour le mur de la collection",
         intro="Le mur fait environ 9 m de long sur 2,90 m de haut. Il porte toute la collection de Madame : c'est la pièce maîtresse du lieu.",
         variantes=[
             ("A · « Kente »", M.bibli_kente, True,
              "Les tablettes se décalent d'un module à l'autre et les fonds alternent crème, moutarde, olive et cognac. Le mur se lit comme une bande de pagne tissé, sans une seule courbe à fabriquer. Une échelle en laiton court sur un rail pour atteindre le haut.",
              ["Original et propre au lieu", "Modules droits, fabrication en série", "Échelle utile à 2,90 m"],
              ["Fonds peints à entretenir", "Hauteurs de livres limitées par case"]),
             ("B · « Claustra »", M.bibli_claustra, False,
              "Une grille de casiers de 0,40 m, dont certaines cases sont fermées par du cannage ou un claustra en terre cuite. L'esprit du modernisme tropical d'Abidjan.",
              ["Très graphique", "Cases fermées pour le rangement"],
              ["Cases de 0,40 m trop basses pour les grands livres", "Beaucoup d'assemblages"]),
             ("C · « Lutrin »", M.bibli_lutrin, False,
              "Un rayonnage continu, avec un bandeau incliné à hauteur des yeux qui présente les livres de face, comme chez un libraire, et des niches vitrées au-dessus.",
              ["Met en valeur les livres coups de cœur", "Simple à lire"],
              ["Plus classique", "Le bandeau mange une rangée de livres"])],
         reco="Recommandation de l'équipe : « Kente », la seule qui donne une identité forte au mur tout en restant faite de modules droits. Elle y ajoute les niches-vitrines pour les livres rares et le bandeau-lutrin de C sur un module près de l'entrée."),
    dict(fichier="V2_accueil", titre="Le meuble d'accueil de la gérante : trois modèles",
         intro="Madame y travaille assise, dos au mur, face aux livres. Le meuble doit accueillir, servir le café et se fermer proprement le soir.",
         variantes=[
             ("A · « Enfilade »", M.accueil_enfilade, False,
              "L'enfilade mid-century en noyer sur pieds fuselés, façade cannelée et repose-pieds en laiton (fiche M01 d'origine).",
              ["Élégant, simple à fabriquer"], ["Les machines restent visibles le soir"]),
             ("B · « Secrétaire »", M.accueil_secretaire, True,
              "L'enfilade gagne un gradin où Madame expose « le livre du jour », et un cabinet à rideau à lattes, comme un secrétaire des années 60, qui cache la machine à café à la fermeture.",
              ["Raconte la bibliothèque dès l'entrée", "Se ferme le soir : le lieu reste un salon", "Rideau à lattes : savoir-faire d'ébéniste"],
              ["Rideau à lattes à soigner (guidage)"]),
             ("C · « Comptoir-bibliothèque »", M.accueil_bibliotheque, False,
              "Un comptoir en L dont la façade côté clients est une bibliothèque ouverte : les livres commencent dès l'accueil.",
              ["Continuité avec le mur de la collection"], ["Livres exposés aux éclaboussures du café", "Plus encombrant"])],
         reco="Recommandation de l'équipe : « Secrétaire », qui reste un meuble de famille, il présente un livre à chaque visiteur et il transforme le café en salon à la fermeture."),
    dict(fichier="V3_table_reunion", titre="La table de réunion : trois modèles pour 9 places",
         intro="La salle mesure 3,00 × 2,80 m. La table fait 2,50 × 0,80 m, face à une banquette de 5 places et à 4 chaises.",
         variantes=[
             ("A · « Compas »", M.table_compas, False,
              "Plateau noyer sur deux piètements en V, inspirés des meubles de Chandigarh.",
              ["Léger, classique mid-century"], ["Les pieds en V gênent les genoux aux extrémités"]),
             ("B · « Pirogue »", M.table_pirogue, True,
              "Les extrémités du plateau s'effilent comme une pirogue de la lagune Ébrié. Un filet de laiton court au centre et cache la jonction : la table se divise en deux pour des ateliers. Pieds-lames en retrait, goulotte à câbles en laiton sous le plateau.",
              ["Histoire locale, forme mémorable", "Divisible pour la location", "Câbles cachés"],
              ["Extrémités effilées : pas de place en bout de table"]),
             ("C · « Tréteaux »", M.table_treteaux, False,
              "Deux tables de 1,25 m sur tréteaux en acier, à assembler en long, en T ou en salle de classe.",
              ["La plus modulable", "Économique"], ["Moins de caractère", "Aspect provisoire"])],
         reco="Recommandation de l'équipe : « Pirogue », une table signature, qui se divise quand même en deux pour les ateliers de location, et qui garde les 9 places."),
    dict(fichier="V4_postes_travail", titre="Les postes de travail individuels : trois modèles",
         intro="Deux postes sont prévus contre le poteau de 0,90 × 0,90 m. Le lieu doit pouvoir en offrir d'autres les jours d'affluence.",
         variantes=[
             ("A · « Arbre à travail »", M.poste_poteau, True,
              "Le poteau est habillé de lattes de noyer et devient un meuble : tablette pour deux, séparateur en feutre, étagère et deux lampes en laiton. On transforme une contrainte en pièce signature.",
              ["Valorise le poteau existant", "Deux places sans surface en plus", "Prises intégrées"],
              ["Deux places seulement"]),
             ("B · « Bureau à oreilles »", M.poste_oreilles, False,
              "Un petit bureau de 0,90 × 0,55 m avec des joues en feutre qui isolent du bruit, une étagère et une lampe.",
              ["Concentration, acoustique", "Mobile"], ["Prend de la place au sol"]),
             ("C · « Abattant »", M.poste_abattant, True,
              "Certains modules du mur de la collection cachent un abattant : on l'ouvre, on s'assoit, on travaille au milieu des livres ; on le referme le soir.",
              ["Postes en plus sans surface au sol", "Tout à fait dans le concept"], ["Places à la demande, sans lampe dédiée"])],
         reco="Recommandation de l'équipe : « Arbre à travail » pour les deux postes fixes, complété par deux ou trois « Abattants » dans le mur de la collection pour les jours d'affluence."),
]


def planche(p):
    w, h = 1800, 1180
    el = [f'<rect width="{w}" height="{h}" fill="#fbf8f2"/>']
    t, _ = texte(60, 62, p["titre"], 28, INK, 700)
    el += t
    t, _ = texte(60, 96, p["intro"], 15, GRIS)
    el += t
    for k, (nom, f, reco, idee, pour, contre) in enumerate(p["variantes"]):
        x0 = 60 + k * 570
        if reco:
            el.append(f'<rect x="{x0 - 14}" y="128" width="548" height="930" fill="none" stroke="{ORANGE}" stroke-width="2.5" rx="6"/>')
            el.append(f'<rect x="{x0 + 360}" y="116" width="160" height="26" fill="{ORANGE}" rx="4"/>')
            el.append(f'<text x="{x0 + 440}" y="134" font-family="{FONT}" font-size="12" font-weight="700" fill="#ffffff" text-anchor="middle" letter-spacing="1">RECOMMANDÉ</text>')
        el += axo(f(), x0 + 260, 370, 480, 400)
        y = 620
        t, y = texte(x0, y, nom, 20, INK, 700)
        el += t
        y += 6
        t, y = texte(x0, y, idee, 14, INK, larg=62, inter=20)
        el += t
        y += 14
        t, y = texte(x0, y, "POUR", 11, GRIS, 700)
        el += t
        for s in pour:
            t, y = texte(x0 + 10, y, "+ " + s, 13, "#3f7a4a", larg=64, inter=18)
            el += t
        y += 8
        t, y = texte(x0, y, "CONTRE", 11, GRIS, 700)
        el += t
        for s in contre:
            t, y = texte(x0 + 10, y, "– " + s, 13, ORANGE, larg=64, inter=18)
            el += t
    t, _ = texte(60, 1095, p["reco"], 16, INK, 700, larg=150, inter=22)
    el += t
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">' + "".join(el) + "</svg>"
    chemin = os.path.join(M.SORTIE, p["fichier"] + ".svg")
    open(chemin, "w", encoding="utf-8").write(svg)
    print(chemin)


def vignettes(p):
    """Une axonométrie seule par variante (VAR_V1_A.svg...), pour le dossier où chaque variante a sa page."""
    out = []
    for k, (nom, f, reco, idee, pour, contre) in enumerate(p["variantes"]):
        w, h = 1400, 1100
        el = [f'<rect width="{w}" height="{h}" fill="#fbf8f2"/>'] + axo(f(), w / 2, h / 2, w - 160, h - 160)
        cle = f'VAR_{p["fichier"][:2]}_{"ABC"[k]}'
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">' + "".join(el) + "</svg>"
        open(os.path.join(M.SORTIE, cle + ".svg"), "w", encoding="utf-8").write(svg)
        out.append(dict(cle=cle, nom=nom, recommande=reco, idee=idee, pour=pour, contre=contre))
    return dict(fichier=p["fichier"], titre=p["titre"], intro=p["intro"], reco=p["reco"], variantes=out)


if __name__ == "__main__":
    import json
    os.makedirs(M.SORTIE, exist_ok=True)
    data = []
    for p in PLANCHES:
        planche(p)
        data.append(vignettes(p))
    json.dump(data, open(os.path.join(M.SORTIE, "variantes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
