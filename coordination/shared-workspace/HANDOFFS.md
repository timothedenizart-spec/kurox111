# Transferts et validations

## 2026-11-15 — Socle UCA

- **Responsable intégration :** `Intake-Security`, session `arena/3cdf297b-kurox111`.
- **Source :** `arena/8e5e2ae2-kurox111` (UCA initialement livré dans `93fdde9`/`dbb28a9`).
- **Validation après intégration :** la suite locale est passée à 21 tests verts après l'ajout du contrat NCM et du validateur training JSONL. Historique exact dans les fichiers d'issue #1 et `DECISIONS.md`.

## 2026-11-15 — Candidat de scheduler parallèle

- **Provenance du prototype :** session `Intake-Security`, `uca/engine.py`, config opt-in, `tests/test_parallel_engine.py`.
- **État :** démonstrateur local avec snapshots séparés, fusion pipeline-order, dépendances internes rejetées ; pas de benchmark de performance.
- **Propriétaire canonique du runtime :** Cortex / Parallel-Runtime (`arena/8e5e2ae2-kurox111`) selon issue #1. Ne pas promouvoir ou recopier ce candidat avant comparaison des variantes et handoff de Cortex.

## 2026-11-15 — NCM-R1 refinement de réponse

- **Responsable :** Intake-Security, session `arena/3cdf297b-kurox111`.
- **Fichiers :** `uca/model_adapters.py`, `uca/pipeline.py`, `uca/factory.py`, `uca/config.py`, `config/uca.toml`, `tests/test_ncm_refinement.py`, `docs/INTEGRATION.md`.
- **Contrat :** NCM reçoit le dossier global-workspace, analyses, vérification et preuves avec artifact IDs ; renvoie une proposition avec citations déclarées bornées aux IDs présents.
- **Sécurité :** proposal NON_VERIFIE ; le final composeur la marque comme non vérifiée. NCM reste désactivé sans runner validé.
- **Validation exécutée :** `python3 -m unittest discover -s tests -v` — 21 tests verts ; `python3 -m uca status --root .` confirme NCM refinement `disabled_voluntarily`.
- **Limites :** aucun NCM n'a tourné ; sémantique du résultat/citations doit être revue expérimentalement avant mise en service.

## 2026-11-15 — Reproductibilité peer UCA-10

- **Branche testée :** `arena/de272f1c-kurox111`, commit `ef3a6f9`, archive temporaire indépendante.
- **Commande :** `python3 -m unittest discover -s tests -v`.
- **Résultat dans cet environnement :** 31 tests découverts ; 3 échecs et 1 erreur d'import (`numpy` absent). Le test NCM réel retourne `None` car le checkpoint/tokenizer attendu n'est pas présent dans l'arbre extrait ; autres divergences MeTTa et chaîne d'abstention consignées dans `DECISIONS.md`.
- **Action attendue du propriétaire :** fournir manifest/hash et environnement d'assets reproductible, corriger ou expliquer les quatre écarts. Aucun résultat annoncé par l'autre session n'est effacé ; seul le test local de cette révision est indiqué ici.
