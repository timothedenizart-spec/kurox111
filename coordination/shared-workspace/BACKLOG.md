# Backlog partagé

| ID | Chantier | État | Pilote | Dépendances / définition de fini |
|---|---|---|---|---|
| UCA-01 | Importer et contrôler un corpus FTS5 local avec provenance par passage | ouvert | non assigné | échantillon, comptage, requêtes de régression, aucun téléchargement implicite |
| UCA-02 | Intégrer et tester un runner MeTTa réel | ouvert | non assigné | programme/règles locaux, contrat JSON, faits et non-résultats testés |
| UCA-03 | Valider les checkpoints SmolLM2 locaux et l'utilisation mémoire | ouvert | non assigné | chemins locaux, tokenizer propre, test d'inférence, RAM/VRAM mesurée |
| UCA-04 | Étudier nanoDiff comme débruiteur masqué | ouvert | non assigné | tokenizer/masque/checkpoint réels, calibration multi-stratégies, pas de remplacement automatique |
| UCA-05 | Évaluer les contrôles cognitifs sur tâches annotées | ouvert | non assigné | jeux de cas, critères explicites, résultats versionnés sans surinterprétation |
| UCA-06 | Examiner LoRA/TIES/DARE/AoE/FLA/E2E | ouvert | non assigné | manifests, compatibilité, tests réels avant activation |
| UCA-07 | Valider le champ afférent parallèle et le merge déterministe | prêt pour validation sur actifs réels | UCA-orchestrateur | tests de snapshots isolés terminés ; restent mesures de latence et ablation séquentiel/parallèle sur actifs réels |
| UCA-08 | Concevoir recherche active et délibération multi-modèle bornées | ouvert | non assigné | corpus/modèles validés, budget explicite, arrêt garanti et benchmark annoté |

## Réservation

Pour réserver : remplacez `non assigné` par votre alias, ajoutez une entrée dans
`HANDOFFS.md` avec le commit de départ, puis mettez à jour ce tableau. Libérez
la tâche si elle reste bloquée avec une explication vérifiable.
