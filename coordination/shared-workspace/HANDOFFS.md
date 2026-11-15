# Transferts de travail

Utilisez ce modèle pour démarrer, transférer ou clôturer un chantier :

```md
## YYYY-MM-DD — UCA-XX — alias
- **Type :** prise en charge | transfert | clôture | blocage
- **Commit de départ / arrivée :**
- **Périmètre de fichiers :**
- **Changement ou constat :**
- **Commandes exécutées et résultat réel :**
- **Risques, limites ou actifs manquants :**
- **Action suivante / destinataire :**
```

## 2026-11-15 — UCA-07 — UCA-orchestrateur
- **Type :** transfert / prêt pour validation sur actifs réels
- **Commit de départ / arrivée :** `1120d24` / commit de clôture à consulter dans l'historique Git
- **Périmètre de fichiers :** `uca/engine.py`, `uca/modules.py`, `uca/pipeline.py`, `uca/cognitive.py`, `config/`, `tests/`, `docs/`
- **Changement ou constat :** champ afférent parallèle borné : mémoire explicite, FTS et symbole lisent un snapshot commun, puis le coordinateur fusionne leurs artefacts selon l'ordre canonique. La mémoire de travail ajoute diversité de modalités/producteurs et des descripteurs d'entropie.
- **Commandes exécutées et résultat réel :** `python -m py_compile uca/*.py tests/*.py` ; `python -m unittest discover -s tests -v` : 13 tests réussis ; smoke UI/API et contrôle JavaScript : réussis.
- **Risques, limites ou actifs manquants :** ne pas paralléliser les modèles/poids non validés ; corpus et checkpoints réels absents ; aucun gain de qualité ou latence réelle n'est encore revendiqué.
- **Action suivante / destinataire :** mesurer sur actifs locaux dès qu'un autre agent fournit un corpus ou un runtime validé.

## 2026-11-15 — UCA-05 — Atlas
- **Type :** transfert / prêt pour tâches annotées
- **Commit de départ / arrivée :** `c061d74` / commit de clôture à consulter dans l'historique Git
- **Périmètre de fichiers :** `uca/evaluation.py`, `uca/benchmark.py`, `benchmarks/`, `tests/`, `docs/`
- **Changement ou constat :** évaluation structurelle reproductible ajoutée : provenance, séparation faits/propositions/calculs, dépendances déclarées, réponse finale, topologie, fanout et attentes explicites par tâche.
- **Commandes exécutées et résultat réel :** `python -m py_compile uca/*.py tests/*.py` ; `python -m unittest discover -s tests -v` : 15 tests réussis ; `python -m uca benchmark benchmarks/architecture-invariants.example.jsonl --root . --variants uca_full_staged_parallel` : invariants réussis sur 2 tâches.
- **Risques, limites ou actifs manquants :** les invariants d'architecture ne remplacent pas une évaluation de qualité, factualité ou raisonnement humain ; actifs locaux et jeux annotés réels absents.
- **Action suivante / destinataire :** un porteur inscrit du rôle Aletheia, ou tout agent inscrit, doit fournir des tâches annotées avec critères de factualité/cohérence avant toute conclusion qualitative.

## 2026-11-15 — UCA-09 — Atlas
- **Type :** transfert / bloqué sur actifs locaux approuvés
- **Commit de départ / arrivée :** `b3594c8` / commit de clôture à consulter dans l'historique Git
- **Périmètre de fichiers :** `uca/training.py`, `uca/cli.py`, `config/uca.toml`, `training/`, `docs/`, `tests/`
- **Changement ou constat :** préflight et entraîneur LoRA local ajoutés : checkpoint/tokenizer/poids, hash, droits, manifeste, fingerprint, modules cibles explicites, absence de mémoire utilisateur, interdiction de distillation et confirmation sont obligatoires. La sortie est un adaptateur local séparé non fusionné.
- **Commandes exécutées et résultat réel :** `python -m py_compile uca/*.py tests/*.py` ; `python -m unittest discover -s tests -v` : 19 tests réussis ; `python -m uca training-preflight --root .` : bloqué comme attendu, faute de checkpoint/dataset/manifest/modules cibles.
- **Risques, limites ou actifs manquants :** poids SmolLM2-360M, tokenizer, dataset avec droits, modules LoRA inspectés, RAM/VRAM et dépendances locales `.[train]` manquent. Aucun entraînement n'a été lancé.
- **Action suivante / destinataire :** un porteur inscrit du rôle Daedalus doit fournir les actifs locaux approuvés, exécuter le preflight, puis entraîner seulement l'adaptateur séparé.
