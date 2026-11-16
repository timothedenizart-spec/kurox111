# Équipe et protocole de coordination — Projet 2

> **Statut : V0.3 déposée pour relecture; P2-007 est le prochain lot planifié.** Les identifiants ci-dessous structurent les responsabilités consignées dans ce dépôt. Ils ne signifient pas que huit agents autonomes sont effectivement connectés à cette conversation.

## Équipe de travail

| Identifiant de rôle | Responsabilité | Responsable de | Ne décide pas seul |
| --- | --- | --- | --- |
| `ORBIT` | Coordination principale | Ordre des travaux, dépendances, tableau, journal et arbitrages de périmètre | Choix créatifs ou de production irréversibles sans validation de la personne responsable |
| `LYRA` | Direction d’expérience | Ton, rythme, intentions du joueur et cohérence narrative | Systèmes techniques ou économiques hors de son périmètre |
| `ATLAS` | Simulation systémique | Cohérence des phases du monde et dépendances entre systèmes | Implémentation technique ou validation finale |
| `NOVA` | Comportements des personnages | Besoins, réactions, interactions et mémoire des PNJ | Règles globales du monde ou performances techniques |
| `MINT` | Économie et services | Ressources, services, commerces et transformations économiques | Choix narratifs ou besoins individuels des personnages |
| `VITA` | Survie et confort joueur | Ressentis, lisibilité des besoins et interface sans jauges | Systèmes de simulation hors de son périmètre |
| `FORGE` | Technique et intégration | Faisabilité, architecture, performance et outillage | Priorités produit, contenu ou décisions artistiques |
| `ARGUS` | Vérification et cohérence | Critères d’acceptation, relecture croisée et suivi des risques | Lancement d’une tâche non attribuée |

Ces identifiants servent à attribuer et tracer le travail dans les fichiers et la PR. Dans cette conversation, la coordination est assurée par un seul agent d’assistance; aucun échange indépendant entre plusieurs agents n’est revendiqué.

## Autorité de décision

1. La personne responsable fixe vision, priorités, portée et feu vert de production.
2. `ORBIT` organise le travail approuvé et signale les périmètres flous.
3. Chaque rôle prépare son domaine; une relecture croisée est requise si une décision affecte un autre domaine.
4. `ARGUS` demande des critères vérifiables avant qu’une tâche soit considérée prête.
5. En cas de désaccord, les options sont consignées; la personne responsable tranche les choix de vision.

## Circuit de travail et relais

`ORBIT` → rôles de domaine concernés → `FORGE` (faisabilité/intégration) → `ARGUS` (vérification) → `ORBIT` → personne responsable.

Une tâche doit avoir un état et un résultat attendu dans `TABLEAU.md`. Chaque relais indique son objectif, son périmètre, ses hypothèses, ses fichiers et la prochaine action. Les décisions confirmées vont dans `DECISIONS.md`; questions et blocages dans `JOURNAL.md`.

## Contraintes de projet

- Le réalisme recherché est narratif et systémique; la contagion et les infectés sont fictionnels.
- Ne pas ajouter d’information médicale réelle ni de conseil sanitaire.
- Les besoins du joueur sont exprimés par le temps et les ressentis, pas par des jauges corporelles.
- Toute nouvelle livraison apporte les fichiers, les vérifications et un relais documenté.
