# Base de conception — Projet 2

**Statut :** annexe de conception issue du cadrage initial. La référence produit actuelle est [`BRIEF.md`](BRIEF.md), la livraison réelle est [`LIVRAISON_V0.3.md`](LIVRAISON_V0.3.md); les idées de cette annexe ne sont pas toutes implémentées ni validées. Pour la provenance des autres prototypes, voir [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md).

## 1. Expérience visée

Le joueur traverse une crise qui commence comme une urgence sanitaire et sociale, pas comme une apocalypse déjà installée. Au départ, les routines et institutions fonctionnent encore, mais l’information est incomplète et les décisions ont un coût. Au fil des jours et des semaines de jeu, les effets cumulés de la crise transforment les comportements, les services, l’économie et les dangers. La mutation vers une menace zombie est un élément fictionnel tardif, annoncé par des signes narratifs, et non une surprise sans préparation.

Le monde doit paraître vivant sans simuler chaque détail à la même résolution. Les systèmes produisent des situations émergentes, mais restent compréhensibles, cohérents et justes pour le joueur.

## 2. Boucle de jeu proposée

1. **Observer** : heure à la montre, météo, état du personnage, nouvelles, lieux ouverts, comportements des habitants.
2. **Évaluer** : besoins, risques, ressources, objectifs immédiats et conséquences possibles.
3. **Planifier** : choisir une destination, un itinéraire et ce qu’on emporte; arbitrer temps, sécurité et ressources.
4. **Agir** : explorer, se ravitailler, travailler, aider, se reposer, communiquer ou éviter une menace.
5. **Subir les conséquences** : temps écoulé, changements corporels, réactions des PNJ, évolution des stocks et de la crise.
6. **S’adapter** : revoir ses priorités quand l’information et l’état du monde changent.

Cette boucle est une hypothèse de travail. La durée d’une journée de jeu, le rythme de progression et les activités centrales restent à valider.

## 3. Besoins corporels sans jauges permanentes

### Principe

Le système suit le temps écoulé depuis les événements pertinents, ainsi que l’effort, le contexte et l’état du personnage. Il n’exige pas de jauges constamment visibles. Une montre et des signes diégétiques donnent au joueur des informations graduelles : sensations, animation, dialogue intérieur sobre, difficultés d’action, odeurs, environnement et routines accessibles.

### Variables à modéliser

- **Faim et soif :** temps depuis l’apport, quantité et qualité de ce qui a été consommé, chaleur, effort et état de santé.
- **Sommeil :** temps éveillé, qualité et durée du dernier repos, stress, bruit, sécurité et interruptions.
- **Hygiène :** temps, activité, météo, accès à l’eau et au savon, état des vêtements et environnement. Effets d’abord sociaux et de confort; ne pas faire de l’hygiène un raccourci punitif vers une maladie.
- **Besoins naturels :** temps depuis la dernière fois, consommation, stress, disponibilité d’un lieu sûr et conséquences pratiques d’un retard. Préserver la dignité du personnage et éviter une simulation humiliante ou graphique.
- **Envies et confort :** envies contextualisées (boisson chaude, confort, intimité, contact social, activité familière), différenciées des besoins vitaux. Elles influencent humeur et choix, mais ne sont pas des obligations répétitives.

### Règles de conception

- Employer des courbes graduelles et des plages variables, pas un compte à rebours universel identique pour tous.
- Les heures affichées par la montre reflètent le temps du monde; les besoins évoluent avec ce temps, à une vitesse de jeu qui reste à régler et à tester.
- Afficher un indice lorsque l’état est pertinent, et laisser le joueur consulter une page d’état volontairement. Ne pas cacher une conséquence grave derrière un signal indéchiffrable.
- Prévoir traits, santé, âge adulte, climat, activité, accès aux ressources et difficulté comme modificateurs prudents, sans transformer les différences individuelles en caricatures.
- Distinguer inconfort, baisse de performance et urgence. Les effets extrêmes doivent être rares, annoncés et évitables par une planification raisonnable.
- Proposer des options d’accessibilité (rappels, intensité des effets, fréquence des signaux, pause, simplification) sans invalider le jeu.

## 4. Épidémie et transformation fictionnelles

La progression combine une **simulation de fond abstraite** (état de groupes, contacts simulés, mobilité, lieux et mesures de crise) et des événements concrets vécus par le joueur. Le jeu communique des probabilités et des tendances par des indices imparfaits : absences, annonces contradictoires, files d’attente, changements de règles, services débordés et évolution des comportements.

