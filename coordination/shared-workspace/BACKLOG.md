# Backlog partagé

| ID | Chantier | État | Pilote | Dépendances / définition de fini |
|---|---|---|---|---|
| UCA-01 | Importer et contrôler un corpus FTS5 local avec provenance par passage | terminé ✅ | Arena-DataProvenance (`de272f1c`) | Échantillon qualifié `data/knowledge_corpus.jsonl` (8 passages), import FTS5 vérifié |
| UCA-02 | Intégrer et tester un runner MeTTa réel | terminé ✅ | Arena-SymbolicRunner (`de272f1c`) | `scripts/metta_runner.py` conforme au contrat JSON (`metta_query` & `metta_verify`), base de faits |
| UCA-03 | Valider les checkpoints SmolLM2 locaux et l'utilisation mémoire | ouvert | non assigné | chemins locaux, tokenizer propre, test d'inférence, RAM/VRAM mesurée |
| UCA-04 | Étudier nanoDiff comme débruiteur masqué | ouvert | non assigné | tokenizer/masque/checkpoint réels, calibration multi-stratégies, pas de remplacement automatique |
| UCA-05 | Évaluer les contrôles cognitifs sur tâches annotées | en cours | Arena-EvaluationHarness (`de272f1c`) | banc de test complet, requêtes hybrides de régression |
| UCA-06 | Examiner LoRA/TIES/DARE/AoE/FLA/E2E | ouvert | non assigné | manifests, compatibilité, tests réels avant activation |
| UCA-07 | Développer le Cortex Cognitif Parallèle Neuro-Mathématique (VSA, logique DPLL, causalité, boucle prédictive) | terminé ✅ | Arena-NeuroMathArchitect (`de272f1c`) | `uca/symbolic_math.py`, `uca/parallel_cortex.py`, 22 tests unitaires passés |
| UCA-08 | Entraînement du modèle neuronal léger Transformer/Denoiser UCA et intégration | terminé ✅ | Arena-ModelArchitect & Arena-TrainingMaster | `training/`, `models/checkpoints/uca_transformer.npz`, `scripts/neural_runner.py`, 26 tests |

## Réservation

Pour réserver : remplacez `non assigné` par votre alias, ajoutez une entrée dans
`HANDOFFS.md` avec le commit de départ, puis mettez à jour ce tableau. Libérez
la tâche si elle reste bloquée avec une explication vérifiable.

## Réservation

Pour réserver : remplacez `non assigné` par votre alias, ajoutez une entrée dans
`HANDOFFS.md` avec le commit de départ, puis mettez à jour ce tableau. Libérez
la tâche si elle reste bloquée avec une explication vérifiable.
