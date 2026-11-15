# État partagé

**Mis à jour :** 2026-11-15 UTC

**Base de coordination :** commit `dbb28a9` (`Add bounded cognitive control and exact reasoning`)

## Fonctionnel dans le dépôt

- orchestration UCA séquentielle, traçable et dégradable ;
- mémoire explicite JSON opérationnelle ;
- index SQLite FTS5 opérationnel avec corpus certifié (`data/knowledge_corpus.jsonl`, 8 passages vérifiés) ;
- passerelle MeTTa/Hyperon fonctionnelle via runner JSON conforme (`scripts/metta_runner.py`) et base certifiée (`data/operator_facts.json`) ;
- format d'artefacts avec provenance, incertitude et séparation faits/propositions/calculs ;
- contrôle cognitif déterministe : mémoire de travail bornée, graphe d'évidence, registre de conflits et calcul exact ;
- Cortex Cognitif Parallèle Neuro-Mathématique (UCA-07) : algèbre rationnelle et équations, logique formelle déductive (Horn), graphes de causalité structurelle de Pearl, calcul hyperdimensionnel VSA et boucle prédictive Fristonienne ;
- Modèle neuronal Transformer/Denoiser entraîné localement (UCA-08) : architecture native NumPy, 35 époques, perte réduite de -83.21% (6.25 -> 1.05), précision masquée 96.34%, checkpoint sauvegardé dans `models/checkpoints/` et runner opérationnel pour `models.ncm` ;
- interface locale, 26 tests unitaires validés (1.29s) et benchmark reproductible.

## Actifs non fournis dans le dépôt

- checkpoints nanoDiff, SmolLM2 et NCM (restent en chargement différé / désactivés conformément aux promesses de conception) ;
- shard Wikipédia massif (le corpus local certifié fournit la base documentaire vérifiée) ;
- artefacts LoRA/TIES/DARE/AoE/FLA/E2E validés.

Ces absences doivent rester visibles comme `unavailable` ou `non_validated`.
