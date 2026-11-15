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

## 2026-11-15 — UCA-10 — Atlas
- **Type :** clôture / prêt à ouvrir localement
- **Commit de départ / arrivée :** `98df609` / commit de clôture à consulter dans l'historique Git
- **Périmètre de fichiers :** `Lancer_UCA.py`, `Lancer_UCA.sh`, `Lancer_UCA.bat`, `uca/launcher.py`, `uca/cli.py`, `tests/test_launcher.py`, `docs/`, `coordination/`
- **Changement ou constat :** l'entrée Python plaçable en double-clic se replace à la racine du dépôt, construit UCA avec les actifs/configuration locaux, choisit un port libre, affiche une métadonnée de disponibilité puis demande l'ouverture du navigateur. Les états des actifs réellement absents restent visibles dans l'UI et ne sont ni téléchargés ni simulés.
- **Commandes exécutées et résultat réel :** `python -m py_compile uca/*.py tests/*.py Lancer_UCA.py` ; `python -m unittest discover -s tests -v` : 22 tests réussis ; smoke de `Lancer_UCA.py --no-browser` depuis un autre répertoire avec `/api/status` : réussi ; smoke `python -m uca launch --root . --no-browser --port 0` : réussi. Le test unitaire intercepte et vérifie l'appel à `webbrowser.open`; aucun navigateur graphique réel n'a été affirmé comme observé.
- **Risques, limites ou actifs manquants :** checkpoints, corpus, runner MeTTa et actifs expérimentaux restent absents et sont déclarés `unavailable`/`non_validated`. Le serveur du lanceur est volontairement lié à `127.0.0.1` par défaut ; utiliser `uca launch --host 0.0.0.0` seulement quand l'opérateur a besoin d'une écoute réseau locale.
- **Action suivante / destinataire :** ouvrir `Lancer_UCA.py` sur la machine opérateur ; ajouter/configurer seulement des actifs locaux autorisés, puis contrôler leur état dans l'interface.

## 2026-11-15 — UCA-11 — Atlas
- **Type :** clôture structurelle / attente d'actifs réels
- **Commit de départ / arrivée :** `c2c85cb` / commit de clôture à consulter dans l'historique Git
- **Périmètre de fichiers :** `uca/model_adapters.py`, `uca/pipeline.py`, `uca/factory.py`, `uca/engine.py`, `uca/evaluation.py`, `uca/benchmark.py`, `config/`, `tests/`, `docs/`, `coordination/`.
- **Changement ou constat :** relance consignée auprès de tous les rôles réservés via le canal versionné ; aucun autre agent ni runner NCM n'est inscrit. L'étape `ncm_reasoning_refinement` reçoit le dossier GlobalWorkspace comme texte/IDs, émet seulement une proposition `NON_VERIFIE`, puis transmet des cibles au vérificateur indépendant. La composition finale peut rapporter cette participation sans injecter le plan NCM comme fait ou réponse de remplacement.
- **Commandes exécutées et résultat réel :** baseline : compilation, 22 tests et benchmark structurel sur deux tâches ; après intégration : `python -m py_compile uca/*.py tests/*.py Lancer_UCA.py` et `python -m unittest discover -s tests -v` : 27 tests réussis ; benchmark `uca_full_staged_parallel,uca_without_ncm` : invariants structurels réussis pour les deux tâches ; statut par défaut : NCM refinement `disabled_voluntarily`. Les tests de shim local couvrent contrat, non-promotion, ancrage indépendant, correction bornée et ablation des deux étapes NCM.
- **Risques, limites ou actifs manquants :** un shim de test ne valide pas NCM ; checkpoints/runners, corpus annoté et mesures humaines restent absents. Aucune amélioration de qualité, factualité ou intelligence n'est déclarée.
- **Action suivante / destinataire :** Daedalus doit fournir un runner NCM local réel et validé (UCA-12) ; Aletheia doit exécuter une ablation annotée (UCA-13) ; Pharos peut améliorer la visualisation après inscription (UCA-14). Toute réponse doit passer par `contacts/INBOX.md`.
