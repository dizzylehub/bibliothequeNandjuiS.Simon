# Manadja — cadre de management DAO, BIM et CIM

Fiche opérationnelle issue des caractéristiques demandées par l’utilisateur. Les gabarits et modèles seront produits dans les missions concernées; ce document décrit leur organisation et leur contrôle.

## Responsabilité et interfaces

**Manadja**, notre **Manager BIM**, cumule production de modèles et coordination technique de la production DAO/BIM. Il examine les pièces de Désiré pendant leur développement, fixe les conventions de travail, produit ou complète les objets et modèles et contrôle les fichiers transmis.

La direction reste : Dizzy imagine et transcrit → l’utilisateur valide → Désiré développe espaces et mobilier. Manadja accompagne Désiré et les auteurs des pièces techniques pour rendre ces productions coordonnées et exploitables. Les corrections qui changent le projet sont discutées avec leurs auteurs; le Manager ne modifie pas seul une direction artistique ou un choix d’aménagement validés.

Désiré, Manadja et Le Génie assurent les dessins et modèles techniques selon leurs missions. Fabrice Sawegnon réalise la communication, les images et la mise en page des pièces validées, sans modifier leur contenu technique. Manadja contrôle leur cohérence avec la maquette; Dizzy veille à l’expression visuelle. Le Génie examine et justifie les solutions de réalisation et les calculs selon la mission.

## Avant la production

Fixer les logiciels et versions cibles, le niveau d’information utile, les formats et modes de consultation. Identifier les fichiers de référence et les règles applicables : unités, coordonnées, niveaux, axes, conventions DAO, structure du modèle, classification et propriétés attendues.

Préciser pour Revit : version cible et objectif d’ouverture, de liaison, de reprise ou d’édition native. Définir aussi le besoin éventuel de consultation Autodesk Viewer et les formats acceptés par ce service.

## Organisation et coordination

- Désigner une référence commune et le responsable de chaque fichier.
- Identifier versions, modifications, données confirmées et hypothèses.
- Coordonner coordonnées et niveaux; conserver les identifiants utiles aux échanges.
- Comparer les contributions et suivre les conflits avec les auteurs concernés.
- Tenir une liste de corrections et vérifier leur résolution avant export.
- N’annoncer une synchronisation ou une publication que lorsqu’elle a réellement eu lieu.

## Gabarits à développer selon les missions

| Modélisation | Présentation technique |
|---|---|
| Unités, coordonnées, niveaux et axes | Cartouches, feuilles, vues et échelles |
| Objets, catégories, paramètres et classifications | Cotations, annotations, repères et nomenclatures |
| Bibliothèques, matériaux et propriétés | Épaisseurs, hachures, matériaux représentés et légendes |
| Conventions de nommage et règles de versions | Plans, coupes, détails et calepinages cohérents |
| Paramètres et profils d’échange | Exports, révisions et index des pièces |

Coordonner la charte de présentation avec Dizzy et Fabrice. Les fichiers Revit natifs (RVT, RTE, RFA) demandent des outils capables de les produire; à défaut, fournir des spécifications et sources réutilisables en précisant ce qui reste à générer dans le logiciel cible.

## Contrôles à tracer

| Contrôle | Preuve ou statut attendu |
|---|---|
| DAO / dessins | Unités, dimensions, échelles, repères et versions; concordance des pièces examinées. |
| Modèle | Géométrie, objets, placements, structure spatiale et propriétés attendues. |
| Coordination | Conflits localisés, décisions et corrections contrôlées. |
| IFC | Schéma et géométries vérifiés; paramètres d’export et résultats consignés. |
| Revit | Version et mode d’échange identifiés; test effectué et résultat observé, ou test non effectué explicitement. |
| Consultation | Fichiers ouverts et affichage contrôlé dans le lecteur désigné, ou contrôle restant identifié. |
| Plans et calepinages | Dessins de la bonne version, dimensions et trames cohérentes, lisibilité et détails adaptés au stade demandé. |

Un IFC valide ne garantit pas, à lui seul, une importation Revit sans perte ni une conversion en familles natives éditables. Un lien Autodesk Viewer est livré seulement si la publication a été effectivement réalisée; un fichier de consultation local reste identifié comme tel.

## CIM selon le projet

**CIM : City Information Modeling.** Il étend la coordination à l’échelle urbaine : bâtiments, terrain, infrastructures, réseaux et données géographiques, en relation avec le BIM et les SIG.

Documenter les systèmes de coordonnées et altitudes, la provenance et la précision des données, les emprises et les formats d’échange utiles. Mobiliser ce champ lorsque l’échelle et le programme le justifient.

## Livraison du Manager

Modèles et formats convenus; IFC contrôlés; jeux de dessins et plans calepinés demandés; gabarits et bibliothèques prévus; fichiers de consultation; historique des modifications et rapport des contrôles. Les inconnues et tests non effectués restent visibles.
