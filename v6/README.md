# Option C — dossier d’esquisse V6 et calque provisoire sur l’IFC V5

## Dossier de présentation

La planche de synthèse en cinq pages est disponible en [PDF A3 paysage](DOSSIER_ESQUISSE_OPTION_C_V6.pdf). Elle présente le site photographié, la référence IFC V5, un plan d’aménagement de principe, une coupe schématique, l’ambiance et les vérifications à mener. Les aperçus PNG sont dans `apercus/`.

Le plan conserve l’enveloppe générale de l’IFC V5 à titre de référence; ses cloisons intérieures, son mobilier et ses zones de programme sont schématiques. L’emplacement de la salle vitrée dans la pièce bleue est une hypothèse à recaler sur un relevé coté. La vue d’ambiance `A06_vue_ambiance_piece_bleue_concept.png` est une image conceptuelle, pas un relevé ni un rendu exact de l’existant.

Le dossier a été relu avec cinq rôles d’analyse IA : conception d’espace, direction artistique, BIM/IFC, ingénierie technique et mise en page du dossier. Ces rôles ont vérifié la cohérence du programme et les incertitudes visibles dans les photos; ils ne constituent pas des visas d’architecte, d’ingénieur ni une validation structurelle.

### Statut et suite

La V6 est prête pour discussion de principe, mais pas pour travaux. La prochaine étape de conception est un relevé sur place qui relie explicitement la pièce bleue aux espaces V5 et mesure les hauteurs, les ouvertures, la mezzanine/volume haut, les WC et la terrasse extérieure. À partir de ce relevé, il sera possible de figer le plan, puis de mettre à jour la géométrie IFC et les coupes.

Le PDF est régénéré par `scripts/generer_dossier_provisoire.py`.

---

## Calque IFC Option C

`DECIMO_ESQ_V6_OPTION_C_PROVISOIRE.ifc` est une copie de travail de `v5/DECIMO_ESQ_V5.ifc`. Elle ajoute un groupe IFC **Option C** et des propriétés `KDEMI_Option_C_Provisoire` aux espaces concernés. Ces propriétés consignent le programme demandé et ce qu'il reste à relever.

Les 45 photos de l'état des lieux sont maintenant disponibles sous `photos/` et ont fait l'objet d'un premier repérage visuel. Elles confirment notamment une pièce bleue allongée, une porte au fond et un volume haut derrière une séparation. Elles ne donnent pas de cotes fiables ni de preuve structurelle; voir `rapport_reperage_photos.md`.

La planche illustrée A05 est disponible en [PDF](A05_reperage_photos.pdf) et en [PNG](A05_reperage_photos.png).

La géométrie V5 n'a pas été retouchée : les 231 produits et leurs GlobalId sont conservés; les 225 représentations géométriques ont les mêmes sommets en coordonnées monde que la source. Cette première adaptation est donc un calque de programme dans l'IFC, pas une maquette d'exécution ni un déplacement de cloisons. Le repérage photo améliore les hypothèses, mais ne permet pas encore d'identifier sans ambiguïté les espaces V5 correspondants.

| Référence V5 | Intention de l'Option C consignée dans l'IFC | À confirmer |
|---|---|---|
| 01 — Salle de lecture, 24,07 m² | Bibliothèque avec davantage de rayonnages au nord-est et coworking léger | Implantation et dégagements autour de l'accueil-café |
| 03 — Salle de réunion, 7,21 m² | Salle vitrée dans la pièce désignée en bleu par la maîtrise d'ouvrage | La pièce bleue du site ne correspond pas encore à une zone IFC repérée; aucune cloison déplacée |
| 07 — WC, 2,87 m² | WC arrière à réaménager; étudier la mezzanine signalée comme réserve | Position réelle, appareils et évacuations; la mezzanine n'existe pas dans la V5 |
| 08 — Terrasse couverte, 15,74 m² | Conserver la partie couverte et étudier le prolongement jusqu'au dallage au-delà du garde-corps | Limites, niveaux, garde-corps et capacité du dallage |

Les cotes de la V5 restent des cotes de maquette d'esquisse. Le relevé photo et les hauteurs réelles sont requis avant de créer les nouveaux volumes, déplacer la salle vitrée ou redessiner les sanitaires et les réseaux. Le script reproductible est `scripts/creer_option_c_ifc.py`; il lit la V5 et écrit uniquement dans `v6/`.

Validation effectuée avec IfcOpenShell 0.9.0 : IFC4, aucune erreur ni aucun avertissement EXPRESS, 225/225 produits géométriques valides. Comparaison indépendante : 231/231 produits conservés et 225/225 représentations inchangées.
