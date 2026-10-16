# V8 — café-bibliothèque de Madame Nandjui

Stade : esquisse, maquette IFC et plans techniques de principe (indice B). Direction A retenue : cocon mid-century et terrasse-salon sous pergola.

**Dossier de présentation à Madame Nandjui** : `dossier/NANDJUI_V8_Dossier_A3.pdf` (50 pages A3 paysage, indice C : rendus réalistes, plan et coupes rendus, toutes les variantes de mobilier et toutes les options, sans nom ni logo d’agence) et sa version modifiable `dossier/NANDJUI_V8_Dossier_A3.pptx`. Typographie : Cormorant Garamond (titres) et Jost (texte), polices libres fournies dans `dossier/polices/` ; le PDF les embarque, le PPTX demande de les installer.

- [Plan de travail V8](PLAN_DE_TRAVAIL_V8.html) : page HTML autonome. Elle contient l'analyse du site, la lecture du croquis de relevé, le brief « cocon mid-century », les deux directions de Dizzy avec leurs croquis, le plan de travail coordonné par G-K, les questions à trancher et la relecture de Josiane.
- `plans/E01_plan_amenagement` (SVG, PNG) : plan d'aménagement, esquisse de Désiré Akai.
- `NANDJUI_ESQ_V8.ifc` : maquette IFC4 de Manadja (contrôle dans `rapports/validation_ifc_v8.txt`).
- `rendus/` : rendus réalistes Blender Cycles depuis la maquette (R_P1 à R_P6, soir et jour), rendus studio de chaque variante de mobilier et échantillons de matériaux (`rendus/mobilier/`), images d’ambiance générées par IA et signalées comme non contractuelles (`rendus/ia/`).
- `vues/` : axonométries V01 et V02, perspectives P1 à P3 et modèle `NANDJUI_V8.glb`, calculés depuis l'IFC.
- `plans/T01` à `T03` : électricité et éclairage, plomberie, climatisation et ventilation (Le Génie).
- `mobilier/` : fiches mobilier de Désiré Akai (M01 à M08), planches de trois variantes V1 à V4 (bibliothèque, accueil, table de réunion, postes de travail) et répertoire de références `REFERENCES.csv`.
- `NOTE_TECHNIQUE_V8.md` : structure, pergola, réseaux, réglementation à confirmer.
- `croquis/` : quatre croquis de Dizzy (SVG et PNG).
  - A1 : cocon mid-century vu depuis le seuil.
  - A2 : la terrasse-salon sous pergola.
  - B1 : coupe du ruban.
  - B2 : façade-lanterne.
- `scripts/` : `croquis_dizzy.py` et `plan_esquisse.py` génèrent les SVG ; `rendre_croquis.sh` et `rendre_plans.sh` en font les aperçus PNG. La police Caveat est sous licence OFL.
- Croquis de relevé : `../photos/releve/` (PDF d'origine et image tournée façade en bas).

Brief du 15 octobre :
- un cocon d'esprit mid-century, cosy et classe, avec une lumière tamisée le soir ;
- tous les travaux sont refaits et la peinture bleue disparaît ;
- le mur de la salle de réunion est démoli et remplacé par une baie vitrée, sous réserve d'un avis structure et de l'accord de la copropriété.

Cotes : largeur intérieure retenue 6,75 m (3,00 + 0,15 estimé + 3,60). Les 5,50 m mesurés dehors restent à rattacher. La profondeur est estimée à 7,60 m (fourchette 7,20 à 8,00 m), à mesurer.

Les croquis sont des dessins de principe générés par script, sans valeur de plan. Les membres de l'équipe sont des rôles de travail d'une IA ; ils ne délivrent aucun visa professionnel.

Régénérer, depuis la racine du dépôt (`pip install -r v8/requirements.txt`) :

```bash
v8/scripts/rendre_plans.sh          # E01 et T01 à T03
v8/scripts/rendre_croquis.sh        # croquis de Dizzy
v8/scripts/rendre_mobilier.sh       # fiches mobilier
python3 v8/scripts/generer_ifc_v8.py
python3 v8/scripts/valider_ifc_v8.py
python3 v8/scripts/vues_ifc_v8.py   # vues 3D et GLB
# rendus réalistes : bpy (Blender 5.x) dans un environnement Python 3.13, puis
BPY_PYTHON=<python avec bpy> v8/scripts/rendre_blender.sh
python3 v8/scripts/preparer_images_dossier.py
# dossier : pptxgenjs à installer (npm install pptxgenjs), puis
NODE_PATH=<dossier>/node_modules node v8/scripts/dossier_v8.js
# puis apply_theme.js (compétence pptx) avec v8/scripts/theme_dossier.json, et conversion PDF
```
