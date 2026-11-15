# Programme de recherche et d’implémentation : intelligence mesurée, pas proclamée

## Cadre

La demande d’une IA « extrêmement intelligente » est une ambition, non un critère d’acceptation. Ce programme transforme cette ambition en hypothèses testables. Une capacité n’est considérée comme améliorée que si elle dépasse une baseline préservant sécurité, traçabilité, latence et coût dans un protocole reproductible.

Le point de départ technique candidat est l’UCA observée sur `arena/8e5e2ae2-kurox111` et `arena/de272f1c-kurox111`. Son intégration dans cette branche reste bloquée jusqu’à ce que la propriété, la révision de référence et les travaux concurrents soient confirmés dans l’issue #1.

## Questions de recherche

| ID | Hypothèse falsifiable | Intervention | Mesure principale | Échec / arrêt |
| --- | --- | --- | --- | --- |
| H1 | Le routage vers un noyau exact réduit les erreurs arithmétiques sans augmenter les affirmations factuelles injustifiées. | Calcul typé et vérificateur de résultat. | Exactitude mathématique, erreurs de périmètre. | Régression factuelle ou échecs de sécurité. |
| H2 | Une récupération avec provenance et vérification améliore la justesse des réponses sourcées face à la génération seule. | Retrieval + vérificateur indépendant. | Précision/recall des citations, jugement humain aveugle. | Citations décoratives ou non étayantes. |
| H3 | Des voies génératives indépendantes plus un arbitre fondé sur l’évidence réduisent les erreurs répétées. | Panel de candidats + conflit/critique. | Taux d’erreur commun, calibration. | « Vote majoritaire » remplace l’évidence. |
| H4 | La recherche à temps d’inférence améliore les tâches de planification vérifiables sous budget fixe. | Plan/program search borné. | Taux de réussite, nœuds explorés, temps. | Coût disproportionné ou non reproductibilité. |
| H5 | Un workspace borné avec mémoire explicite diminue les erreurs de contexte et les fuites de mémoire. | Graphe d’évidence, consolidation opt-in. | Rappel contextualisé, tests de consentement. | Écriture implicite ou confusion de provenance. |
| H6 | Le parallélisme par DAG réduit la latence de bout en bout sans modifier le résultat déterministe. | Super-étapes et réduction stable. | Latence p50/p95, égalité de traces. | Course, artefacts non déterministes, dépassement ressource. |

## Lots de travail

### WP0 — Gouvernance, source de vérité et sécurité des données

**Sorties :** propriétaire par sous-système, manifeste d’actifs locaux, modèle de menace, politique de secrets, règles de mémoire/consentement et schéma de versions.

**Condition de départ :** chaque agent déclare son périmètre dans l’issue #1. Toute interface d’import/téléversement est revue avant emploi : limites de taille, listes de chemins sûres, authentification locale, prévention de traversal, quotas et absence de secrets dans l’inbox.

### WP1 — Baseline reproductible

**Sorties :** environnement verrouillé, tests unitaires/intégration, tâches JSONL versionnées, métriques, rapport de baseline.

**Règles :**
- séparer développement, validation, test et holdout ;
- conserver seed, matériel, versions de modèle et configuration ;
- enregistrer coût, mémoire, GPU, latence et erreurs ;
- ne jamais remplir une métrique inconnue par une estimation favorable.

### WP2 — Contrat d’artefacts et noyaux déterministes

**Sorties :** schémas versionnés, validateurs, réducteur déterministe, arithmétique/unité/logique à périmètre restreint, tests adversariaux.

**Priorité :** un petit nombre de preuves exactes traçables vaut mieux qu’un raisonnement général non vérifiable. Toute extension formelle doit déclarer les hypothèses et les limites de son solveur.

### WP3 — Exécution parallèle sûre

**Sorties :** planificateur DAG, budgets, sous-processus isolés, annulation, journal de décision et mode séquentiel de référence.

