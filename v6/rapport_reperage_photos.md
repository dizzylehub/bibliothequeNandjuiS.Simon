# Première lecture des photos — Option C

**Sources examinées :** `photos/LE SITE/` (18 images) et `photos/interieur/` (27 images), toutes en 1080 × 810 px. Plusieurs vues sont des doublons exacts ou des angles presque identiques. Les photos ont été parcourues en planches-contact et en grand format pour les pièces bleues et les seuils. Ce repérage est visuel; il ne remplace ni un relevé ni une visite technique.

## Ce que les images montrent

- **Dehors :** le local donne sur un espace extérieur clos par un muret et une grille métallique. On voit une bande de dallage au droit de l'entrée, puis des surfaces extérieures plus larges, en partie engazonnées ou en terre. Les prises de vue montrent aussi un arbre et des façades voisines. Il reste à confirmer quelle partie est dans l'emprise privative et laquelle est exploitable pour la terrasse.
- **Accès :** la façade présente une entrée vitrée protégée par des grilles ouvrantes, une fenêtre grillagée voisine et un seuil donnant sur une dalle extérieure. À reprendre dans le plan d'accès et les vues de façade.
- **Intérieur clair :** plusieurs vues montrent une pièce dégagée, une petite fenêtre haute en façade arrière et des portes dans les parois latérales. Le plafond est bas et continu à l'œil, avec des retombées/saillies visibles; aucune photo ne donne une hauteur mesurable.
- **Pièce bleue :** les vues montrent une pièce allongée, sol carrelé, murs bleus, un accès latéral et une porte au fond qui ouvre sur un compartiment plus sombre, avec deux petites marches. Cela concorde avec l'indication de la maîtrise d'ouvrage selon laquelle les WC se trouvent au fond de cette zone, mais la photographie seule ne permet pas d'identifier les appareils sanitaires.
- **Volume haut arrière :** au-dessus d'une séparation au fond de la pièce bleue, on distingue un plateau ou volume de rangement portant un carton. Cela rend plausible le rangement en hauteur signalé par la maîtrise d'ouvrage. Les photos ne montrent ni structure porteuse, ni accès, ni garde-corps, ni charge admissible : je le désigne ici comme **volume haut existant à vérifier**, pas comme mezzanine structurellement validée.
- **État à rénover :** finitions et éclairages apparents sont hétérogènes; certaines installations sont en applique. Les prises, commandes, tableaux et réseaux doivent être repérés avant de fixer le comptoir café, les cloisons ou le mobilier.

## Conséquences pour le plan et l'IFC

1. Le programme demandé est conservé : accueil-café près de l'entrée et tenu depuis un poste dos au mur; salle vitrée de réunion dans la zone bleue désignée; lecture, rayonnages abondants et coworking dans la surface restante; WC au fond de la zone bleue avec écran visuel depuis les espaces publics; terrasse étudiée sur le dallage extérieur.
2. Les vues photo ne suffisent pas à superposer les pièces à l'orientation et aux espaces `IfcSpace 01–08` de la V5. Une lecture pourrait faire correspondre la pièce bleue à la salle de réunion IFC 03 (7,21 m²), mais les collaborateurs ne peuvent pas confirmer cette correspondance sans repère commun entre photos et plan. Le WC IFC 07 (2,87 m²) est également à recaler. Il ne faut pas déplacer les objets IFC en se fiant à la perspective des photos.
3. La V5 indique une HSP de 3,00 m et une sous-face de dalle à +3,30 m, mais cette dalle est déjà identifiée comme hypothèse. Les vues ne confirment ni ces hauteurs, ni la géométrie, l'accès ou les charges du rangement haut.
4. L'IFC chiffre 15,74 m² de terrasse couverte, mais ne modélise pas le muret/grille comme garde-corps ni la limite juridique de l'espace. Les photos montrent surtout un chemin dallé irrégulier, un muret/portail et de la pelouse; elles ne prouvent pas que le chemin au-delà du muret est le dallage privatif voulu pour la terrasse. Relever la séquence seuil → terrasse couverte → muret/grille → chemin → pelouse/voie et confirmer les limites avant extension.

## Relevé nécessaire pour passer au plan coté

- Un plan coté de toutes les pièces avec épaisseurs, ouvertures, sens d'ouverture et orientation de façade; repérer explicitement sur ce plan la pièce bleue et la porte WC.
- Hauteurs sous plafond, sous poutres/retombées, niveau du haut rangement, hauteur libre dessous et dessus, profondeur/largeur, mode d'accès et appuis. Faire vérifier la capacité portante avant stockage.
- Cotes et niveaux du seuil, des marches, de la dalle extérieure et du dessus du muret/grille; limites privatives et état du dallage.
- Position des appareils WC, évacuations, arrivées d'eau, prises, tableau et unités de climatisation éventuelles.
- Cotes et emplacements du poteau, des murs potentiellement porteurs et de la fenêtre haute.

## Statut de la variante V6

La copie [DECIMO_ESQ_V6_OPTION_C_PROVISOIRE.ifc](DECIMO_ESQ_V6_OPTION_C_PROVISOIRE.ifc) continue de préserver toute la géométrie V5 et contient le programme comme calque IFC. Ce rapport améliore son registre d'hypothèses à partir des photos, mais **la géométrie de conception n'est pas encore recalée**. Le script [creer_option_c_ifc.py](scripts/creer_option_c_ifc.py) reproduit la variante provisoire.
