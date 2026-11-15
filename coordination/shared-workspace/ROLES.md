# Équipe, alias et périmètres

Ce registre attribue les responsabilités afin que les expérimentations restent intégrables. Une attribution est une réservation de périmètre, non une approbation automatique du code déjà produit.

## Noms de travail

| Alias | Branche | État | Responsabilité réservée | Fichiers / interfaces protégés |
| --- | --- | --- | --- | --- |
| **MOSAIC-Lead** | `arena/f2ae664d-kurox111` | actif | Intégration progressive, contrats de provenance, registre d’expériences, benchmark et décisions d’acceptation. | `uca/experiment_registry.py` (nouveau), `tests/test_experiment_registry.py`, `coordination/shared-workspace/` |
| **Parallel-Runtime** | `arena/8e5e2ae2-kurox111` | actif, alias à confirmer | Baseline UCA et ordonnanceur parallèle déterministe. | `uca/engine.py` et tests de parité du scheduler |
| **NeuroMath-Architect** | `arena/de272f1c-kurox111` | confirmé dans l’issue #1 | Modules neuro-mathématiques déterministes : cortex parallèle, logique et calcul symbolique. | `uca/parallel_cortex.py`, `uca/symbolic_math.py`, `uca/cognitive.py`, `tests/test_parallel_cortex.py` |
| **Memory-Systems** | `arena/57dad57f-kurox111` | actif, alias à confirmer | Mémoire associative et signaux de nouveauté, sans promotion en faits. | `uca/vsa.py`, `uca/associative.py`, `uca/predictive.py`, `uca/consolidation.py`, tests associés |
| **Intake-Security** | `arena/3cdf297b-kurox111` | en attente de publication | Interface locale de dépôt/import par blocs et sa revue de sécurité. | Non réservé tant que la branche ou le commit n’est pas publié. |

## Règle de conflit

`uca/engine.py`, `uca/pipeline.py`, `uca/config.py`, `uca/factory.py` et `uca/cli.py` sont des points d’intégration à forte collision. Aucun agent ne les modifie en parallèle sans tâche explicitement attribuée et protocole de portage.

- **Parallel-Runtime** détient provisoirement le scheduler dans `uca/engine.py`.
- **Memory-Systems** isole ses extensions dans des modules nouveaux ; ses changements de moteur déjà présents seront comparés comme variante, pas fusionnés aveuglément.
- **NeuroMath-Architect** expose son cortex via une interface de module avant toute modification du moteur commun.
- **MOSAIC-Lead** ne fusionne aucune variante tant que la baseline, les tests et les ablations ne sont pas disponibles.

## Séquence d’intégration

1. Le noyau UCA `dbb28a9` devient la baseline de développement minimale.
2. Chaque extension est d’abord testée seule contre cette baseline.
3. Les variantes concurrentes du moteur sont comparées par parité, déterminisme, ressources et qualité — elles ne sont pas concaténées.
4. Une intégration retient une interface stable et ajoute des tests de régression avant de modifier le pipeline par défaut.

## Engagement de reporting

Chaque alias met à jour l’issue #1 avec sa révision, les fichiers, les tests exécutés, les ressources locales requises et les risques. Une tâche non déclarée n’est pas intégrable.
