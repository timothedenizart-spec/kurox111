# NCM-REFINE — amélioration finale reliée au raisonnement, sans effacer l’évidence

> **Statut : plan d’intégration et de test.** Un NCM ne devient jamais une source de vérité ni un canal de chaîne de pensée cachée. Il peut proposer une formulation, détecter une incohérence ou demander une vérification ; le graphe de raisonnement, les sources et les vérificateurs conservent l’autorité.

## But mesurable

Améliorer la clarté, la couverture des limites et la fidélité aux preuves de la réponse finale **sans** augmenter les affirmations non étayées. Le succès sera mesuré face à la baseline NCM désactivé, avec une suite holdout et revue humaine aveugle ; il n’est pas présumé.

## Flux cible

```text
requête → récupération / raisonnement / calcul exact → workspace → vérification
                                                          │
                                                   paquet de réflexion borné
                                                          │
                                                  NCM-REFINE (proposition)
                                                          │
                                            gate de claims et de provenance
                                              ├─ refus / NCM indisponible ──► réponse baseline
                                              └─ proposition corroborée ────► composition finale
```

Le paquet transmis au NCM ne contient que : demande normalisée, extraits documentaires avec leurs IDs, faits symboliques, calculs exacts, résultats de vérification, conflits, incertitudes et brouillon de réponse. Il ne contient ni secrets, ni mémoire non consentie, ni représentations token/embedding d’un autre modèle.

## Contrat du runner `ncm_refine_response`

Le runner local reçoit un seul objet JSON sur stdin :

```json
{
  "operation": "ncm_refine_response",
  "contract_version": 1,
  "draft": "…",
  "reflection_packet": {
    "source_artifact_ids": ["…"],
    "exact_computation_artifact_ids": ["…"],
    "verification_artifact_ids": ["…"],
    "unresolved_limits": ["…"]
  }
}
```

Il retourne un unique objet JSON :

```json
{
  "candidate_answer": "…",
  "change_intents": ["clarity", "add_limit"],
  "claims": [
    {"text": "…", "source_artifact_ids": ["…"]}
  ],
  "uncertainties": ["…"],
  "runner_metadata": {"model_id": "…", "checkpoint_digest": "…"}
}
```

Limites de contrat : maximum de taille, JSON strict, IDs d’artefact existants, aucune instruction exécutable, aucun accès réseau ou écriture de mémoire via le runner. Le modèle, tokenizer, checkpoint et calibration sont déclarés dans son manifeste local.

## Gate de réflexion et de provenance

1. Le NCM produit exclusivement un artefact `PROPOSAL` avec statut `NON_VERIFIE`.
2. Toute nouvelle affirmation doit pointer vers des IDs source/calcul/fait existants.
3. Le vérificateur confirme le lien ; une absence de résultat est `inconclusive`, jamais une confirmation.
4. Une proposition sans claim nouveau mais qui améliore seulement la structure reste marquée comme proposition jusqu’à la phase de composition.
5. La réponse baseline est conservée si le runner est absent, invalide, lent, non calibré, ou si une claim échoue le gate.
6. Les données de réflexion visibles sont une trace concise : changement proposé, références, résultat du gate et limites — jamais une chaîne de pensée détaillée.

## Modes de déploiement

| Mode | Effet utilisateur | But |
| --- | --- | --- |
| `off` | Pipeline actuel, bit-identique. | Baseline obligatoire. |
| `shadow` | Le NCM produit une proposition stockée uniquement en trace développeur. | Mesurer qualité, couverture et erreurs sans modifier la réponse. |
| `gated` | Une proposition corroborée peut être prise en compte par le compositeur, sinon fallback. | A/B contrôlé après tests. |
| `disabled_after_regression` | Retour immédiat au baseline. | Rollback sûr. |

Le mode initial est `off`. `shadow` exige un runner validé et un manifeste d’expérience ; `gated` exige les critères d’acceptation du plan de test.

## Répartition ferme

| Agent | Lot | Fichiers / sortie | Condition de passage |
| --- | --- | --- | --- |
| **Thalamus** | NCM-01 contrat, gate de provenance, registre d’expériences et intégration après revue. | `uca/ncm_refinement.py` (nouveau), tests de contrat, rapport d’ablation. | Aucune proposition ne modifie les faits ou ne contourne le fallback. |
| **Cortex** | NCM-02 adaptateur/runner local pour `ncm_refine_response`. | `uca/model_adapters.py`, config et runner uniquement après audit. | Mode `shadow`, timeout, JSON/schema et checkpoint déclarés. |
| **Hippocampe** | NCM-03 corpus et jeux d’épreuves sourcés. | Data Card, splits, cas avec preuves contradictoires/absentes. | Licences, digests et partitions vérifiés. |
| **Préfrontal** | NCM-04 évaluation et red-team. | tests injection, abstention, factualité, clarté, coût. | Comparaison aveugle versus baseline et non-régression. |
| **Intake-Security** | NCM-05 revue de l’import de poids/données. | limites upload, scan, chemins, secrets, quotas. | Rapport de sécurité publié avant import. |

## Ce qui ne doit pas être fait

- ne pas remplacer directement la réponse finale par la sortie NCM ;
- ne pas appeler une sortie NCM « fait », « preuve » ou « calibration » sans protocole ;
- ne pas entraînner/importer le zip NCM sans licence, digest et revue de code ;
- ne pas utiliser le NCM pour masquer une réponse non sourcée ou contourner l’abstention ;
- ne pas confondre baisse de loss d’un micro-modèle avec amélioration générale de l’IA.
