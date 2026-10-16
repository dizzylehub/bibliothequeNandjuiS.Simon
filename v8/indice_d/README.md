# V8 — indice D : le salon des possibles

Refonte demandée : images plus incarnées, mobilier moins générique, axonométries et coupes renouvelées, esquisses de type dessin d'architecte et personnages naturels.

## Livraison

- `dossier/NANDJUI_V8_D.pdf` : nouvelle présentation A3 paysage.
- `dossier/NANDJUI_V8_D.pptx` : version modifiable (texte, composition et images séparés).
- `images/` : perspectives d'intention, esquisses et vues calculées.
- `mobilier/` : cinq rendus studio et cinq sources Blender modifiables.
- `dessins/` : six planches vectorielles SVG et aperçus PNG.
- `SCENE_V8_D.blend` : scène de présentation avec le nouveau mobilier implanté.
- `scene_d.npz` : géométrie évaluée de la scène D pour les développements ultérieurs.

## Direction

Noyer au grain discret, lin écru, olive, cognac, terrazzo clair et bronze brossé. Accoudoirs galbés, pieds fuselés, dossiers inclinés, plateaux capsule et chants adoucis. Les détails de sellerie, la réparabilité, l'éclairage localisé et la continuité intérieur/terrasse structurent la proposition.

Les coupes d'expression remplacent les silhouettes schématiques par des personnages à l'anatomie naturelle, vêtus, assis ou debout dans des postures liées au lieu. Les esquisses sont des images de synthèse au style main levée, pas des dessins exécutés à la main.

## Statut et cohérence

Les neuf images d'intention et d'expression sont générées avec un outil d'images à partir de références V8 et de la nouvelle direction. Elles ne sont pas métriques. Leurs accessoires, canapé, luminaires et formes fines de mobilier peuvent différer des modèles Blender de conception. Cette différence est signalée dans la présentation.

Les axonométries, le plan et les coupes calculées utilisent l'enveloppe V8 et les nouveaux meubles implantés. Le comptoir Rivage est une variante autonome à implanter ; il ne remplace pas encore le comptoir existant dans la scène. L'IFC historique reste l'état V8 C ; les sources D sont dans Blender, sans certification de fabrication ou d'interopérabilité Revit. Les hauteurs et la profondeur du local restent des hypothèses de relevé.

Les planches mobilier sont des détails de conception : dimensions proposées, assemblages schématiques à dimensionner, essais de stabilité et confort nécessaires avant fabrication. Les illustrations de section IA ne servent pas à prendre des cotes.

## Régénérer

Depuis la racine du dépôt, avec l'environnement préparé :

```bash
source /workspace/.onboarding/nandjui/activate.sh
python v8/indice_d/scripts/design.py --mode studio --view FAUTEUIL --res 1400 --samples 32
# Autres pièces : TABLE, CHAISE, ACCUEIL, TERRASSE
python v8/indice_d/scripts/design.py --mode axo --view 01 --res 1800 --samples 32
python v8/indice_d/scripts/design.py --mode axo --view 02 --res 1800 --samples 32
python v8/indice_d/scripts/design.py --mode section --view COUPE_AA --samples 24
python v8/indice_d/scripts/design.py --mode section --view COUPE_BB --samples 24
python v8/indice_d/scripts/design.py --mode plan --view PLAN --samples 24
python v8/indice_d/scripts/design.py --mode interior --view P1 --res 1600 --samples 32
python v8/indice_d/scripts/details.py
python v8/indice_d/scripts/render_svg.py "$PWD" v8/indice_d/dessins
node v8/indice_d/scripts/presentation.js
soffice -env:UserInstallation=file:///workspace/.onboarding/nandjui/lo-profile --headless --convert-to pdf --outdir v8/indice_d/dossier v8/indice_d/dossier/NANDJUI_V8_D.pptx
```

Dépendances : Python 3.13, bpy 5.2.2, NumPy, bibliothèques V8, Chromium/Playwright pour les SVG, pptxgenjs 4.0.1 et LibreOffice. Les images IA sont conservées comme assets ; elles ne sont pas recréées par ces scripts. Les polices Jost et Cormorant Garamond sont fournies dans `../dossier/polices`.


## Archive livrée

L’archive locale `../NANDJUI_V8_D_livraison.zip` contient cette édition et les dépendances de source V8 nécessaires au calcul (`scripts/rendu_blender.py`, `rendus/scene_v8.npz`, polices). Les chemins relatifs du dépôt sont conservés. Le dossier ne contient pas de secrets ni de dépendances installées. Les versions Python et Node nécessaires sont déclarées dans `requirements.txt` et `package.json`.

Cette archive dépasse la limite GitHub de 100 Mo par fichier et n’est donc pas versionnée. Sur GitHub, utilisez **Code → Download ZIP** pour télécharger le dépôt avec tous les documents de cette édition, ou ouvrez les fichiers du dossier `dossier/` pour télécharger le PDF et le PowerPoint séparément.
