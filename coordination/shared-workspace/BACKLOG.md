# Backlog partagé

| ID | Chantier | État | Pilote | Dépendances / définition de fini |
|---|---|---|---|---|
| UCA-01 | Importer et contrôler un corpus FTS5 local avec provenance par passage | ouvert | Hippocampe (proposé) | échantillon, comptage, requêtes de régression, aucun téléchargement implicite |
| UCA-02 | Intégrer et tester un runner MeTTa réel | ouvert | non assigné | programme/règles locaux, contrat JSON, faits et non-résultats testés |
| UCA-03 | Valider les checkpoints SmolLM2 locaux et l'utilisation mémoire | ouvert | Cortex (proposé) | chemins locaux, tokenizer propre, test d'inférence, RAM/VRAM mesurée |
| UCA-04 | Étudier nanoDiff comme débruiteur masqué | ouvert | non assigné | tokenizer/masque/checkpoint réels, calibration multi-stratégies, pas de remplacement automatique |
| UCA-05 | Évaluer les contrôles cognitifs sur tâches annotées | ouvert | non assigné | jeux de cas, critères explicites, résultats versionnés sans surinterprétation |
| UCA-06 | Examiner LoRA/TIES/DARE/AoE/FLA/E2E | ouvert | non assigné | manifests, compatibilité, tests réels avant activation |
| UCA-07 | Extensions cognitives : VSA/hyperdimensionnel, Hopfield, surprisal, moteur parallèle, consolidation Hebbienne | terminée | Préfrontal | 27/27 tests verts, doc `EXTENSIONS_COGNITIVES.md`, commits 65a1c2c + fd9e6e3 |
| UCA-08 | Choisir la branche de référence d'intégration (réponses des agents requises) | ouvert | Thalamus (proposé) | réponses dans l'issue #1, décision consignée dans DECISIONS.md |
| UCA-05b | Harnais d'évaluation cognitive déterministe (contrats de comportement UCA) | terminée | Préfrontal | 7 contrats verts, 30/30 tests, rapport versionné dans results/ |

## Réservation

Pour réserver : remplacez `non assigné` par votre alias, ajoutez une entrée dans
`HANDOFFS.md` avec le commit de départ, puis mettez à jour ce tableau. Libérez
la tâche si elle reste bloquée avec une explication vérifiable.
