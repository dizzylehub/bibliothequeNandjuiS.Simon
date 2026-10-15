"""Page 4 — Charte graphique K&Démi (synthèse)."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-user/5dfc2a2e-f67b-5d7c-bd12-e0811e213d4e/scratchpad")
from charte_kdemi import *
from matplotlib.patches import Rectangle, PathPatch
OUT = sys.argv[1]
MM = 1 / 25.4
fig = plt.figure(figsize=(420 * MM, 297 * MM))
fig.add_artist(Rectangle((228 / 420, 0), 192 / 420, 1, transform=fig.transFigure, fc=SABLE_CLAIR, ec="none", zorder=-5))
def T(x, y, s, size, color=ENCRE, **kw):
    return fig.text(x / 420, 1 - y / 297, s, fontsize=size, color=color, va="top", **kw)
def H(x, y, s):
    return T(x, y, s, 8.5, TERRE_CUITE, fontproperties=FP_MEDIUM)

# logo principal, grand format, et déclinaison sur fond terre cuite
draw_logo(fig, 22, 40, 34)
fig.add_artist(Rectangle((22 / 420, 1 - 150 / 297), 92 / 420, 50 / 297, transform=fig.transFigure, fc=ENCRE, ec="none", zorder=-1))
draw_logo(fig, 27, 116, 17, reverse=True)
fig.add_artist(Rectangle((120 / 420, 1 - 150 / 297), 92 / 420, 50 / 297, transform=fig.transFigure, fc=SABLE, ec="none", zorder=-1))
draw_logo(fig, 125, 116, 17, inner_color=BLANC_CHAUX)
T(22, 155, "Logo sur fond sombre et sur fond sable. Zone de protection : la hauteur de l’arche tout autour.", 6.8, TAUPE)
T(22, 30, "LOGOTYPE", 8.5, TERRE_CUITE, fontproperties=FP_MEDIUM)

H(22, 170, "PALETTE")
PAL = [("Terre cuite", TERRE_CUITE, "Signature : titres, filets, accents"), ("Iroko", IROKO, "Repères, matière bois"),
       ("Sable", SABLE, "Aplats, fonds"), ("Sable clair", SABLE_CLAIR, "Panneaux, alternances"),
       ("Blanc chaux", BLANC_CHAUX, "Fond de page"), ("Encre", ENCRE, "Texte, traits"),
       ("Taupe", TAUPE, "Texte secondaire, cotes"), ("Olive", OLIVE, "Dégagements, végétal (rare)")]
for i, (nom, hx, use) in enumerate(PAL):
    x = 22 + (i % 4) * 48; y = 177 + (i // 4) * 40
    fig.add_artist(Rectangle((x / 420, 1 - (y + 20) / 297), 44 / 420, 20 / 297, transform=fig.transFigure,
                             fc=hx, ec=TAUPE if hx in (BLANC_CHAUX, SABLE_CLAIR) else "none", lw=.4))
    r, g, b = (int(hx[k:k + 2], 16) for k in (1, 3, 5))
    T(x, y + 22.5, nom, 7.4)
    T(x, y + 26.5, f"{hx.upper()}  ·  RVB {r} {g} {b}", 6, TAUPE)
    T(x, y + 30, use, 6, TAUPE)

T(236, 13, "Charte graphique", 25, ENCRE, fontproperties=FP_TITRE)
T(236, 27, "K&Démi — identité issue de la proposition Decimo", 12, TERRE_CUITE)
T(236, 35, "Arche cintrée, terre cuite et bois : la matière du projet devient l’identité de l’agence", 8.5, TAUPE)
fig.add_artist(plt.Line2D([236 / 420, 404 / 420], [1 - 42 / 297] * 2, color=TERRE_CUITE, lw=1.2))
H(236, 50, "TYPOGRAPHIES")
T(236, 58, "DM Serif Display", 20, ENCRE, fontproperties=FP_TITRE)
T(236, 68, "Titres, logotype, grands chiffres — 22 à 30 pt", 7, TAUPE)
T(236, 78, "Jost Medium — INTERTITRES EN CAPITALES", 11, ENCRE, fontproperties=FP_MEDIUM)
T(236, 86, "Intertitres 8 à 9 pt, capitales accentuées, couleur terre cuite", 7, TAUPE)
T(236, 95, "Jost Regular — texte courant, légendes et cotes.", 11, ENCRE)
T(236, 103, "Texte 7 à 10 pt, encre ou taupe ; Jost Light pour les mentions", 7, TAUPE)
H(236, 116, "ELEMENTS GRAPHIQUES".replace("ELEMENTS", "ÉLÉMENTS"))
for k, s in enumerate(["Filet terre cuite sous le titre de chaque planche",
                       "Panneau de cartouche à droite, fond sable clair",
                       "Repères mobilier : pastilles iroko ; repères de principes : pastilles encre",
                       "Dégagements et cotes de passage en olive",
                       "Tableaux : en-tête terre cuite, texte blanc ; lignes alternées sable"]):
    T(236, 124 + k * 7, "—", 7.4, TAUPE); T(241, 124 + k * 7, s, 7.4)
H(236, 166, "REGLES".replace("REGLES", "RÈGLES"))
for k, s in enumerate(["Typographie française : accents partout, y compris sur les capitales,",
                       "apostrophe typographique ’, guillemets « », espaces insécables.",
                       "Une seule couleur d’accent par planche : la terre cuite.",
                       "Le logo n’est ni déformé, ni recoloré hors des deux versions ci-contre.",
                       "Fond blanc pour les dessins techniques, sable pour les textes."]):
    T(236, 174 + k * 6.2, s, 7.4)
fig.add_artist(plt.Line2D([236 / 420, 404 / 420], [1 - 270 / 297] * 2, color=TAUPE, lw=.4))
T(236, 273, "Proposition de charte — à valider par K&Démi.", 6.2, TAUPE)
T(404, 278, "K&Démi  ·  CHARTE GRAPHIQUE  ·  Octobre 2026", 6.2, TERRE_CUITE, ha="right")
fig.savefig(OUT + ".pdf"); fig.savefig(OUT + ".png", dpi=170)
print("ok")
