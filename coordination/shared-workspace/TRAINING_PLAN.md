# Plan d’entraînement UCA — préparation, responsabilités et critères de départ

> **État au 2026-11-15 : entraînement bloqué par prérequis, non par manque de volonté.** Cette branche ne contient aucun checkpoint local, corpus d’entraînement approuvé ni GPU visible. Les seuls JSONL présents sont deux exemples de benchmark (686 octets cumulés), impropres à l’entraînement. Lancer un « entraînement » maintenant créerait un résultat non reproductible ou trompeur.

## Décision du propriétaire et limite matérielle

Le propriétaire a choisi la **continuation de préentraînement** et autorisé un téléchargement explicitement nommé. Il a également choisi le sandbox CPU actuel. Ce choix permet de préparer et de valider la chaîne, mais pas de prétendre entraîner utilement un modèle de langage de taille UCA : la session visible dispose de 2 CPU, ~3.8 GiB RAM et aucun GPU NVIDIA.

La première méthode reste un **adaptateur LoRA réversible**, appliqué à un corpus documentaire approuvé, puis comparé à la baseline gelée. Ne pas préentraîner depuis zéro. Avant tout téléchargement, Cortex et Thalamus doivent inscrire dans le manifeste le checkpoint exact, l’URL ou dépôt source, le commit/version, la licence, le digest attendu et la justification de compatibilité. Aucun téléchargement arbitraire n’est autorisé.

Les voies d’amélioration architecturale (mémoire, vérification, recherche, parallélisme) restent des modules séparés. Elles ne constituent pas un prétexte pour altérer les poids sans benchmark.

## Rôles de l’équipe

| Alias | Mission d’entraînement | Sortie attendue | Ne fait pas |
| --- | --- | --- | --- |
| **Thalamus** — `arena/f2ae664d-kurox111` | gouvernance de run, manifeste, préflight, traçabilité, décision d’acceptation | manifeste validé, registre d’expérience, rapport de comparaison | télécharger ou entraîner des poids sans actifs approuvés |
| **Cortex** — `arena/8e5e2ae2-kurox111` | adaptateur du trainer, chargement local du checkpoint et LoRA | runner local, reprise de run, journal de ressources | modifier le corpus ou déclarer une amélioration sans évaluation |
| **Hippocampe** — `arena/de272f1c-kurox111` | curation de corpus, fiche de données, partitions train/validation/holdout | Data Card, digests, licences, splits disjoints | transmettre des données sensibles ou mélanger le holdout au train |
| **Préfrontal** — `arena/57dad57f-kurox111` | tests cognitifs, régressions et évaluation de sûreté | rapport d’ablation / de non-régression | choisir seul le checkpoint ou écraser la baseline |
| **Intake-Security** — branche à publier | revue du dépôt de fichiers et des frontières d’import | rapport de sécurité et quotas | mettre des poids, secrets ou données personnelles dans Git |

Ces rôles remplacent les alias provisoires antérieurs dans le cadre du chantier d’entraînement. Toute modification de responsabilité est annoncée dans l’issue #1.

## Actifs obligatoires avant un run

1. **Checkpoint local** : chemin, digest SHA-256, architecture, tokenizer associé, licence et autorisation d’usage.
2. **Corpus approuvé** : Data Card, source, licence, politique de données personnelles, digest et format documenté.
3. **Partitions disjointes** : train, validation et holdout par identifiant ; aucun réglage sur le holdout.
4. **Budget** : machine, GPU/VRAM, durée maximale, énergie/coût maximal et stratégie de reprise.
5. **Méthode** : LoRA/QLoRA ou autre méthode annoncée, seed, hyperparamètres, tokenizer, longueur de contexte et prompt template.
6. **Critères de sortie** : métriques automatiques, protocole humain, seuils préenregistrés, tests de sûreté et rollback.

Un lien vers un zip de code, un corpus sans licence, une URL distante ou une sortie de modèle ne remplace aucun de ces actifs.

## Parcours en quatre phases

### T0 — Préflight reproductible

Thalamus valide `training/manifest.example.json` adapté au run réel : tous les chemins doivent être locaux, les digests valides, les partitions distinctes et les budgets positifs. Le préflight ne lance aucun modèle.

### T1 — Smoke test minuscule

Cortex lance un test sur un jeu synthétique sans données personnelles : chargement, une ou quelques itérations, sauvegarde d’adaptateur, reprise et inférence. But : vérifier le pipeline, pas améliorer la qualité.

### T2 — Fine-tuning contrôlé

Après validation T1 et revue de la Data Card, un LoRA/QLoRA local est exécuté avec logs de seed, métriques validation, mémoire, durée et checkpoints temporaires dans `runs/` (ignoré par Git). Les poids de base restent immuables.

### T3 — Évaluation et décision

Préfrontal exécute benchmark, épreuves de régression cognitive, robustesse et revue humaine aveugle. Thalamus enregistre baseline/intervention avec `ExperimentRegistry`. L’adaptateur n’est candidat que si les seuils préenregistrés sont atteints sans régression de sûreté ou de provenance.

## Arborescence locale, non versionnée pour les actifs

```text
models/<checkpoint>/                 # poids et tokenizer locaux, ignorés par Git
training-data/<dataset>/             # corpus local approuvé, à ajouter au .gitignore si créé
runs/<run-id>/                       # sorties, journaux et adaptateurs, ignorés par Git
training/manifests/<run-id>.json     # manifestes versionnables sans secrets
```

Ne commitez jamais les poids, les corpus bruts, tokens, identifiants ou sorties contenant des données personnelles.

## Conditions d’arrêt immédiat

- licence, consentement, provenance ou digest manquant ;
- chevauchement détecté entre entraînement et holdout ;
- matériel insuffisant pour le budget demandé ;
- fuite de données, secret dans un log ou comportement manifestement dangereux ;
- métriques nulles, non comparables ou régression au-delà des seuils.

## Actif exact encore requis

La stratégie est désormais choisie, mais les sources restent à nommer. Indiquer le checkpoint exact et le corpus documentaire autorisé (dépôt/URL, révision, licence et digest si disponible). Sans ces identifiants, l’équipe peut livrer le préflight et les tests CPU, mais ne doit pas sélectionner arbitrairement ni simuler un entraînement réel.