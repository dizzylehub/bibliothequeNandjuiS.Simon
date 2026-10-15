# Dossier de concours V7 — Bibliothèque Nandjui D. Simon

Le dossier raconte une bibliothèque de quartier à travers cinq usages : arriver, être accueilli, se réunir, lire et travailler, puis prolonger la journée sous l’arbre. Il présente un projet de conception assisté par des collaborateurs IA mobilisés par rôles. Il ne revendique ni auteur humain fictif ni visa professionnel.

## Livrables

- `DOSSIER_CONCOURS_V7.pdf` : présentation de 22 pages au format A3 paysage.
- `DOSSIER_CONCOURS_V7_EDITABLE.pptx` : version de présentation modifiable; textes, formes et images sont des objets séparés.
- `apercus_concours/index.html` : galerie responsive des planches; les aperçus PNG sont dans le même dossier.
- `DECIMO_PROPOSITION_V7.ifc` : maquette de conception coordonnée avec les planches.
- `validation_ifc_v7.txt` : contrôle IFC4, géométrie de 207 produits représentés; zéro erreur et zéro avertissement dans ce contrôle.
- `VISITE_MAQUETTE_V7.html` et `MAQUETTE_V7_VISITE.glb` : consultation 3D complémentaire de la maquette.
- `scripts/generer_dossier_concours.py` : source du PDF, du PPTX et de la galerie.

## Régénérer

Depuis la racine du dépôt, avec Python, Pillow, ReportLab, PyMuPDF et python-pptx installés :

```bash
python v7/scripts/generer_dossier_concours.py
```

Le générateur n’intègre les dessins que si `assets/dessins/dimensions_surfaces.json` indique le SHA-256 de l’IFC courant. Il n’intègre les rendus IFC que si les fichiers `*_camera.json` indiquent le même hash et correspondent à leurs PNG. Les images issues d’une autre version restent exclues même si leur date est récente.

## Statut et lecture des images

- Les photographies du dossier documentent l’état observé; elles ne constituent pas un relevé coté.
- `assets/matieres.png` est une planche tactile générée par IA, une intention de palette. Les matières et leur disponibilité doivent être confirmées localement.
- Les images sous `assets/ambiance/` sont des ambiances générées par IA et non contractuelles. Leur statut est précisé dans leurs légendes.
- `provenance_ambiances.json` relie chaque image d’intention à sa photographie ou vue IFC de référence et énonce ses limites.
- Les vues sous `assets/ifc/` sont des rendus de la maquette IFC; elles documentent sa géométrie, pas la réalité construite.
- Les dessins sous `assets/dessins/` sont extraits de la maquette; les cotes, surfaces et niveaux restent à rapprocher du relevé du site.
- Les points à confirmer (réseaux, structure, WC, limites et terrasse, détails de fabrication) sont regroupés dans `faisabilite.md` et vers la fin du dossier.

## Traçabilité

Le générateur vérifie le SHA-256 du modèle avant d’utiliser les rendus et dessins. Les détails de source sont conservés dans `assets/ifc/*_camera.json` et `assets/dessins/dimensions_surfaces.json`. Les références et hypothèses du projet sont détaillées dans `BRIEF_MAITRISE_OUVRAGE.md`, `conception.md` et `faisabilite.md`.
