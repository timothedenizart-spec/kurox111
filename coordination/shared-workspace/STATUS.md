# État partagé

**Mis à jour :** 2026-11-15 UTC

**Base de coordination :** commit `dbb28a9` (`Add bounded cognitive control and exact reasoning`)

## Fonctionnel dans le dépôt (complément 2026-11-15, branche arena/57dad57f-kurox111)

- moteur d'exécution **parallèle par niveaux topologiques contigus** (déterministe : sorties identiques au séquentiel ; `engine.execution_mode`) ;
- mémoire vectorielle hyperdimensionnelle VSA/HRR : complétion holographique, sonde d'auto-fidélité, transfert analogique pondéré (propositions uniquement) ;
- réseau de Hopfield stdlib avec refus honnête au-delà de 0,15·n motifs ;
- moniteur de surprisal de Shannon sur les preuves locales (signal de vérification, pas verdict) ;
- consolidation Hebbienne hors-ligne (`python -m uca consolidate`), déterministe et sourcée par documents ;
- suite de tests portée à 27 (tous verts, stdlib uniquement).

## Fonctionnel dans le dépôt

- orchestration UCA séquentielle, traçable et dégradable ;
- mémoire explicite JSON, SQLite FTS5, passerelle MeTTa configurable ;
- format d'artefacts avec provenance, incertitude et séparation faits/propositions/calculs ;
- contrôle cognitif déterministe : mémoire de travail bornée, graphe d'évidence,
  registre de conflits, signal de manque d'ancrage et calcul rationnel exact ;
- interface locale, tests et benchmark reproductible.

## Actifs non fournis dans le dépôt

- checkpoints nanoDiff, SmolLM2 et NCM ;
- runner MeTTa/Hyperon validé ;
- base réelle de 50 faits opérateurs ;
- shard Wikipédia français et index FTS de 206 846 passages ;
- artefacts LoRA/TIES/DARE/AoE/FLA/E2E validés.

Ces absences doivent rester visibles comme `unavailable` ou `non_validated`.
