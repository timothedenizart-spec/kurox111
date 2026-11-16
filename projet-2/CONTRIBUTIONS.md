# Registre des contributions retrouvées — Projet 2

État du repérage au 16 novembre 2026. Sources consultées : branches Git distantes, PR ouvertes/fermées et issues de coordination. Les fichiers ci-dessous sont regroupés ici sans effacer leur provenance. Les noms de rôles historiques sont des étiquettes de responsabilités, pas une preuve de présence de plusieurs agents autonomes.

## Référence intégrée

| Source | Contenu retrouvé | État dans l’espace commun |
| --- | --- | --- |
| Branche `arena/59647e61-kurox111`, commit `c28976ea538d` (PR #2) | Brief V0.1, itérations V0.2–V0.3, prototype web `app.js`/`simulation.js`, interface, dix tests, livraison et protocole de coordination. | **Intégré comme base jouable de référence** à la racine du dépôt. PR #2 demeure ouverte pour revue. |
| Branche `arena/458e1a3c-kurox111`, commit `4d733be13d94` | Cahier des charges E-01 à E-12, propositions de rôles, questions ouvertes plateforme/format/temps, règles de coordination. | Documents intégrés ici : `CAHIER_DES_CHARGES.md`, `EQUIPE.md`, `QUESTIONS_OUVERTES.md`. Les décisions provisoires postérieures sont distinguées dans le brief et le registre de décisions. |

## Prototypes parallèles archivés

| Source | Contenu retrouvé | Contrôle refait ici | Décision de coordination |
| --- | --- | --- | --- |
| Branche `arena/ef1aae95-kurox111`, commit `eda837879f9b` (déclaration de rôle Cité sous l’alias Noroît dans l’issue #3) | Prototype distinct avec exposition fictionnelle, routines/isolement des PNJ, mémoire relationnelle, entraide, économie et fins; sept tests `node:test`; notes de conception et coordination. | Sept tests réussis en environnement CommonJS isolé. Le lancement direct depuis le dépôt ESM échoue à cause du `require` dans `smoke.test.js`; ce détail est conservé pour éviter de présenter le contrôle comme natif. | Code et notes conservés dans [`contributions/arena-ef1aae95/ARCHIVE.md`](contributions/arena-ef1aae95/ARCHIVE.md). Ne pas fusionner en bloc; comparer les concepts utiles à la V0.4. |
| Branche `arena/1dbdd8bb-kurox111`, commit `86b42e75dc28` | Prototype distinct « Éclipse » : horloge et sauvegarde temps réel, propagation par lieux partagés, mémoire/rumeurs de quartier, économie avec stocks et livraison, choix sociaux; plan de relais par pôles. | `node --check` de `game/app.js` réussi. Cette branche ne fournit pas de suite de tests automatisés reproductible dans ses fichiers déposés. | Prototype et documents de branche conservés dans [`contributions/arena-1dbdd8bb/ARCHIVE.md`](contributions/arena-1dbdd8bb/ARCHIVE.md). À évaluer, notamment sauvegarde, causalité des stocks et simulation locale, sans remplacer la référence sans décision/revue. |

## Recherche et périmètre

- Une seule PR de jeu est ouverte : [PR #2](https://github.com/timothedenizart-spec/kurox111/pull/2).
- Le canal spécifique Projet 2 est [l’issue #3](https://github.com/timothedenizart-spec/kurox111/issues/3); elle contient la déclaration Noroît/Cité et demande l’arbitrage avant copie de sa branche.
- Les branches historiques avec artefacts Projet 2 repérées sont `arena/458e1a3c-kurox111`, `arena/59647e61-kurox111`, `arena/ef1aae95-kurox111` et `arena/1dbdd8bb-kurox111`. Les autres branches distantes inspectées ne contenaient pas de dossier Projet 2.
- Les travaux sans rapport avec le jeu, notamment ceux liés à UCA, ne sont pas importés dans ce projet.

## Suite de coordination

La V0.3 de la PR #2 reste la seule base d’intégration afin d’éviter trois applications concurrentes. Les deux prototypes archivés sont des sources d’idées et de comportement à comparer, pas des branches de code fusionnées. Toute extraction de fonctionnalité doit être proposée comme tâche P2 avec provenance, critères et tests. La personne responsable arbitre les éléments qui changent le produit.
