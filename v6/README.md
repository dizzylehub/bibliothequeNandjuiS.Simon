# Bibliothèque Nandjui — Option C, V6

## Fichiers de livraison

- [Pack complet à télécharger (ZIP)](PACK_LIVRAISON_OPTION_C_V6.zip)
- [Dossier de présentation et de conception, PDF A3 (10 planches)](DOSSIER_PROJET_OPTION_C_V6.pdf)
- [Maquette IFC4 éditable](DECIMO_ESQ_V6_OPTION_C.ifc)
- [Aperçu du plan d’aménagement (PNG)](apercus_projet_v6/page_02.png)
- [Aperçus PNG des planches](apercus_projet_v6/)
- [Repérage photographique](A05_reperage_photos.pdf) et [version PNG](A05_reperage_photos.png)
- [Avis technique préliminaire](avis_technique_preliminaire.md)
- [Note de direction artistique et revue du dossier](NOTE_DIRECTION_ARTISTIQUE_ET_REVUE_PLANCHES_V6.md)
- [Différentiel IFC V5 → V6](rapport_diff_ifc_v5_v6.md)
- [Rapport de validation IFC](validation_ifc_v6.txt)
- [Repérage des photos d’état des lieux](rapport_reperage_photos.md)
- [Image d’ambiance conceptuelle de la pièce bleue](A06_vue_ambiance_piece_bleue_concept.png)

Le dossier présente le plan d’aménagement, le plan de plafond et d’éclairage repris de la maquette, deux coupes, l’élévation d’entrée, des élévations intérieures, une axonométrie, des vues axonométriques de mobilier et une planche de matières et notes. Les vues de maquette sont générées depuis l’IFC V6. L’image d’ambiance conceptuelle est séparée et ne sert pas de document de mesure.

## Proposition retenue

L’Option C reprend la disposition validée : accueil-café près de l’entrée avec un seul poste de service, salle de réunion vitrée côté gauche dans la pièce désignée en bleu, bibliothèque et rayonnages droits au nord et à l’est, petit coworking et terrasse couverte. L’arbre à livres central est retiré. Un écran de confidentialité WC, un volume haut de réserve et la prolongation de terrasse figurent comme options à vérifier.

L’IFC V6 part de `v5/DECIMO_ESQ_V5.ifc`, que le script ne modifie pas. Il conserve l’enveloppe et les éléments fixes du modèle de référence et ajoute/remplace du mobilier et des éléments explicitement identifiés comme hypothèses. Les espaces IFC reprennent encore les emprises V5 : les surfaces affichées décrivent donc la maquette de référence et ne constituent pas un relevé de l’existant. La correspondance de la pièce bleue avec l’espace IFC 03 reste à relever sur place.

## Statut et vérifications à faire

La maquette IFC4 a été validée avec IfcOpenShell : aucune erreur ni aucun avertissement EXPRESS, et 224 géométries sur 224 contrôlées. Ce contrôle vérifie la structure et la géométrie IFC, pas la conformité réglementaire, les collisions détaillées ni la constructibilité.

Le dossier constitue une proposition de conception coordonnée au stade esquisse développée. Il ne peut pas servir directement à construire. Les dimensions du site et les hauteurs réelles ne sont pas établies par les photos. Avant les plans d’exécution, relever sur place l’enveloppe, les niveaux, les portes, les baies, la pièce bleue, les WC et leurs évacuations, le volume haut, ainsi que les limites et pentes de la terrasse extérieure. Faire vérifier par les professionnels compétents la structure et les charges du rangement haut, les dégagements et l’écran WC, l’accessibilité, l’éclairage, la ventilation, les réseaux et les règles locales. Les 27 luminaires et réseaux présents dans la V5 sont conservés comme référence, sans recalage ni complément propre à la V6. Les vues A08 illustrent les objets IFC, sans détails d’assemblage ni fixations.

Le retour WC laisse 1,00 m de passage dans la géométrie IFC contre environ 1,03 m dans le modèle V5; débattement de porte et largeur finie restent à contrôler. Le comptoir et l’assise sont des gabarits de mobilier, à ajuster après relevé et test ergonomique. La plateforme haute, l’extension de terrasse et les finitions sont des hypothèses et non des ouvrages validés.

## Régénération

Depuis la racine du dépôt :

```bash
python3 v6/scripts/generer_ifc_v6.py
python3 v5/scripts/valider_ifc.py v6/DECIMO_ESQ_V6_OPTION_C.ifc
python3 v6/scripts/generer_dossier_projet_v6.py
```

Les rôles de conception d’espace, direction artistique, BIM/IFC, ingénierie technique et mise en page ont été utilisés comme relectures par IA. Ce ne sont pas des visas professionnels ni des validations de chantier.
