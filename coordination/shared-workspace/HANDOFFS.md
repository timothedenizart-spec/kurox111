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

## 2026-11-15 — UCA-07 — Cognition-avancée (`arena/57dad57f-kurox111`)

- **Type :** prise en charge
- **Commit de départ / arrivée :** merge tracé d'`arena/8e5e2ae2-kurox111` @ `1120d24` → nouveaux commits sur `arena/57dad57f-kurox111`
- **Périmètre de fichiers :** ajoutés `uca/vsa.py`, `uca/associative.py`, `uca/predictive.py`, `uca/consolidation.py`, `docs/EXTENSIONS_COGNITIVES.md`, `tests/test_advanced_cognition.py` ; modifiés `uca/engine.py`, `uca/pipeline.py`, `uca/config.py`, `uca/factory.py`, `uca/cli.py`, `config/uca.toml`, `README.md`, `docs/ARCHITECTURE.md`
- **Changement ou constat :** mémoire hyperdimensionnelle VSA/HRR (complétion holographique, auto-fidélité, transfert analogique), réseau de Hopfield à capacité honnête, moniteur de surprisal de Shannon, consolidation Hebbienne hors-ligne, moteur parallèle par niveaux contigus (sorties bit-identiques au séquentiel, vérifié par test de parité)
- **Commandes exécutées et résultat réel :** `python3 -m unittest discover -s tests` → 27/27 OK ; démo CLI (init → import FTS5 → consolidate → chat --developer → status avec niveaux) fonctionnelle
- **Risques, limites ou actifs manquants :** bases SmolLM2/MeTTa/nanoDiff toujours indisponibles (statuts honnêtes inchangés) ; `engine.execution_mode = "sequential"` restaure l'ordre historique
- **Action suivante / destinataire :** revue par UCA-orchestrateur ; proposer cette branche comme référence d'intégration dans l'issue #1

## 2026-11-15 — UCA-05b — Préfrontal

- **Type :** prise en charge puis clôture
- **Commit de départ / arrivée :** `fd9e6e3` → commit « cognitive evaluation harness » sur `arena/57dad57f-kurox111`
- **Périmètre de fichiers :** ajoutés `uca/eval_cognition.py`, `benchmarks/cognitive_checks.example.jsonl`, `tests/test_cognitive_eval.py`, `coordination/shared-workspace/results/UCA-05b-cognitive-eval-2026-11-15.json` ; modifiés `uca/cli.py`, `README.md`, `docs/EXTENSIONS_COGNITIVES.md`
- **Changement ou constat :** harnais d'évaluation cognitive déterministe (contrats passé/échoué, fixtures isolées par racine temporaire) ; 7 contrats fournis couvrant arithmétique exacte, absence honnête, mémoire opt-in, conflit symbolique borné, non-promotion des analogies et consolidations
- **Commandes exécutées et résultat réel :** `python3 -m unittest discover -s tests` → 30/30 OK ; `python3 -m uca eval-cognitive benchmarks/cognitive_checks.example.jsonl` → 7/7 cas verts ; rapport versionné joint
- **Risques, limites ou actifs manquants :** aucune métrique de qualité n'est revendiquée ; les cas avec modèles réels exigent UCA-03 (Cortex, proposé)
- **Action suivante / destinataire :** Cortex et Thalamus pour revue ; enrichir les cas annotés après UCA-01 (Hippocampe, proposé)

## 2026-11-15 — UCA-09 — Préfrontal

- **Type :** prise en charge puis clôture
- **Commit de départ / arrivée :** `7cc8854` → commit « local micro-training » sur `arena/57dad57f-kurox111`
- **Périmètre de fichiers :** ajoutés `uca/microtrain.py`, `shims/nanodiff_micro_runner.py`, `config/uca.micro-demo.toml`, `benchmarks/nanodiff-calibration.micro.jsonl`, `tests/test_microtrain.py`, `docs/ENTRAINEMENT.md` ; modifiés `uca/cli.py` (`microtrain`, `--config`), `uca/nanodiff_validation.py` (garde honnête cas vides), `README.md`, backlog/registry/status
- **Changement ou constat :** micro-débruiteur masqué CBOW réellement entraîné sur CPU (numpy), 44 460 paramètres, corpus = docs du dépôt (508 phrases, sha256 `6ef5d7bf8cc87904`) ; CE 6,06 → 1,01 ; perplexité holdout 301,08 vs 1 149,03 unigramme vs 684 uniforme ; restauration 13,1 % ; calibration nanoDiff exécutée en conditions réelles : **mean_delta -0,099 → validated_for_activation=false**, module maintenu `non_validated`
- **Commandes exécutées et résultat réel :** `python3 -m unittest discover -s tests` → 38/38 OK ; `python -m uca microtrain` (reproductible, seed 42) ; `validate-nanodiff --config config/uca.micro-demo.toml` → verdict négatif respecté
- **Risques, limites ou actifs manquants :** micro-échelle assumée (pas un transformer) ; artefacts modèle gitignorés sous `models/` ; activation finale = revue humaine (UCA-11, proposé Cortex+Thalamus)
- **Action suivante / destinataire :** Hippocampe pour UCA-10 (extension corpus) ; Cortex pour UCA-03 (vrais checkpoints)

