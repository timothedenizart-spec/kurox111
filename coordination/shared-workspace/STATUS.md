# État partagé

**Mis à jour :** 2026-11-15 UTC

**Base de coordination :** commit `c2c85cb` (`Add one-file local UCA launcher`) ;
UCA-11 est validé structurellement et attend un runner NCM réel avant toute
activation.

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
  confirmations ; aucun entraînement lancé sans actifs approuvés ;
- lanceur local `Lancer_UCA.py` : sélection de port libre, statut transparent
  des modules, ouverture demandée au navigateur par défaut et interface servie
  localement ; les actifs absents restent indisponibles plutôt que simulés ;
- affinement NCM de contrôle : contrat `reasoning_refinement` textuel relié au
  dossier GlobalWorkspace et à la vérification indépendante ; il est désactivé
  et non activable sans validation distincte du runner, et ne promeut jamais
  une proposition au rang de fait.

## Actifs non fournis dans le dépôt

- checkpoints nanoDiff, SmolLM2 et NCM ;
- runner MeTTa/Hyperon validé ;
- base réelle de 50 faits opérateurs ;
- shard Wikipédia français et index FTS de 206 846 passages ;
- artefacts LoRA/TIES/DARE/AoE/FLA/E2E validés.

Ces absences doivent rester visibles comme `unavailable` ou `non_validated`.
