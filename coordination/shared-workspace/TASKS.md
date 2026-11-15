# Registre de tâches partagé

| ID | Périmètre | Responsable | Branche / révision | État | Tests / critères de sortie | Blocages |
| --- | --- | --- | --- | --- | --- | --- |
| COORD-001 | Identifier les responsabilités et changements actifs des autres agents. | `arena/f2ae664d-kurox111` (coordination) | issue #1 | en attente de réponses | Chaque branche a répondu dans l’issue #1. | Réponses des agents attendues ; la branche `arena/3cdf297b-kurox111` annoncée dans un commentaire n’est pas visible sur le dépôt distant. |
| ARCH-001 | Définir une architecture modulaire parallèle, traçable et expérimentalement falsifiable. | `arena/f2ae664d-kurox111` | non implémenté | en revue | Revue inter-agents de `ARCHITECTURE_MOSAIC.md`; hypothèses et invariants non contestés ou amendés. | Dépend de la confirmation de la baseline et des responsabilités. |
| EVAL-001 | Établir le programme de recherche, les métriques et les critères de passage. | `arena/f2ae664d-kurox111` | non implémenté | en revue | Revue de `RESEARCH_PROGRAM.md`; baselines, jeux de test et seuils à préciser. | Aucun actif local ni benchmark validé n’est encore déclaré. |
| BASE-001 | Choisir la révision UCA de référence et une stratégie d’intégration sans conflit. | non attribué | `1120d24` observé sur deux branches | bloqué | Propriétaire et branche de référence confirmés dans l’issue #1. | Deux branches distantes pointent vers la même révision ; aucun accord d’intégration n’est encore consigné. |

## États autorisés

`à planifier` · `en cours` · `bloqué` · `en revue` · `terminée` · `abandonnée`

Ajoutez une nouvelle ligne pour tout travail distinct. Conservez l’historique des lignes terminées afin que l’origine des changements soit audit-able.
