# Journal de coordination

## 2026-11-16 — lancement du premier incrément

- Objectif confirmé : une simulation de survie pandémique lente et crédible avant la mutation fictionnelle.
- Rôles verrouillés : Orion (coordination), Épidémie (contamination), Civitas (PNJ), Atlas (économie), Vigile (survie), Chronos (temps), Nocturne (ambiance), Sentinelle (qualité).
- Décision de démarrer par un prototype web local, persistant et sans dépendance.
- La première implémentation vise une boucle observable, pas une simulation exhaustive : montre, besoins sans jauges, voisinage, commerces et escalade de crise.

## 2026-11-16 — deuxième incrément : le quartier prend des habitudes

- Épidémie et Civitas ont remplacé le risque global par une transmission dans les lieux partagés : épicerie, pharmacie, place et trajets.
- Chaque résident possède désormais un petit réseau de contacts, un lieu courant et une mémoire courte, ce qui permet des observations plus cohérentes.
- Nocturne a ajouté les rumeurs datées avec source et degré d’incertitude ; elles restent des fragments, jamais un diagnostic.
- Atlas rend les ouvertures et fermetures explicables dans l’interface : livraisons, décisions, manque de personnel ou état du gérant.
- Chronos et Vigile résolvent un repos prolongé lorsque la partie reprend et consignent un incident nocturne sobre.

## 2026-11-16 — troisième incrément : la solidarité a un coût

- Civitas relie maintenant le joueur à chaque voisin par une relation qualitative : quelques mots, entraide matérielle, partage de rumeur ou retrait la font évoluer.
- Les gestes peuvent être mémorisés et retransmis par le réseau proche d’un résident ; une aide locale peut donc devenir une information qui circule.
- Atlas ajoute un stock interne par commerce, consommé par le quartier et réalimenté par une tournée journalière de Noé lorsque son trajet reste possible.
- Les commerces n’exposent jamais le stock numérique : ils racontent un dernier arrivage, des derniers articles ou des rayons épuisés.

## 2026-11-16 — dépôt et coordination de reprise

- Les trois incréments du prototype sont déposés dans `LIVRAISON.md`, avec leurs références de commit, leur périmètre réel et leurs vérifications.
- Chaque pôle reçoit une responsabilité de reprise et un critère de passage ; les prochaines modifications ne doivent pas mêler plusieurs propriétaires du même fichier logique sans arbitrage d’Orion.
- Le cycle suivant est volontairement limité à quatre axes : conséquences contextuelles des besoins, accessibilité de l’intensité, relations autonomes entre PNJ et demandes de quartier.
