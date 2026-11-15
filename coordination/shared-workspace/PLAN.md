# Plan inter-agents UCA — établi 2026-11-15 (Préfrontal), approuvé par le propriétaire du dépôt

Canal de synchronisation : **issue #1**. Registre : `contacts/AGENT_REGISTRY.md`.
Règle cardinale : toute « amélioration » doit être **mesurée** (sonde, contrat ou
calibration) avant d'être revendiquée — sinon elle reste une hypothèse étiquetée.

## Où nous en sommes (vérifié)

| Briques | État mesuré |
|---|---|
| Moteur + 15 modules, contrôle cognitif, arithmétique exacte | 49/49 tests verts |
| Contrats cognitifs (comportements réglementaires) | 9/9 verts |
| Laboratoire de sondes (mesures d'amélioration) | 8/8 solides |
| Extensions : VSA/HRR, Hopfield, surprisal, consolidation, moteur parallèle | livrées, testées |
| Micro-débruiteur entraîné localement (44 460 param.) | entraîné ; calibration honnête : **non validé** |
| Interface autonome un fichier + prévisualisations | livrée |
| **Raffineur conceptuel NCM-local relié à la réflexion** | **livré (UCA-13)** |

## Améliorations identifiées par les tests (mesures à l'appui)

| Constat mesuré | Action | Statut |
|---|---|---|
| Extracteur arithmétique perdait « ( » : `calcule (2+3)×7` → `2+3)*7` | rééquilibrage des parenthèses + test de régression | **corrigé** |
| Sonde surprisal mal étalonnée (fond fixe ≠ module réel) | sonde réalignée sur `corpus_background` | **corrigé** |
| Marge de discrimination VSA mesurée par dimension (dim 64 < 2048) | dimension adaptative + cleanup Hopfield à marge faible | **ouvert (UCA-14)** |
| Calibration nanoDiff négative (delta −0,099) | le micro-modèle reste hors pipeline ; itérer après corpus plus grand | ouvert (UCA-10 puis recalibration) |

## Feuille de route par agent

### Préfrontal (cette session) — en cours
- ~~UCA-13~~ raffineur NCM-local relié au système de réflexion **✅**
- Laboratoire de sondes permanent (`python -m uca probes`) ✅ → rejoué à chaque chantier
- UCA-14 : dimension VSA adaptative selon la masse de faits + attracteur Hopfield de nettoyage à marge faible

### Cortex (`arena/8e5e2ae2-kurox111`) — proposé, confirmation attendue
- UCA-03 : checkpoints SmolLM2 (la vraie montée en échelle du raisonnement par modèles)
- revue du raffineur (fichier `uca/refiner.py`) et du contrat REFINEMENT

### Hippocampe (`arena/de272f1c-kurox111`) — proposé, confirmation attendue
- UCA-10 : corpus français étendu avec provenance (cible : recalibration nanoDiff)
- UCA-01 : import FTS5 contrôlé (débloque la corroboration documentaire mesurable)

### Thalamus (`arena/f2ae664d-kurox111`) — proposé, confirmation attendue
- UCA-08 : choix de la branche de référence d'intégration
- UCA-11 : gouvernance d'activation (seuils de calibration, revue croisée)

## Cadence proposée
1. Toute session démarre par `python -m uca probes` + `eval-cognitive` (mesures datées dans `results/`).
2. Une amélioration = un chantier + une mesure avant/après + tests verts.
3. Décisions append-only dans `DECISIONS.md` ; transferts dans `HANDOFFS.md`.
