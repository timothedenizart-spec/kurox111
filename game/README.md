# Prototype jouable — ÉCLIPSE

Ce dossier contient le vertical slice du jeu. Il s’ouvre avec un serveur statique et ne nécessite ni build ni dépendance.

## Boucles implémentées

- **temps réel :** la montre lit l’heure locale et les états sont sauvegardés dans `localStorage` ;
- **besoins sans jauges :** six besoins utilisent des intervalles internes, puis renvoient seulement des phrases et des conséquences diégétiques ;
- **monde vivant :** dix-huit habitants possèdent une mobilité, des ressources, un foyer, une profession, une mémoire courte et un état sanitaire non révélé ;
- **contamination :** les habitants passent par exposition, incubation, symptômes, gravité puis, assez tardivement, altération fictionnelle ;
- **économie :** stocks, quotas, prix et fermetures varient selon la phase de crise ;
- **incertitude :** les descriptions d’habitants sont des observations, pas des diagnostics.

## Vérification rapide

1. Lancer le serveur indiqué au README racine.
2. Cliquer sur les besoins : eau, ration et argent doivent changer sans qu’aucune barre de besoin apparaisse.
3. Ouvrir un commerce : le stock est limité à une unité par jour réel et l’achat alimente le sac.
4. Ouvrir un habitant ou observer la rue : une note doit rejoindre le carnet.
5. Rafraîchir la page : la chronique doit reprendre au même état.

## Limites assumées de l’incrément

La transmission est encore une probabilitié locale simplifiée : elle ne modélise pas encore les réseaux précis de lieux, les foyers ni les contacts individuels. Les phases avancent sur des jours réels, conformément au parti pris du projet ; les contenus des phases lointaines sont donc codés et testables par lecture, mais nécessitent une partie persistante pour être vécus naturellement.
