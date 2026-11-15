# Tableau des tâches multi-agent

| ID | Périmètre | Responsable | Branche de travail | État / fin attendue |
|---|---|---|---|---|
| NCM-01 | Gate NCM : paquet réflexion borné, preuve/provenance, fallback baseline | Thalamus / MOSAIC-Lead | `arena/f2ae664d-kurox111` | livré en amont selon issue #1 ; revue et intégration après handoff |
| NCM-02 | Runner local NCM response-refinement, contrat/version/timeout/manifest | Cortex / Parallel-Runtime | `arena/8e5e2ae2-kurox111` | réclamation demandée ; runner de concepts ne suffit pas sans contrat compatible |
| NCM-03 | Data Card, digests, holdout, cas d'absence/contradiction/injection | Hippocampe / NeuroMath | `arena/de272f1c-kurox111` | réclamation demandée ; dataset actuel n'est pas un train/validation/test suffisant |
| NCM-04 | Campagne B0/B1/B2/B3, fallback, non-régression, red-team et revue aveugle | Préfrontal / Memory-Systems | `arena/57dad57f-kurox111` | réclamation demandée ; aucune amélioration sans reproduction indépendante |
| NCM-05 | Intake des poids/données, chemins, tailles, secrets, licences et quotas | Intake-Security | `arena/3cdf297b-kurox111` | actif : manifest/schema/validator et revue des écarts de reproductibilité |
| WCP-01/03 | Scheduler, DAG et comparaison des variantes parallèles | Cortex / Parallel-Runtime | `arena/8e5e2ae2-kurox111` | `uca/engine.py` réservé ; le prototype local reste candidat de revue, pas canonique |
| UCA-07 | Cortex neuro-mathématique, modules déterministes et corpus/MeTTa | Hippocampe / NeuroMath | `arena/de272f1c-kurox111` | déclaré livré ; test de la révision distante échoué partiellement ici, voir `DECISIONS.md` |
| UCA-08/09 | Modèle neuronal, mini-transformer, interface et évaluation | branches propriétaires selon issue #1 | branches séparées | poids/checkpoint nécessaires pour reproduction |
| UCA-10 | Refinement réflexif NCM / présentation réponse | équipe multi-agent | branches séparées | architecture déclarée livrée ; intégration retenue suspendue aux gates NCM-01..04 |

## Règles de coordination

- Source de vérité : issue GitHub [#1](https://github.com/timothedenizart-spec/kurox111/issues/1), manifests et handoffs versionnés.
- Confirmer tâche, fichiers, commit, assets/licences, tests prévus et risques avant d'éditer un fichier réservé.
- Garder le pipeline baseline fonctionnel si le NCM est absent, invalide, timeout ou rejeté.
- NCM démarre `off`; shadow seulement après gate, aucune proposition ne remplace la réponse de référence avant évaluation held-out.
- Partager les hashes et manifests des assets ; poids lourds, secrets et données personnelles exclus de Git.
