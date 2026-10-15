from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1]
W, H = 2000, 1450
SAND, INK, ACCENT, WHITE = "#F4F0E8", "#202421", "#A56E46", "#FFFFFF"
canvas = Image.new("RGB", (W, H), SAND)
draw = ImageDraw.Draw(canvas)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
title = ImageFont.truetype(bold_path, 54)
subtitle = ImageFont.truetype(font_path, 25)
card_title = ImageFont.truetype(bold_path, 25)
body = ImageFont.truetype(font_path, 22)
small = ImageFont.truetype(font_path, 18)

draw.text((60, 34), "BIBLIOTHÈQUE DECIMO · A05", font=title, fill=INK)
draw.text((62, 100), "Repérage photographique — première adaptation au local existant", font=subtitle, fill=ACCENT)

cards = [
    (ROOT / "photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (4).jpeg",
     "01 · Entrée et seuil", "Grille ouvrante, porte vitrée et dallage au droit de la façade."),
    (ROOT / "photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (14).jpeg",
     "02 · Pièce claire", "Volume nu, fenêtre haute et portes latérales; hauteurs à relever."),
    (ROOT / "photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (22).jpeg",
     "03 · Pièce bleue et fond", "Espace allongé; porte en fond et plateau de rangement visible au-dessus de la séparation."),
    (ROOT / "photos/LE SITE/WhatsApp Image 2026-10-13 at 5.50.23 PM (5).jpeg",
     "04 · Avant-cour", "Muret, cheminement dallé et zone plantée; limites privatives à confirmer."),
]
margin_x, gap_x, card_w = 60, 40, 920
top_y, gap_y, card_h = 165, 24, 445
for i, (path, head, caption) in enumerate(cards):
    col, row = i % 2, i // 2
    x = margin_x + col * (card_w + gap_x)
    y = top_y + row * (card_h + gap_y)
    draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=16, fill=WHITE)
    im = Image.open(path).convert("RGB")
    im = ImageOps.fit(im, (card_w - 24, 335), method=Image.Resampling.LANCZOS)
    canvas.paste(im, (x + 12, y + 12))
    draw.text((x + 20, y + 356), head, font=card_title, fill=INK)
    draw.text((x + 20, y + 393), caption, font=small, fill=INK)

bottom_y = 1110
draw.line((60, bottom_y, W - 60, bottom_y), fill=ACCENT, width=3)
draw.text((62, bottom_y + 18), "TRADUCTION POUR L’OPTION C", font=card_title, fill=ACCENT)
left = [
    "• Accueil-café à l’entrée, géré depuis le comptoir; poste dos au mur.",
    "• Salle vitrée dans la pièce bleue, selon l’implantation demandée.",
    "• WC au fond : préserver l’intimité par un écran ajouré et ventilé.",
]
right = [
    "• Maintenir une forte capacité de rayonnages et des modules simples à fabriquer.",
    "• Étudier la terrasse sur le dallage existant sans présumer de son emprise.",
    "• Photos sans échelle : cotes, niveaux, structure et réseaux restent à relever.",
]
for j, line in enumerate(left): draw.text((62, bottom_y + 62 + j * 38), line, font=body, fill=INK)
for j, line in enumerate(right): draw.text((1030, bottom_y + 62 + j * 38), line, font=body, fill=INK)
draw.text((62, H - 38), "V6 provisoire : IFC V5 conservé comme référence; aucun mur ni réseau déplacé sur la seule base des perspectives.", font=small, fill="#555A55")

canvas.save(OUT / "A05_reperage_photos.png")
canvas.save(OUT / "A05_reperage_photos.pdf", "PDF", resolution=150)
print(OUT / "A05_reperage_photos.png")
print(OUT / "A05_reperage_photos.pdf")
