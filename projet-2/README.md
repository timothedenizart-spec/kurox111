# Projet 2 — coordination des agents (jeu d’apocalypse pandémique)

Cet espace est le point de coordination et de dépôt du travail pour le prototype de jeu de survie **La dernière semaine**. Il organise les rôles, décisions, livraisons et relais entre les domaines de simulation, expérience, habitants, économie, technique et vérification.

## État actuel : phase 1 — prototype V0.3 déposé

La V0.3 est livrée sur la branche de travail et documentée dans [`LIVRAISON_V0.3.md`](LIVRAISON_V0.3.md). Elle contient une démo web locale avec :

- montre diégétique et besoins exprimés par le temps de jeu, sans jauges ;
- habitants contextuels qui se déplacent, mémorisent les interactions et construisent une confiance ;
- crise fictionnelle progressive, du quotidien à l’effondrement social puis aux infectés ;
- économie qui perd sa valeur au profit des ressources et de l’entraide ;
- exposition fictionnelle signalée narrativement, sans donnée médicale ni diagnostic ;
- signaux de quartier, radio, abri préparé et refuge collectif.

La branche est prête à être relue via la pull request [#2](https://github.com/timothedenizart-spec/kurox111/pull/2). Le prochain lot, **P2-007**, approfondit les relations persistantes et les comportements propres à chaque habitant.

## Équipe nommée

- `ORBIT` — coordination, dépendances, ordre des livraisons et arbitrage
- `LYRA` — direction d’expérience, ton et choix narratifs
- `ATLAS` — simulation systémique et règles de monde
- `NOVA` — habitants, relations et comportements contextuels
- `MINT` — économie, services et valeur des ressources
- `VITA` — survie, confort joueur et interface sans jauges
- `FORGE` — architecture technique, performance et intégration
- `ARGUS` — vérification, tests et cohérence

Les responsabilités détaillées, limites et règles de relais sont dans [`AGENTS.md`](AGENTS.md).

## Documents de coordination

| Document | Usage |
| --- | --- |
| [`LIVRAISON_V0.3.md`](LIVRAISON_V0.3.md) | Dépôt de la version livrée, validation et relais technique |
| [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md) | Inventaire des branches, agents/rôles déclarés et prototypes retrouvés |
| [`CAHIER_DES_CHARGES.md`](CAHIER_DES_CHARGES.md) | Exigences d’origine E-01 à E-12 |
| [`EQUIPE.md`](EQUIPE.md) | Rôles canoniques et correspondance des alias historiques |
| [`QUESTIONS_OUVERTES.md`](QUESTIONS_OUVERTES.md) | Choix produit non encore tranchés |
| [`CONCEPTION.md`](CONCEPTION.md) | Annexes de conception proposées, à aligner avec le brief V0.3 |
| [`VALIDATION.md`](VALIDATION.md) | Scénarios de revue et état des vérifications |
| [`PROTOTYPE.md`](PROTOTYPE.md) | Commandes, fonctionnalités et limites du prototype |
| [`TABLEAU.md`](TABLEAU.md) | État des tâches, dépendances et prochain lot actif |
| [`AGENTS.md`](AGENTS.md) | Rôles, autorité de décision et protocole de relais |
| [`BRIEF.md`](BRIEF.md) | Vision du jeu, périmètre et itérations V0.1 à V0.3 |
| [`JOURNAL.md`](JOURNAL.md) | Transmissions horodatées, validations et blocages |
| [`DECISIONS.md`](DECISIONS.md) | Décisions confirmées et leurs conséquences |
| [`MODELE_TACHE.md`](MODELE_TACHE.md) | Format d’une nouvelle tâche ou fiche de relais |

## Règles de coordination actives

1. Une tâche active a un responsable de coordination unique, même si plusieurs rôles y contribuent.
2. Tout changement de périmètre, hypothèse ou blocage est inscrit dans le journal avant d’être propagé.
3. Les règles de simulation restent fictionnelles : aucune information médicale, sanitaire ou biologique réelle ne doit être ajoutée comme mécanique de jeu.
4. Les besoins du joueur restent des ressentis liés au temps de jeu : aucune jauge corporelle ne doit être introduite sans décision explicite.
5. Une livraison est déposée seulement avec ses fichiers, son contrôle automatisé et son relais documenté.
