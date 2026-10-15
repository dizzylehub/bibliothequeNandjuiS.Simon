# Revue IFC V5 (cohérence, import Revit, modifiabilité) et suggestions

Revue du 2026-10-15 sur `DECIMO_ESQ_V5.ifc` et `DECIMO_ESQ_V5_maille_Revit.ifc` (ifcopenshell 0.9.0).

## 1. Cohérence : ce qui est sain

- IFC4, 0 erreur de validation (schéma + EXPRESS), 225/225 géométries, aucun GlobalId dupliqué.
- Tous les produits sont contenus dans un niveau ; les 10 ouvertures et 8 remplissages sont reliés ; 8 `IfcSpace` avec `Qto_SpaceBaseQuantities`.
- La V4 est conservée à l'identique (141/141 produits, voir `verif_v4_v5.md`).

## 2. Problèmes relevés

| # | Constat | Effet dans Revit | Traitement |
|---|---|---|---|
| 1 | Projet nommé « étude intérieure V4 » (LongName « V2 »), site « Default », bâtiment sans nom | Info projet et navigateur trompeurs | Corrigé dans `_Revit_editable` |
| 2 | 62 génériques V4 nommés par leur seul ElementId (« 4350632 ») | Sélection et filtrage impossibles | Renommés « Générique V4 - matériau - id » |
| 3 | 84 `IfcBuildingElementProxy` sur 225 produits, dont 62 sans classe métier | Tous en « Modèle générique », sans paramètres de catégorie | **Non corrigé** : reclassifier demande de modifier l'existant (voir §3) |
| 4 | 94 éléments sans `PredefinedType` (murs, portes, fenêtres, proxies) | Sous-catégorie non déduite | Renseignés |
| 5 | 60 éléments sans `IfcTypeObject` (couvrements, mobilier, équipements...) | Une famille par instance : changer une dimension oblige à tout reprendre | Un type par famille créé (58 types, souvent 1 élément) |
| 6 | 89 éléments sans matériau | Pas de matériau Revit, couleur par défaut | Matériau de repli « ESQ - … » (à affiner) |
| 7 | Porte à galandage du coin lecture sans `IfcRelFillsElement` | Importée sans mur hôte, ne suit pas le mur | **Non corrigé** (géométrie) : à héberger dans une ouverture |
| 8 | Cote du niveau RDC = -1,9e-12 | Niveau « presque zéro », bruit à l'affichage | Mise à 0 |
| 9 | Variante maillée : 0 ouverture, 0 remplissage, 207/215 produits en `IfcTriangulatedFaceSet` | Tout en DirectShape, rien de paramétrique | Voir §3 |
| 10 | Unité en centimètres, aucun `IfcMapConversion`, 3 niveaux (SS1, N01, N02) quasi vides | Revit ouvre en cm sans problème, mais pas de géoréférencement ; niveaux parasites | Non traité (voir suggestions) |

## 3. Fichiers et usage

- `DECIMO_ESQ_V5.ifc` : référence, inchangé.
- `DECIMO_ESQ_V5_Revit_editable.ifc` (**nouveau**) : V5 + corrections non géométriques ci-dessus. GlobalId, placements et représentations vérifiés identiques (assertion dans le script), 0 erreur de validation, 225/225 géométries. Géométrie en extrusions paramétriques conservées : c'est le meilleur point de départ pour Revit.
- `DECIMO_ESQ_V5_maille_Revit.ifc` : à réserver à la visualisation ; il n'est pas modifiable.
- Régénération : `python3 v5/scripts/preparer_revit_editable.py` (journal dans `preparation_revit_editable.txt`).

Limite à connaître : l'import IFC de Revit ne garantit pas de murs natifs. Pour obtenir des murs, portes et fenêtres réellement éditables, il faut les recréer dans Revit par-dessus l'IFC lié (calque de calage) ou passer par un outil d'import direct (Dynamo, Rhino.Inside, plug-in IFC-vers-natif). L'IFC seul ne suffit pas, et ce point n'a pas pu être testé ici (pas de Revit dans cet environnement).

## 4. Suggestions pour le projet

**Maquette**
1. Décider avec le BET si l'existant V4 peut être reclassifié (proxies vers `IfcColumn`, `IfcWall`, `IfcBeam`, `IfcRoof`, claustras en `IfcWall`/`IfcMember`). C'est la seule façon d'obtenir des catégories Revit utiles, et ce serait un jalon « V5.1 - existant requalifié » séparé de l'aménagement.
2. Poser un `IfcMapConversion` (EPSG:2165 Abidjan / UTM 30N) et un point de base partagé, avant toute coordination avec la copropriété ou le BET.
3. Supprimer ou documenter les niveaux SS1, N01, N02 : ils portent des éléments V4 (7 proxies) mais le lot n'a qu'un RDC.
4. Ajouter des classifications (Uniclass ou OmniClass, ou une nomenclature K&D) pour pouvoir filtrer et chiffrer sans passer par les noms.
5. Fournir des `Qto_*BaseQuantities` pour tous les éléments aménagés, pas seulement les espaces : cela alimentera directement l'estimatif.
6. Héberger la porte à galandage dans une ouverture et exposer ses paramètres (largeur, hauteur, sens) via `Pset_DoorCommon`.
7. Passer l'unité en mètres ou en millimètres à la prochaine reconstruction : les cm sont une héritière de la V4 et déroutent les outils tiers.

**Processus**
8. Garder une seule source de vérité : les scripts produisent déjà tous les livrables ; ajouter une CI (GitHub Actions) qui exécute `regenerer.sh` et `verif_v4_v5.py` pour qu'aucun commit ne casse la conformité V4/V5. Ne pas versionner les trois anciens IFC V2 à V4 à la racine : une release suffit, le dépôt fait 3,5 Mo d'IFC.
9. Tester l'import dans Revit réel (liaison + ouverture) et consigner les avertissements dans un rapport daté : c'est le seul contrôle manquant à cette chaîne.
10. Tenir un fichier de décisions pour les 12 points ouverts du README (responsable, échéance, état), car plusieurs bloquent la suite (claustras, imposte, copropriété, statut des refends).
11. Prévoir un export BCF ou un tableau d'incohérences pour les échanges avec le BET et la copropriété.

**Conception (points déjà ouverts, à arbitrer en premier)**
12. Les claustras devant la vitrine en arche (point 2), la dalle haute hypothétique (point 1) et les rails lumineux dans le plénum (point 4) sont les trois sujets qui changent le plus la maquette : à trancher avant l'APS.
13. Faire relever sur site les cotes qui sont aujourd'hui des hypothèses (dalle, tableau divisionnaire, coffrages EU/EV), puis recaler la maquette plutôt que de multiplier les variantes.
