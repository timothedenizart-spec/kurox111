# Projet 2 — espace de coordination : Éclipse

## But commun

Créer un jeu de survie immersif dans lequel le joueur traverse, en temps réel, la bascule d’une crise sanitaire réaliste vers une apocalypse liée à une mutation infectieuse. La ville ne s’écroule pas instantanément : l’activité, la monnaie, les commerces, les soins et les relations humaines se dégradent avec des causes visibles et cohérentes.

La priorité est l’**observation** : pas de jauges de faim, soif, fatigue, hygiène ou besoins naturels. Si le personnage possède une montre, l’heure qui passe, ses capacités, son environnement et des indices narratifs deviennent ses repères.

> Les rythmes employés sont des conventions de jeu plausibles, non des recommandations de santé.

## Équipe et responsabilités

| Pôle | Nom de coordination | Mandat | Livrable / décision dont il est propriétaire |
| --- | --- | --- | --- |
| Coordination | **Orion** | Faire tenir ensemble récit, règles et contraintes de production. | Jalons, arbitrages et registre de décisions. |
| Épidémie | **Épidémie** | Modéliser transmission, incubation, gravité et mutation par paliers. | Machine d’états sanitaire, paramètres documentés. |
| Habitants | **Civitas** | Donner aux PNJ des foyers, priorités, mémoire et comportements. | Modèle de population, interactions et rumeurs. |
| Monde | **Atlas** | Rendre crédibles travail, argent, stocks, fermetures et institutions. | Modèle économique, commerce et services. |
| Survie | **Vigile** | Concevoir les besoins du personnage sans interface de jauges. | Déclencheurs temporels, indices, conséquences. |
| Temps | **Chronos** | Garantir un temps réel persistant et un calendrier lisible à la montre. | Horloge, sauvegarde, calendrier de crise. |
| Ambiance | **Nocturne** | Traduire les systèmes en sensation, son, messages et mise en scène. | Langage d’indices et direction d’interface. |
| Qualité | **Sentinelle** | Tester lisibilité, équité, performance et cohérence éthique. | Scénarios de test et critères de validation. |

Les noms ci-dessus désignent des **responsabilités de travail**, pas des personnages du jeu.

## Règles de coordination

1. Une fonctionnalité touche le moins de pôles possible ; si elle traverse plusieurs systèmes, Orion consigne l’arbitrage dans `DECISIONS.md`.
2. Épidémie publie les états et événements possibles avant que Civitas ne modélise les réactions des PNJ.
3. Atlas ne ferme jamais un commerce sans raison explicable par le joueur : absentéisme, livraison interrompue, restriction, violence, faillite ou décision du gérant.
4. Vigile propose toujours plusieurs signaux diégétiques avant une conséquence sévère. Aucune barre, pourcentage ou compte à rebours de besoin n’est montré au joueur.
5. Chronos conserve les instants réels des dernières actions ; les besoins ne se réinitialisent donc pas en changeant de page.
6. Sentinelle valide une fonctionnalité à la fois sur la cohérence, l’accessibilité et la charge émotionnelle avant extension.

## Périmètre du premier prototype

Le premier incrément est volontairement un **vertical slice local** : une personne, son immeuble, quatre commerces et un voisinage restreint. Il prouve les boucles centrales avant de prétendre simuler une métropole entière.

- horloge et sauvegarde locales ;
- besoins discrets : alimentation, hydratation, repos, hygiène, toilettes et lien social ;
- budget et inventaire restreints ;
- vingtaine de résidents aux états cachés ;
- informations incomplètes ;
- cinq phases de crise sur plusieurs jours réels.

Consulter [`TABLEAU.md`](TABLEAU.md) pour l’avancement, [`AGENTS.md`](AGENTS.md) pour les contrats d’interface entre pôles et [`LIVRAISON.md`](LIVRAISON.md) pour le dépôt de travail et la reprise coordonnée.
