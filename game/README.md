# Prototype jouable — ÉCLIPSE

Ce dossier contient le vertical slice du jeu. Il s’ouvre avec un serveur statique et ne nécessite ni build ni dépendance.

## Boucles implémentées

- **temps réel :** la montre lit l’heure locale et les états sont sauvegardés dans `localStorage` ;
- **besoins sans jauges :** six besoins utilisent des intervalles internes, puis renvoient seulement des phrases et des conséquences diégétiques ;
- **monde vivant :** dix-huit habitants possèdent une mobilité, des ressources, un foyer, une profession, un petit réseau de contacts, une mémoire courte et un état sanitaire non révélé ;
- **contamination :** les habitants passent par exposition, incubation, symptômes, gravité puis, assez tardivement, altération fictionnelle ; une exposition ne peut naître que dans un lieu partagé ;
- **économie :** stocks, quotas, prix et fermetures varient selon la phase de crise et une cause locale affichée (gérance, livraison, décision ou sécurité) ;
- **incertitude :** les descriptions d’habitants sont des observations, pas des diagnostics, et les rumeurs conservent une source et un statut qualitatif ;
- **repos :** une période d’au moins quatre heures réelles se résout à la reprise de partie, avec un événement nocturne consigné dans le carnet.

## Vérification rapide

1. Lancer le serveur indiqué au README racine.
2. Cliquer sur les besoins : eau, ration et argent doivent changer sans qu’aucune barre de besoin apparaisse.
3. Ouvrir un commerce : le stock est limité à une unité par jour réel et l’achat alimente le sac.
4. Ouvrir un habitant ou observer la rue : une note doit rejoindre le carnet.
5. Rafraîchir la page : la chronique doit reprendre au même état.

## Limites assumées de l’incrément

La transmission reste une simulation locale volontairement légère : elle modélise des lieux partagés et des réseaux sociaux limités, mais pas encore les foyers, les itinéraires complets ni la durée exacte de chaque rencontre. Les phases avancent sur des jours réels, conformément au parti pris du projet ; les contenus des phases lointaines sont donc codés et testables par lecture, mais nécessitent une partie persistante pour être vécus naturellement.
