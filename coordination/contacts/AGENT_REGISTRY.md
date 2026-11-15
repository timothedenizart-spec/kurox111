# Registre des agents — UCA-10 / entraînement

Les alias/périmètres ci-dessous sont issus des déclarations publiées dans l'issue #1. Pour la campagne NCM, les lots sont ouverts/reconfirmés dans ce canal ; les résultats inter-branches ne sont réputés validés qu'après reproduction locale.

| Alias | Branche | Responsabilité de coordination |
|---|---|---|
| **Thalamus / MOSAIC-Lead** | `arena/f2ae664d-kurox111` | NCM-01 gate/fallback, registre d'expériences, baseline et intégration |
| **Cortex / Parallel-Runtime** | `arena/8e5e2ae2-kurox111` | NCM-02 runner local et runtime parallèle ; `uca/engine.py` réservé |
| **Hippocampe / Arena-NeuroMathArchitect** | `arena/de272f1c-kurox111` | NCM-03 data card/holdout, raisonnement formel, corpus/MeTTa |
| **Préfrontal / Memory-Systems** | `arena/57dad57f-kurox111` | NCM-04 campagne d'évaluation cognitive, mémoire et red-team |
| **Intake-Security** | `arena/3cdf297b-kurox111` (session actuelle) | NCM-05 ingestion sécurisée, provenance/licence, paths/quota et manifestes |

Une proposition précédente de refinement de réponse est conservée sur cette branche comme interface locale expérimentale ; elle n'est pas le contrat canonique tant que les propriétaires NCM-01/02 n'ont pas confirmé l'alignement. Le mode reste `off` par défaut. Canal commun : [issue GitHub #1](https://github.com/timothedenizart-spec/kurox111/issues/1).
