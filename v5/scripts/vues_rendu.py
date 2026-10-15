"""Vues perspectives propres pour les rendus finaux (fal) : v5/vues_rendu/.

Pour chaque vue : <nom>_ombre.png (couleurs matériaux, sans légende ni cartouche),
<nom>_traits.png (silhouettes / arêtes) et <nom>_camera.json (cadrage reproductible).
Usage : python3 v5/scripts/vues_rendu.py [largeur hauteur]
"""
import os, sys, json, hashlib, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import VUES, V5_IFC  # noqa
from scene import charger, triangles, role  # noqa
from rendu_gl import render, camera_info  # noqa

SIZE = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (2560, 1600)
EXT = dict(shadows=True, sun_dir=(-0.38, -0.62, 0.69), sky=(0.80, 0.82, 0.86), ground=(0.50, 0.45, 0.40), fill_k=0.0, exposure=1.0)
INT = dict(shadows=True, sun_dir=(-0.30, -0.70, 0.65), sky=(0.98, 0.95, 0.90), ground=(0.86, 0.80, 0.72),
           sun_col=(1.0, 0.90, 0.76), fill_dir=(0.15, -1.0, 0.25), fill_k=0.22, exposure=0.92, emissive=1.25,
           background=(0.95, 0.93, 0.90))
VIEWS = {
    "01_devanture_rue_pieton": (dict(position=(1.55, -7.70, 1.60), target=(3.75, 0.0, 2.55), fov_v=54.0), EXT, ("sol_ext",),
                                "Devanture sur rue, vue piéton depuis le trottoir opposé (œil à 1,60 m)"),
    "02_interieur_depuis_entree": (dict(position=(4.10, 0.45, 1.55), target=(4.70, 6.60, 1.75), fov_v=58.0), INT, ("sol_ext",),
                                   "Salle de lecture depuis le seuil : accueil, salon, arbre à livres, niches"),
    "03_interieur_vers_devanture": (dict(position=(3.55, 6.80, 1.55), target=(4.30, 0.0, 1.45), fov_v=58.0), INT, ("sol_ext",),
                                    "Depuis le fond (niches) vers la devanture : portail, vitrage, claustras"),
    "04_arbre_a_livres": (dict(position=(3.40, 3.25, 1.20), target=(4.75, 5.61, 2.25), fov_v=62.0), INT, ("sol_ext",),
                          "Arbre à livres et oculus indigo, contre-plongée"),
    "05_coin_lecture": (dict(position=(2.78, 2.33, 1.45), target=(0.95, 0.40, 1.05), fov_v=60.0), INT, ("sol_ext",),
                        "Coin lecture : vitrine en arche, claustra Adinkra, rayonnages, table ronde"),
}

if __name__ == "__main__":
    os.makedirs(VUES, exist_ok=True)
    sc = charger()
    h = hashlib.sha256(open(V5_IFC, "rb").read()).hexdigest()
    for name, (cam, light, hide, desc) in VIEWS.items():
        t = time.time()
        T, C, I = triangles(sc, lambda e: role(e) not in hide)
        shaded, trait = render(T, C, I, cam, size=SIZE, **light)
        shaded.save(os.path.join(VUES, f"{name}_ombre.png"), optimize=True)
        trait.save(os.path.join(VUES, f"{name}_traits.png"), optimize=True)
        info = {"vue": name, "description": desc, "source_ifc": "v5/DECIMO_ESQ_V5.ifc", "source_sha256": h,
                "repere": "monde IFC, mètres, z vers le haut, origine angle intérieur sud-ouest du RDC (sol fini = 0)",
                "camera": camera_info(cam, SIZE), "eclairage": {k: v for k, v in light.items()},
                "masques": list(hide), "script": "python3 v5/scripts/vues_rendu.py"}
        json.dump(info, open(os.path.join(VUES, f"{name}_camera.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"{name} {time.time() - t:.1f} s")
