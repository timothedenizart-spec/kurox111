# Journal de tests baseline — 2026-11-15

## Exécution

```bash
python -m uca benchmark benchmarks/tasks.example.jsonl \
  --variants 'uca_full,uca_without_retrieval,uca_without_symbolic,uca_without_ncm,uca_without_nanodiff,smollm2_135_alone,smollm2_360_alone,nanodiff_compatible_only'
```

- Révision : `fabca02` au moment du test.
- Jeux de tâches : `benchmarks/tasks.example.jsonl` (deux exemples, **pas** un holdout validé).
- Actifs locaux détectés : aucun checkpoint SmolLM2, aucun runner MeTTa, aucun runner NCM ou nanoDiff validé.

## Résultat

| Variante | Runs | État | Observation |
| --- | ---: | --- | --- |
| `uca_full` | 2 | `completed_with_degradation` | SmolLM2-135M, SmolLM2-360M et MeTTa indisponibles. |
| `uca_without_retrieval` | 2 | `completed_with_degradation` | Même indisponibilité de modèles/faits. |
| `uca_without_symbolic` | 2 | `completed_with_degradation` | SmolLM2 indisponibles. |
| `uca_without_ncm` | 2 | `completed_with_degradation` | NCM n’était pas actif dans la baseline. |
| `uca_without_nanodiff` | 2 | `completed_with_degradation` | nanoDiff n’était pas actif dans la baseline. |
| `smollm2_135_alone` | 2 | `completed_with_degradation` | Checkpoint 135M absent. |
| `smollm2_360_alone` | 2 | `completed_with_degradation` | Checkpoint 360M absent. |
| `nanodiff_compatible_only` | 1 exécuté, 1 ignoré | `completed` / `skipped` | Le seul cas compatible est exécuté sans denoiser activé. |

## Conclusion honnête

Ces exécutions confirment la résilience de dégradation et les chemins d’ablation ; elles ne mesurent **aucune** amélioration d’intelligence, de factualité ou de raisonnement. Les métriques de qualité restent indisponibles faute de modèles, données et évaluateur validés.

Le prochain test qui peut produire une comparaison utile est NCM-04 : B0 baseline, B2 NCM `shadow`, puis éventuellement B3 `gated`, sur un holdout sourcé et une revue humaine aveugle.
