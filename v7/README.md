# Bibliothèque Nandjui D. Simon — une bibliothèque habitée

Lire et travailler le jour, se retrouver autour d’un café, prolonger la rencontre sur la terrasse : la proposition V7 organise le lieu autour de ces usages. Elle développe la disposition demandée à partir de la maquette V5 et des photographies du local.

## Regarder le projet sans logiciel de dessin

- **[Voir les 22 planches directement sur GitHub](VOIR_LE_DOSSIER.md)** : les images s’affichent dans la page, y compris sur téléphone.
- [Dossier de présentation PDF A3](DOSSIER_CONCOURS_V7.pdf).
- [Présentation PowerPoint modifiable](DOSSIER_CONCOURS_V7_EDITABLE.pptx) : textes et images sont des éléments distincts; polices Archivo disponibles dans `../charte/polices/`.
- [Galerie HTML](apercus_concours/index.html) à ouvrir dans un navigateur après téléchargement du dossier.
- [Visite 3D dans un navigateur](VISITE_MAQUETTE_V7.html), après téléchargement : géométrie intégrée au fichier, Internet nécessaire pour charger le lecteur. La galerie de planches est consultable sans ce lecteur.
- [Maquette GLB de consultation](MAQUETTE_V7_VISITE.glb).

## Fichiers du projet

- [IFC4 V7](DECIMO_PROPOSITION_V7.ifc) : objets de projet séparés; les versions V5 et V6 restent conservées dans leurs dossiers.
- [Pack complet ZIP](PACK_PROJET_V7.zip).
- [Brief de la maîtrise d’ouvrage](BRIEF_MAITRISE_OUVRAGE.md), [parti architectural](conception.md) et [faisabilité](faisabilite.md).
- [Différentiel V6 → V7](rapport_diff_v6_v7.md), [validation IFC indépendante](validation_ifc_v7.txt) et [provenance des ambiances](provenance_ambiances.json).

Le poste accueil-café est placé près du seuil, avec une assise dos au mur et un accès de travail au nord du comptoir. La salle vitrée reste à gauche; trois ensembles de rayonnages droits au nord, à l’est et au fond ouest libèrent le centre. La proposition comporte une table partagée à quatre places et deux postes individuels. La réunion vise six personnes dans une implantation compacte à vérifier. Le WC arrière, la réserve haute et le prolongement vers le dallage extérieur font l’objet de vérifications spécifiques.

## Lecture des dessins et images

Les plans, coupes et rendus de maquette sont calculés depuis le même IFC V7. Le plan de coupe à +1 m, les vues en écorché et les options masquées sont documentés dans les scripts et fichiers caméra. La visite GLB reprend l’axonométrie d’affichage; l’IFC contient le projet complet et ses options.

Les ambiances IA illustrent les matières, la lumière et les usages à partir des perspectives de la maquette. Le photomontage de seuil s’appuie sur une photographie du site et propose des finitions. Ces images sont légendées et restent distinctes des dessins de mesure. Les livres, personnes, végétaux et petits objets d’ambiance ne constituent pas un quantitatif de fourniture.

Les cotes et surfaces proviennent de la maquette de référence et ne remplacent pas un relevé. Avant les plans d’exécution : mesurer le local et les hauteurs, recaler les ouvertures et poteaux, coordonner les réseaux du café et les sanitaires, vérifier les dégagements, l’acoustique, la ventilation, la réserve haute et les limites de terrasse. La V7 constitue un dossier de conception et de présentation au niveau concours, pas un visa de chantier.

## Contrôle et sources

IFC4 : aucune erreur ni aucun avertissement EXPRESS; 207 représentations géométriques contrôlées, 207 réussies. Les empreintes SHA des vues et dessins permettent de vérifier qu’ils correspondent à l’IFC livré.

Sources : IFC et dossier V5 de référence; adaptation V6; photographies originales sous `../photos/`; croquis et références transmis par la maîtrise d’ouvrage. Cinq rôles de travail IA ont été utilisés : conception d’espace, direction artistique, dessin architectural, BIM et faisabilité technique. Ils ne constituent pas des intervenants humains ni des visas professionnels.

Les scripts sous `scripts/` permettent de reproduire le modèle, les dessins, les rendus, le dossier et la visite. Dépendances : `python3 -m pip install -r v7/requirements.txt`. Les rendus demandent un contexte OpenGL (EGL/Mesa dans cet environnement). Depuis la racine du dépôt :

```bash
python3 v7/scripts/generer_ifc_v7.py
python3 v7/scripts/render_maquette.py --size 2200 1467
python3 v7/scripts/dessins_architecture.py
python3 v7/scripts/generer_dossier_concours.py
python3 v7/scripts/exporter_visite_3d.py
python3 v7/scripts/preparer_livraison.py
```

Une régénération IFC peut modifier les métadonnées et donc son SHA; régénérer aussi les dessins et vues avant de reconstruire le dossier.
