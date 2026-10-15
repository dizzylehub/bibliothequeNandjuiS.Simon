# Rapport de variante IFC V6 → V7

## Source et reproductibilité

- Source : `v6/DECIMO_ESQ_V6_OPTION_C.ifc`
- Modèle livré : `v7/DECIMO_PROPOSITION_V7.ifc`
- SHA-256 V7 : `826ccd2a023f6a248f1e46bb5b5f80a629be5c8a58212b45fd6914e6930a2391`
- Génération : `python v7/scripts/generer_ifc_v7.py`
- Rendus exacts IFC : `python v7/scripts/render_maquette.py --size 2200 1467`

Le script ne modifie pas V5 ni V6. Le groupe IFC « Projet V7 — aménagement rectiligne sur enveloppe V5 à relever » rassemble 25 produits V7. Les espaces IFC existants (8 `IfcSpace`) sont conservés.

## Différentiel

La comparaison par `GlobalId` donne 230 produits V6, 188 produits communs, 42 produits retirés et 25 produits ajoutés, soit 213 produits dans V7. Les suppressions principales sont les niches et cadres cintrés de projet, le portail décoratif, l’ancien mur de façade et ses percements cintrés, l’ancien mobilier qui gênait les cheminements, les niches nord, la console vinyles, l’arbre/podium et les deux anneaux lumineux. Les murs latéraux et les espaces ne sont pas redessinés.

Les nouveaux produits V7 comprennent : une façade rectiligne segmentée autour d’ouvertures rectangulaires, les grilles et vitrages de façade, une cloison vitrée et sa porte entre les salles 03 et 01, son bandeau acoustique jusqu’à z=3,30 m, le comptoir unique et son siège, la table coworking avec quatre chaises, deux sièges individuels, un rayonnage droit ouest de 1,50 m et trois intentions lumineuses.

## Implantations principales

- Comptoir accueil-café : x=1,35–2,00 m, y=0,20–1,70 m, plan de travail z=0,84 m. Un siège est placé à l’ouest, dos au mur et face au comptoir. Le dégagement nord indiqué est de 0,76 m et le passage public est de 0,91 m à l’est. Ces dimensions restent à vérifier sur site, avec les équipements et le fonctionnement réel du poste.
- Rayonnage droit ouest du fond : x=3,10–3,42 m, y=5,40–6,90 m, z=0–2,20 m, 6 tablettes, soit 1,50 m linéaire de rangement proposé. Il remplace une partie des niches courbes V5 sans occuper l’allée principale.
- Cloison vitrée salle 03/lecture 01 : implantée sur la ligne x≈3,00 m, avec porte vitrée et bandeau acoustique continu de z=2,60 à 3,30 m. Les espaces et leurs limites IFC ne sont pas déplacés. Fixations, acoustique, sécurité incendie, débattement de porte et raccord au faux plafond restent à coordonner.
- Façade : l’emprise de référence générale x=0,09–6,51 m, y=−0,09–0,105 m, z=0–3,30 m est conservée par une nouvelle représentation segmentée. Les ouvertures rectangulaires sont un parti de projet à relever ; elles ne constituent pas un relevé de l’existant. Le modèle ne modifie pas les murs latéraux.
- Le stockage haut et le dallage d’extension de terrasse restent dans l’IFC comme options héritées de V6, non validées. Ils sont masqués dans les rendus de présentation.

## Contrôles et limites

- IFC4 : validation EXPRESS = 0 erreur, 0 avertissement.
- Contre-vérification géométrique indépendante avec `v5/scripts/valider_ifc.py` : 207 produits porteurs de représentation contrôlés, 207 géométries réussies, aucun échec. Le contrôle choisit explicitement la représentation Body plutôt que l’axe d’un mur. Le premier contrôle qui utilisait la sélection implicite de représentation signalait huit faux échecs; il est remplacé par ce bilan. Voir `validation_ifc_v7.txt`.
- Rendus : cinq images de 2200 × 1467 px, calculées depuis le SHA V7 indiqué ci-dessus. Les fichiers `*_camera.json` enregistrent caméra, SHA source, produits filtrés et triangles affichés.
- Dans l’axonométrie, la coupe de présentation est z≤2,40 m; les pans de façade sud V7 et de mur est sont abaissés graphiquement à +1,00 m. Les sols de contexte, réservations techniques, faux plafonds, plateforme haute et dallage optionnel sont masqués selon les vues. Les masques ne modifient pas l’IFC.
- La façade proposée remplace la géométrie de projet cintrée, en conservant son emprise globale comme repère. L’existence, la structure et les cotes doivent être relevées avant toute étude d’exécution. Les gabarits de circulation sont des objectifs de plan, pas une attestation réglementaire ou PMR.
