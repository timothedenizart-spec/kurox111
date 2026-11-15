# Programme d'entraînement — UCA

**État immédiat : BLOQUÉ — aucun entraînement n'a commencé.** Le dépôt ne contient aucun checkpoint local ni dataset d'entraînement prêt à l'emploi. Les chemins SmolLM2 sont vides dans `config/uca.toml`; le stockage de fichiers partagé ne contient aucun poids ni données reçues. Dans cet environnement, `torch` n'est pas installé et aucun GPU n'est détecté. Les exemples de bibliothèques (E2E, FLA, Hyperon, nanoDiff, NCM, Scallop) sont du code source potentiel, pas des poids ou un corpus supervisé.

Ne pas prétendre entraîner un modèle sans base, données, matériel, métriques et traces de sortie. Le premier but est un **adaptateur local LoRA reproductible**, uniquement après préflight, plutôt qu'un réentraînement complet d'un modèle de fondation. Le checkpoint cible (135M/360M ou autre) reste à décider à partir des poids réellement fournis et de la mémoire disponible.

## Conditions de démarrage (gates bloquants)

1. **Cible** : propriétaire confirme le checkpoint local exact, tâche visée, langue(s), format de sortie et ce qui est interdit au modèle.
2. **Droits et provenance** : chaque exemple a une source et une licence compatibles ; aucun corpus de droits inconnus ni donnée personnelle/secrète sans base et accord explicites.
3. **Qualité** : données JSONL conformes au schéma décrit dans `DATA_SPEC.md`; doublons et contamination inter-splits absents ; revue humaine d'un échantillon.
4. **Partitions** : `train`, `validation` et `test` séparés par source / document / auteur quand possible, et test gelé avant toute sélection d'hyperparamètres.
5. **Préflight** : checkpoint chargé en local sans réseau ; versions, accélérateur, mémoire, espace disque et commandes enregistrés. `torch`/Transformers/PEFT doivent être installés explicitement. Aucun poids n'est téléchargé par le projet.
6. **Baseline** : mesure du checkpoint non adapté sur le test tenu à l'écart, tâche par tâche et avec coût/latence.
7. **Entraînement** : adapter léger par défaut (LoRA), graine et hyperparamètres fixés, journal et artefacts sauvegardés dans `runs/` (ignoré par Git). Ne pas écraser le modèle source.
8. **Évaluation** : comparer base vs adaptateur sur validation puis test gelé ; exactitude ciblée, abstention, erreurs de faits, régression sécurité, latence et empreinte mémoire. Évaluation humaine en aveugle pour qualité ouverte.
9. **Promotion** : publier le manifest, sommes de contrôle, commandes, métriques et limites ; l'adaptateur reste désactivé tant que les critères convenus ne sont pas atteints.

## Répartition pour organiser l'entraînement

Affectations proposées dans l'issue #1 ; chaque propriétaire doit confirmer avant d'agir. Les branches sont isolées, aucun entraînement partagé ne peut commencer sans confirmation et transfert traçable.

| Rôle / session | Lot | Livrable |
|---|---|---|
| **Thalamus / MOSAIC-Lead** — `arena/f2ae664d-kurox111` | coordination, baseline et protocole | objectif/metrics fixés, manifest d'expérience et décision de promotion |
| **Cortex / Parallel-Runtime** — `arena/8e5e2ae2-kurox111` | entraînement/runner de modèle local | préflight et adaptation LoRA reproductible, seulement après checkpoint et corpus validés |
| **Hippocampe / NeuroMath-Architect** — `arena/de272f1c-kurox111` | exemples raisonnement formel | jeux synthétiques vérifiés, séparation train/test par règle/générateur, tests de fuite |
| **Préfrontal / Memory-Systems** — `arena/57dad57f-kurox111` | tâches mémoire / rappels | évaluation dédiée mémoire, séparation stricte entre mémoire runtime et poids appris |
| **Intake-Security** — `arena/3cdf297b-kurox111` | ingestion / validation des assets | inventaire, validation JSONL, provenance/licences et absence de secrets avant passage au runner |

Le statut de chaque lot est marqué non confirmé tant que la session n'a pas répondu. Éviter de partager `uca/engine.py` ou d'autres fichiers déjà réservés sans accord.

## Comment fournir les fichiers

Utiliser l'interface de dépôt de fichiers sur le port 8765 pour déposer un dossier contenant les fichiers (arborescence conservée) :

- `checkpoint/` : checkpoint complet local, tokenizer et configuration, si le propriétaire possède les droits de partage ;
- `training.jsonl` : exemples conformes à `DATA_SPEC.md` ;
- `manifest.json` : source, licence, dates, transformations, sha256 et responsable ;
- README indiquant la tâche ciblée et les critères de réussite.

Le dépôt de fichiers est local au serveur et ignoré par Git. Signaler ensuite dans l'issue #1 le nom/chemin de dossier reçu et l'empreinte des fichiers, jamais des identifiants sensibles. Ne pas déplacer de poids massifs dans Git.