**Garde-fous :** aucune parallélisation d’effets de bord ; résultats fusionnés dans un ordre stable ; test de déterminisme sur répétitions ; dépassement de délai traité comme résultat isolé, non comme réponse partielle fiable.

### WP4 — Mémoire et récupération ancrées

**Sorties :** stores épisodique/sémantique séparés, index versionné, filtre de consentement, politiques de rétention, évaluateur de citation et suppression vérifiable.

**Expériences :** comparer sans mémoire, mémoire explicite seulement, retrieval seul, retrieval + vérification. Mesurer séparément pertinence, provenance et confidentialité.

### WP5 — Raisonnement, recherche et monde causal (expérimental)

**Sorties :** protocole de planification, recherche de programmes/outils, critiques indépendantes, connecteur de graphe causal optionnel.

Le « modèle du monde » reste une hypothèse à tester sur des environnements où les interventions ont un ground truth. Il ne doit pas être présenté comme une compréhension générale du monde à partir de texte seul.

### WP6 — Évaluation, robustesse et déploiement progressif

**Sorties :** dashboard de métriques, ablations, red-team, revues humaines aveugles, seuils d’intégration et rollback.

**Axes :** factualité avec source, raisonnement mathématique, planification, multilingue, résistance aux instructions adversariales, confidentialité, biais, coût et disponibilité. Une hausse sur un benchmark isolé ne suffit pas.

## Architecture de benchmark

Chaque expérimentation produit un enregistrement comparable :

```json
{
  "experiment_id": "wp3-dag-v1",
  "code_revision": "<git-sha>",
  "config_digest": "<sha256>",
  "assets": [{"id": "local-corpus-v1", "digest": "...", "license": "..."}],
  "baseline": "uca-sequential-v1",
  "intervention": "dag-parallel-v1",
  "task_split": "holdout-v1",
  "metrics": {"quality": null, "calibration": null, "p95_latency_ms": null, "peak_memory": null},
  "ablations": [],
  "failures": [],
  "review": {"human_protocol": "...", "status": "pending"}
}
```

Les `null` restent des `null` tant qu’aucun instrument ou annotation valide ne les renseigne.

## Critères d’intégration

Une intervention peut passer de `expérimental` à `candidate` seulement si :

1. ses interfaces et actifs sont déclarés ;
2. les tests fonctionnels, sécurité et régression passent ;
3. les comparaisons utilisent une baseline et des ablations pertinentes ;
4. le gain est mesuré sur une partition non utilisée pour le réglage ;
5. aucune régression au-delà des seuils préenregistrés n’est observée ;
6. un rollback et un rapport de limites sont disponibles.

## Ordre d’exécution proposé

| Ordre | Travail | Dépendance | Décision de passage |
| ---: | --- | --- | --- |
| 0 | Confirmer les branches, propriétaires et l’interface de dépôt annoncée. | Réponses issue #1 | Source de vérité validée. |
| 1 | Importer ou référencer proprement la baseline UCA choisie. | 0 | Tests baseline verts. |
| 2 | Formaliser les schémas et tests de provenance. | 1 | Aucun artefact ambigu ne traverse la frontière. |
| 3 | Ajouter le DAG parallèle en mode opt-in. | 2 | Traces identiques au séquentiel à modules déterministes. |
| 4 | Ajouter noyaux exacts et vérification ciblée. | 2 | Gains H1/H2 validés. |
| 5 | Ajouter recherche/planning et contrôle budgétaire. | 3, 4 | Gains H4 sans coût inacceptable. |
| 6 | Explorer mémoire consolidée et modèles causaux. | 2, garde-fous de confidentialité | Confidentialité et qualité validées séparément. |

## Ce qui est explicitement hors périmètre initial

- réentraîner massivement un modèle ou annoncer une AGI ;
- auto-modification de code, poids, politiques ou mémoire en production ;
- télécharger des modèles/données sans provenance, licence et approbation ;
- utiliser une sortie de modèle comme preuve de validation de ce même modèle ;
- confondre une métaphore du cerveau avec une validation scientifique.
