# Rapport différentiel IFC — V5 vers V6 Option C

Source : `v5/DECIMO_ESQ_V5.ifc` (IFC4). Variante générée par `v6/scripts/generer_ifc_v6.py` vers `v6/DECIMO_ESQ_V6_OPTION_C.ifc`. La V5 n’est pas modifiée.

## Résultat du différentiel

- V5 : 231 produits IFC; V6 : 230. 218 produits conservent leur GlobalId; 13 meubles V5 sont retirés et 12 objets V6 ajoutés.
- Les retraits ciblés comprennent le comptoir et le siège d’accueil V5, la table de réunion et ses quatre chaises, le groupe fauteuils/table basse remplacé par le coworking, l’arbre à livres central demandé retiré par A03, et deux modules `B01` de rayonnage est remplacés par un linéaire droit plus long. Les 3 modules de niche/rangement nord et les rayonnages ouest sont conservés. Aucun retrait générique de `IfcFurnishingElement`/`IfcFurniture` n’est appliqué.
- L’arbre n’avait pas de mobilier explicitement agrégé ou relié par relation IFC. Les meubles de réunion/coworking retirés séparément sont ceux indiqués ci-dessus; aucun autre meuble n’est supprimé au seul titre d’une association supposée à l’arbre.
- Restent préservés, notamment, l’habillage menuisé du tableau divisionnaire (IfcFurniture), le tableau mural, les niches nord, la banquette, la console vinyles, les équipements techniques, les 27 luminaires, portes, murs, vitrage, réseaux et sanitaires.
- Parmi les 212 produits conservés ayant une représentation, 203 ont une boîte englobante identique à la V5, à la tolérance numérique de 1e-7 m. Les 9 autres sont des murs V5 avec représentation d’axe 2D seulement : leur représentation IFC est conservée, mais IfcOpenShell ne calcule pas de boîte englobante volumique à partir de ces axes. Six autres produits conservés n’ont pas de représentation géométrique. Les 8 `IfcSpace` gardent leur géométrie V5; seuls leurs noms longs/descriptions et propriétés d’usage V6 changent. L’usage réunion de la pièce bleue/Space 03 est confirmé par la cliente; l’emprise précise de cet IfcSpace reste à confronter au relevé. Les espaces 06 et 07 ne sont pas recalculés.

## Mobilier et rayonnages V6

- `IfcFurnishingElement` : comptoir accueil-café intégré, siège accueil-café, table réunion 6 places, groupe de 6 sièges, deux rayonnages droits nord/est, table coworking 4 places, deux postes de lecture individuels.
- Le comptoir est un poste unique côté entrée, de principe 1,79 m de longueur; l’assise est à l’ouest du comptoir, dossier orienté vers le mur ouest et personne tournée vers l’est, vers les livres. Le modèle donne environ 0,38 m entre assise et comptoir et environ 0,11 m entre assise et face intérieure du mur ouest. Ces dégagements sont à confirmer avec une chaise réelle, l’ergonomie de service et les cotes finies.
- Le rayonnage nord-est mesure environ 2,8 m de linéaire et reste au sud des niches fixes nord. Le rayonnage est mesure environ 2,3 m; il remplace les deux modules V5 est retirés. Il commence à y=4,35 m, environ 0,15 m après la limite nord du poteau IFC 4351026 (bbox V5 x=5,61–6,51 m, y=3,30–4,20 m). Aucune géométrie ajoutée n’intersecte la bbox de ce poteau. Les passages et ancrages restent à contrôler sur site.

## Confidentialité WC, réserve haute et terrasse

- `IfcBuildingElementProxy` `V6 — retour opaque WC en option - à valider` : retour opaque de 0,03 x 0,48 m, hauteur 1,85 m, positionné le long de la rive est du dégagement IFC 06. La largeur IFC de principe passe de 1,03 m à 1,00 m; le retour ne traverse pas la circulation et précède la porte WC. C’est une option démontable, non une validation d’accessibilité ou de conformité : vérifier largeur finie, débattement de porte, visibilité depuis bibliothèque/coworking/salle vitrée et fonctionnement sur site.
- `IfcSlab` : plateforme de réserve au-dessus de la partie arrière de la pièce bleue présumée (`IfcSpace 03`), entre z +2,08 et +2,28 m. Hypothèse seulement; emprise, appuis, structure, hauteur libre, accès par échelle, garde-corps, incendie et charge restent à vérifier avec relevé et ingénieur. Ne pas construire ni charger sur la base de ce modèle.
- `IfcCovering` : emprise de dallage extérieur optionnelle, distincte de la terrasse couverte V5. Limites foncières, niveaux, pente et évacuation d’eau restent à relever. Le recouvrement graphique du terrain V5 est volontaire pour montrer l’option de finition.

## Validation exécutée

`v5/scripts/valider_ifc.py` sur le fichier V6 : schéma IFC4; 0 erreur EXPRESS, 0 avertissement, 224 produits avec représentation contrôlés, 224 géométries réussies, 0 échec. Les 12 nouveaux objets sont dans le groupe `Option C V6 — mobilier, réserve, terrasse`, modifiables séparément dans le modèle IFC.

## Limites

La génération de maillages et la validation IFC ne constituent pas un contrôle complet des collisions ni une validation de constructibilité, d’accessibilité ou de conformité réglementaire. La disposition du mobilier, le retour WC, les cotes de la pièce bleue et la plateforme sont à confronter au site avant exécution.
