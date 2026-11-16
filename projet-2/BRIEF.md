# Brief de production — Projet 2

## But validé

Créer une expérience de survie immersive dans une ville fictive. Le monde passe progressivement d’une crise sanitaire fictive à un effondrement social, puis à une apocalypse de créatures infectées. Le joueur doit lire son environnement, l’horloge de sa montre et les réactions des habitants plutôt que remplir des jauges.

Le projet vise une **simulation crédible au service du jeu**, et non un modèle médical, sanitaire ou économique réel. La contagion, ses mutations et les créatures sont entièrement fictives.

## Piliers de conception

1. **Temps lisible, corps ressenti** — faim, soif, sommeil, hygiène, toilettes, stress et besoin social sont déclenchés par le temps écoulé dans le jeu. Ils produisent des ressentis et des conséquences contextuelles, jamais des barres de progression.
2. **Habitants qui ont une intention** — chaque habitant possède un foyer, une destination, un état, une mémoire courte et une priorité immédiate (travailler, se protéger, chercher une ressource, aider, éviter une zone). Leur comportement évolue avec les informations et la situation.
3. **Contamination fictionnelle progressive** — l’intensité mondiale, les rumeurs, les comportements et les lieux changent par phases narratives. La transformation finale est un élément de fiction, sans détail réel sur les agents pathogènes.
4. **Économie qui se délite** — au début, travailler et acheter sont importants. À mesure que les services cessent, les prix, l’ouverture des commerces et la valeur de l’argent changent ; les ressources, relations et refuges prennent le relais.
5. **Information diégétique** — montre, journal, conversations, vitrines, rues et attitudes des habitants donnent les informations indispensables.

## Première tranche livrable : prototype web V0.1

Le premier livrable est une démo jouable dans le navigateur, située dans une petite ville fictive.

| Élément | Inclus dans V0.1 |
| --- | --- |
| Horloge | Temps de jeu, jour et phase affichés dans une montre diégétique |
| Besoins | Ressentis textuels calculés à partir du temps écoulé, sans jauges |
| Monde | Cinq lieux et des commerces qui ferment au fil des jours |
| Habitants | Une population simulée, avec état, emplacement et comportements contextuels |
| Crise | Phases d’alerte, de rupture puis de transformation fictionnelle |
| Économie | Argent utile au départ, prix et accès aux commerces qui se dégradent |
| Boucle joueur | Se déplacer, travailler, acheter, manger, boire, se reposer, se laver, échanger et observer |

## Hors périmètre de V0.1

- multijoueur ;
- graphismes photoréalistes ou monde 3D ;
- diagnostic médical, données sanitaires ou mécanismes biologiques réels ;
- génération infinie de monde ;
- contenu graphique ou choquant.

## Langage commun des agents

- **Fait** : élément présent et vérifiable dans la démo.
- **Hypothèse** : idée à tester, non considérée comme une promesse.
- **Décision** : choix validé dans `DECISIONS.md`.
- **Risque** : élément qui peut nuire à la cohérence, au confort de jeu ou à la faisabilité.

La personne responsable garde le dernier mot sur le ton, la portée et les priorités.
