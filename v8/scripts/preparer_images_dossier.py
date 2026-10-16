# Prépare les images du dossier (v8/dossier/img) depuis la racine du dépôt.
# Usage : python3 v8/scripts/preparer_images_dossier.py
from PIL import Image
import json, os
src = {
 "photo_facade": "photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (1).jpeg",
 "photo_salle": "photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (10).jpeg",
 "photo_bleue": "photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (22).jpeg",
 "photo_arbre": "photos/LE SITE/WhatsApp Image 2026-10-13 at 5.50.23 PM (5).jpeg",
 "releve": "photos/releve/croquis_releve_facade_en_bas.png",
 "A1": "v8/croquis/A1_cocon_mid_century.png", "A2": "v8/croquis/A2_terrasse_pergola.png",
 "B1": "v8/croquis/B1_le_ruban_coupe.png", "B2": "v8/croquis/B2_facade_lanterne.png",
 "E01": "v8/plans/E01_plan_amenagement.png", "T01": "v8/plans/T01_electricite_eclairage.png",
 "T02": "v8/plans/T02_plomberie.png", "T03": "v8/plans/T03_climatisation_ventilation.png",
 "V01": "v8/vues/V01_axo_coupe_2m60.png", "V02": "v8/vues/V02_axo_terrasse.png",
 "P1": "v8/vues/P1_depuis_entree.png", "P2": "v8/vues/P2_depuis_salon.png", "P3": "v8/vues/P3_terrasse.png",
}
for f in os.listdir("v8/mobilier"):
    if f.endswith(".png"):
        src[f[:-4]] = "v8/mobilier/" + f
# rendus réalistes (Blender), rendus studio du mobilier, images d'ambiance IA
for dossier, prefixe in (("v8/rendus", ""), ("v8/rendus/mobilier", "S_"), ("v8/rendus/ia", "")):
    if os.path.isdir(dossier):
        for f in os.listdir(dossier):
            if f.endswith(".png") or f.endswith(".jpg"):
                src[prefixe + f.rsplit(".", 1)[0]] = os.path.join(dossier, f)
dims = {}
for k, p in src.items():
    im = Image.open(p).convert("RGB")
    # retire le bandeau de titre des rendus calculés (le dossier a ses propres titres)
    if k in ("P1", "P2", "P3"):
        im = im.crop((0, 150, im.width, im.height))
    if k in ("V01", "V02"):
        im = im.crop((0, 130, im.width, im.height))
    im.thumbnail((2400, 2400))
    out = f"v8/dossier/img/{k}.jpg"
    im.save(out, "JPEG", quality=86)
    dims[k] = [im.width, im.height]
json.dump(dims, open("v8/dossier/img/dims.json", "w"), indent=0)
print(len(dims), "images")