## 2026-11-15 — UCA-12 — Préfrontal

- **Type :** prise en charge puis clôture
- **Commit de départ / arrivée :** `6172105` → commit « single-file interface » sur `arena/57dad57f-kurox111`
- **Périmètre de fichiers :** ajoutés `uca/interface.py`, `uca/interface_page.html`, `tests/test_interface.py`, `interface/uca.html` (généré, 22,5 Ko) ; modifiés `uca/cli.py` (sous-commande `interface`), `README.md`
- **Changement ou constat :** un seul fichier HTML qui s'ouvre automatiquement (`python -m uca interface`) avec tout préchargé : état moteur réel (14 modules, niveaux parallèles), 2 démonstrations calculées à la génération, métriques du modèle entraîné, rapport 7/7 contrats cognitifs. Hors-ligne : conversation honnêtement désactivée (jamais simulée) ; console d'arithmétique rationnelle exacte BigInt pleinement fonctionnelle (port fidèle du noyau serveur, 10/10 cas sous node). Servie par `uca serve`, la même page active le chat réel.
- **Commandes exécutées et résultat réel :** `python3 -m unittest discover -s tests` → 42/42 OK ; `curl` local des deux prévisualisations (fichier statique :8091, moteur :8080/chat → `100/8 = 25/2` exact)
- **Risques, limites ou actifs manquants :** l'ouverture automatique exige un environnement avec écran (dégradé honnêtement sinon) ; pas de donnée personnelle dans le fichier
- **Action suivante / destinataire :** Thalamus (proposé) pour revue visuelle ; Cortex si le shell de page doit devenir l'unique UI servie

## 2026-11-15 — UCA-13 — Préfrontal

- **Type :** prise en charge puis clôture ; plan inter-agents établi (voir `PLAN.md`, D-002)
- **Commit de départ / arrivée :** `1f38f78` → commit « NCM-local refiner + probe lab » sur `arena/57dad57f-kurox111`
- **Périmètre de fichiers :** ajoutés `uca/refiner.py`, `uca/probes.py`, `tests/test_refiner_and_probes.py`, `coordination/shared-workspace/PLAN.md`, `results/probe-lab-2026-11-15.json` ; modifiés `uca/types.py` (REFINEMENT), `uca/pipeline.py` (final_response consomme le plan), `uca/cognitive.py` (fix parenthèses mesuré), `uca/config.py`, `config/uca.toml`, `uca/factory.py`, `uca/cli.py` (`probes`), `benchmarks/cognitive_checks.example.jsonl` (9 cas), `README.md`, `docs/EXTENSIONS_COGNITIVES.md`
- **Changement ou constat :** raffineur NCM-local relié au système de réflexion (workspace + vérification + surprisal) : lignes de réflexion, conflits ouverts non arbitrés, limites actives ; laboratoire de sondes mesurées (8 sondes) — deux faiblesses réelles trouvées par les tests et corrigées (extraction parenthésée, étalonnage surprisal), avec régressions
- **Commandes exécutées et résultat réel :** `python3 -m unittest discover -s tests` → **49/49 OK** ; `eval-cognitive` → **9/9** ; `probes` → **8/8 solides** (rapports versionnés dans `results/`)
- **Risques, limites ou actifs manquants :** pas le runner NCM externe (LM1B/VQ reste non validé) ; marge VSA mesurée par dimension → UCA-14 ouvert
- **Action suivante / destinataire :** Cortex (revue raffineur), Thalamus (UCA-08), Hippocampe (UCA-10 corpus) ; annonce du plan dans l'issue #1

_Aucun autre transfert n'est encore enregistré._
