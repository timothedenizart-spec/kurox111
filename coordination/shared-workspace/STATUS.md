# État partagé

**Mis à jour :** 2026-11-15 UTC

**Base de coordination :** commit `dbb28a9` (`Add bounded cognitive control and exact reasoning`)

## Fonctionnel dans le dépôt

- orchestration UCA séquentielle, traçable et dégradable ;
- mémoire explicite JSON, SQLite FTS5, passerelle MeTTa configurable ;
- format d'artefacts avec provenance, incertitude et séparation faits/propositions/calculs ;
- contrôle cognitif déterministe : mémoire de travail bornée, graphe d'évidence,
  registre de conflits, signal de manque d'ancrage et calcul rationnel exact ;
- champ afférent parallèle borné : mémoire/FTS/symbole isolés par snapshot puis
  fusionnés de façon canonique avant les étapes délibératives ;
- interface locale, tests, benchmark reproductible et évaluation structurelle
  séparée des mesures de qualité de réponse ;
- préflight d'entraînement LoRA local avec manifeste, provenance, hash et
  confirmations ; aucun entraînement lancé sans actifs approuvés.

## Actifs non fournis dans le dépôt

- checkpoints nanoDiff, SmolLM2 et NCM ;
- runner MeTTa/Hyperon validé ;
- base réelle de 50 faits opérateurs ;
- shard Wikipédia français et index FTS de 206 846 passages ;
- artefacts LoRA/TIES/DARE/AoE/FLA/E2E validés.

Ces absences doivent rester visibles comme `unavailable` ou `non_validated`.
