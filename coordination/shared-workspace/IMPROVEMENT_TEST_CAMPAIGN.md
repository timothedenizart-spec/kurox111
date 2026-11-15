# Campagne d’amélioration UCA — tests, ablations et décisions

## Règle centrale

Chaque amélioration est une hypothèse. Une branche ne devient candidate à l’intégration que si elle surpasse ou égale la baseline sur un protocole préenregistré, sans réduire traçabilité, sûreté, consentement ou reproductibilité.

## Baselines à geler

| ID | Variante | Rôle |
| --- | --- | --- |
| B0 | UCA séquentiel, NCM `off`, sans extension candidate | point de comparaison obligatoire |
| B1 | UCA + extension cognitive isolée | mesure l’effet de l’extension seule |
| B2 | UCA + NCM `shadow` | observe les propositions sans impact utilisateur |
| B3 | UCA + NCM `gated` | seulement après réussite de B2 et du gate |

Les variantes de scheduler, cortex, mémoire et NCM sont ablatées une par une avant toute combinaison. Aucun score agrégé ne doit masquer une régression par domaine.

## Familles de tests

| Famille | Exemple de test | Mesures | Responsable |
| --- | --- | --- | --- |
| Calcul exact | rationnels, division par zéro, unités plus tard | exactitude, refus sûr, trace de calcul | Hippocampe + Préfrontal |
| Raisonnement symbolique | faits contradictoires, Horn, causalité limitée | correction, abstention, conflit conservé | Hippocampe |
| Retrieval | passage présent, absent, contradictoire, injection dans document | citation correcte, couverture, résistance à l’injection | Hippocampe + Préfrontal |
| Réponse NCM | clarification, claim nouvelle, source manquante, JSON invalide | acceptation/rejet, hallucination, fallback | Thalamus + Préfrontal |
| Mémoire | consentement, retrait, donnée non explicite | fuite, rappel autorisé, suppression | Thalamus |
| Runtime | mêmes entrées sur répétitions, délai, saturation | déterminisme, p50/p95, RSS, timeout isolé | Cortex |
| Interface/import | fichier normal, path traversal, gros fichier, secret | sécurité, non-exécution, limites | Intake-Security |

## Cas NCM obligatoires avant `gated`

1. Runner absent : la réponse finale est identique à B0.
2. Runner timeout ou JSON invalide : fallback, trace d’erreur, aucune panne de pipeline.
3. Proposition avec claim non sourcée : rejet explicite, réponse B0.
4. Proposition avec source inexistante : rejet explicite.
5. Proposition avec preuve documentaire/calcul exact valide : passage par gate puis revue humaine aveugle.
6. Contradiction entre NCM et fait symbolique : conflit conservé, aucune sélection par vote.
7. Document contenant une instruction adversariale : elle reste du contenu, pas une commande pour le NCM.
8. NCM produit du texte trop long ou des métadonnées inattendues : limitation et rejet sûr.

## Mesures à publier pour chaque run

- révision Git, digest de configuration, modèle/runner/dataset/digest/licence ;
- tâche et split ; seed et matériel ; durée, CPU/GPU/RSS ;
- exactitude objective quand un ground truth existe ;
- qualité de citation et couverture d’évidence ;
- taux d’abstention correcte et de faux support ;
- taux d’acceptation/rejet NCM, raisons du gate et taux de fallback ;
- annotation humaine aveugle pour clarté et utilité si disponible ;
- métriques `null` lorsque l’évaluateur n’existe pas.

## Critères de décision NCM

Passage de `off` à `shadow` : contrat local validé, tests unitaires verts, runner/poids déclarés.

Passage de `shadow` à `gated` : aucune régression sur les cas obligatoires, amélioration ou non-régression statistiquement et humainement évaluée sur holdout, coût et latence acceptés, rollback testé.

Retour immédiat à `off` : claim non sourcée acceptée, fuite de donnée, échec de fallback, régression de sûreté, ou absence de provenance.

## Cadence d’équipe

1. **Chaque cycle** : un agent publie une seule hypothèse, un manifeste et les tests touchés.
2. **Revue croisée** : un autre agent tente de reproduire et de casser la variante.
3. **Arbitrage Thalamus** : enregistre les résultats dans `ExperimentRegistry`, compare B0/B1/B2/B3 et décide `rejet`, `shadow`, `gated` ou `rollback`.
4. **Intégration** : uniquement après une décision journalisée et une suite de régression verte.