Étapes narratives proposées, sans calendrier fixe :

1. **Signal faible** — cas signalés, incertitude, vie quotidienne largement maintenue.
2. **Crise visible** — informations concurrentes, précautions et perturbations localisées.
3. **Pression systémique** — services sollicités, pénuries ponctuelles, changements de mobilité et de confiance.
4. **Ruptures** — institutions et commerces fonctionnent de manière inégale; communautés et réseaux locaux prennent de l’importance.
5. **Mutation fictionnelle** — symptômes et comportements nouveaux annoncent une menace qui change les règles de survie.
6. **Nouvel équilibre** — communautés, dangers et ressources se réorganisent; aucune fin unique n’est imposée par le seul compteur de temps.

Ces phases sont des états de conception, pas des instructions médicales ni un modèle prédictif du monde réel. L’exposition en jeu doit être lisible sans révéler à coup sûr chaque issue; une protection réduit le risque sans garantir l’immunité. Les manifestations, durées, paramètres biologiques et vecteurs exacts restent fictionnels et abstraits.

## 5. Habitants et PNJ

Simuler les PNJ à plusieurs niveaux pour concilier intelligence apparente et performances :

- **Proche du joueur :** perceptions locales, objectifs à court terme, mémoire récente, besoins, réactions et dialogue contextuel.
- **Dans la zone :** routines résumées, déplacements par objectifs, relations et changements d’état sans calcul détaillé à chaque instant.
- **Hors champ :** progression agrégée par communauté et événements, réconciliée au retour du joueur.

Chaque PNJ important possède une identité, quelques besoins prioritaires, un métier ou rôle, un réseau relationnel, un niveau d’information et des contraintes. Les décisions doivent découler de ce qu’il sait et peut faire, pas d’une omniscience. Les agents peuvent coopérer, refuser, négocier, se tromper, changer de routine et réagir à la confiance comme aux ressources. Éviter que chaque PNJ exige une conversation ou un suivi individuel permanent.

## 6. Économie et disponibilité

L’argent n’est pas un interrupteur qui cesse soudainement d’avoir cours. La valeur pratique d’un achat varie selon le lieu et le moment : ouverture, stocks, moyens de paiement, confiance, règles locales et risque. Les commerces ferment ou réduisent leur offre par causes distinctes (approvisionnement, personnel, sécurité, énergie, décision du propriétaire), à des rythmes inégaux.

Le jeu suit des catégories de stock et de demande plutôt que chaque unité partout. Au début, travail, revenu, prix et paiement sont utiles. Ensuite, certains biens deviennent rares, les services deviennent intermittents, puis le troc, l’entraide et les réseaux locaux peuvent prendre plus d’importance. L’argent peut conserver une utilité résiduelle sans garantir l’accès à une ressource absente.

## 7. Conséquences, fins et rythme

Les fins devraient découler de choix, relations, préparation et état des communautés, plutôt que d’un unique score caché. Prévoir plusieurs issues compatibles avec le ton : protection d’un groupe, départ, maintien d’un refuge, recherche d’une solution, ou échec de survie. Les conditions détaillées restent à concevoir.

La crise doit laisser des fenêtres de préparation et de réorientation. Les événements majeurs sont annoncés ou inférables; les surprises relèvent de l’incertitude du monde, pas de règles qui changent arbitrairement.

## 8. Questions à faire trancher

- Plateforme et moteur visés? Solo uniquement au premier livrable?
- Vue et format : première personne, troisième personne, isométrique, texte ou autre?
- Durée visée d’une journée de jeu et possibilité de mettre en pause?
- Niveau de violence, thèmes exclus et options de contenu?
- Périmètre du premier prototype : une zone, une journée et quelques PNJ, ou autre?

## 9. Critères de validation de la conception

- Un joueur peut expliquer pourquoi un besoin devient préoccupant à partir du temps et des circonstances.
- Les signes précurseurs permettent de prendre une décision avant une conséquence majeure.
- Les PNJ réagissent sur la base d’informations et de ressources plausibles à leur situation.
- Les changements de commerces et de valeur de l’argent ont des causes visibles et peuvent différer selon les lieux.
- La progression de crise est graduelle, cohérente et n’impose pas un calendrier identique à chaque partie.
- Les options d’accessibilité permettent de réduire les irritants sans supprimer les informations nécessaires.
