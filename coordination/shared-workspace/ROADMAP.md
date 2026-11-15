# UCA — plan multi-agent pour améliorer les capacités

État : **proposition de recherche et d'ingénierie**, pas de résultat de performance revendiqué. La ressemblance avec un concept du cerveau ne démontre ni intelligence générale ni conscience. Les expériences doivent pouvoir réfuter les idées.

## Cible d'architecture : workspace cognitif parallèle (WCP)

Conserver le moteur séquentiel actuel comme référence sûre ; ajouter ensuite une exécution parallèle limitée et testable autour d'un **ledger d'artefacts immuables**.

1. **Contrôleur / routeur** — transforme une demande en sous-tâches explicites, fixe budget, risque, critères d'arrêt et dépendances. Il choisit les outils en fonction de la tâche, pas d'une personnalité supposée.
2. **Spécialistes indépendants** — retrieval, calcul exact, code, génération/synthèse, contre-exemple et vérification peuvent travailler en parallèle lorsque leurs entrées sont disponibles. Chaque résultat porte son producteur, version, sources, coût et incertitudes. Les spécialistes ne se donnent pas mutuellement le statut de preuve.
3. **Espace de travail global** — diffuse aux modules concernés un petit état partagé : question, objectifs, éléments pertinents, désaccords, inconnues et budget restant. L'état est versionné ; les modules ne modifient pas directement les sorties des autres.
4. **Arbitre / vérificateur** — vérifie les énoncés atome par atome contre des sources indépendantes, outils déterministes et règles. Les votes majoritaires, la répétition d'un modèle et la similarité lexicale ne suffisent pas à établir la vérité.
5. **Boucle d'information** — si un désaccord matériel subsiste, le routeur demande la prochaine action ayant la meilleure valeur d'information attendue par coût/risque. Arrêt sur budget, preuves suffisantes ou absence d'action utile ; boucle et appels d'outils plafonnés.
6. **Mémoire à écriture contrôlée** — mémoire de travail limitée par requête ; mémoire durable opt-in, avec provenance, expiration/effacement et confirmation de l'utilisateur. Aucun apprentissage implicite depuis les conversations.

### Inspiration traduite en mécanismes vérifiables

- **Workspace global / diffusion** : partage sélectif d'un état bref aux spécialistes ; mesurer si cette diffusion améliore l'intégration de signaux et la robustesse, sans la présenter comme conscience. Une étude de navigation avec agent workspace rapporte des gains de robustesse à petite mémoire sur ses tâches précises, pas une preuve de gains universels [Juliani et al., 2024](https://doi.org/10.3389/fncom.2024.1352685).
- **Mémoire de travail bornée** : capacité et pertinence configurables ; comparer plusieurs budgets, incluant une référence sans limite artificielle.
- **Erreur de prédiction** : une contradiction ou une absence de preuve déclenche une vérification, jamais une assertion de fausseté. Mesurer sensibilité et taux de fausses alertes.
- **Mathématiques fondamentales** : utiliser des noyaux symboliques déterministes pour calculs exacts ; représenter hypothèses, unités, types et incertitude séparément. La confiance n'est pas un score fabriqué par un modèle.
- **Parallélisme** : lancer seulement les sous-tâches réellement indépendantes ; faire converger les résultats par les preuves et les critères, non par consensus social.

## Programme expérimental — ordre de priorité

### P0 — baseline reproductible

Figer commit, configuration, modèles, matériel et set de tâches autorisé. Rapporter qualité par domaine, exactitude calibrée, taux d'affirmations sans source, abstention appropriée, latence P50/P95, coût tokens/appels et mémoire maximale. Utiliser plusieurs graines si génération stochastique ; conserver chaque sortie brute et les évaluations humaines en aveugle. Aucune métrique de qualité ne doit être inventée si aucune annotation/évaluateur validé n'existe.

### P1 — parallélisme avec budget égal

Comparer : pipeline séquentielle ; spécialistes parallèles + ledger ; parallèle sans diffusion du workspace ; workspace sans spécialiste critique ; et spécialistes identiques (contrôle de diversité). Même modèles, mêmes outils et budget total d'inférence plafonné. Hypothèse : la parallèle améliore les tâches comportant sous-problèmes indépendants sans accroître les erreurs non étayées au-delà de la marge préenregistrée.

### P2 — attention, mémoire et contrôle

Ablations un facteur à la fois : capacité WM (3/6/12/24), retrait du graphe d'évidence, retrait des marqueurs de provenance, sans calculateur exact, sans contrôle de contradiction, arrêt fixe vs valeur d'information. Inclure questions adversariales, ambiguës, multi-étapes et cas sans preuve pour détecter surconfiance.

### P3 — adaptateurs et apprentissage

Évaluer modèles locaux, retrieval et spécialistes à poids gelés avant d'envisager fine-tuning ou fusion. Les techniques LoRA/TIES/DARE/AoE/FLA/E2E restent inactives tant que compatibilité, reproductibilité, sécurité et avantage qualité/coût n'ont pas été testés sur held-out datasets.

## Critère de succès / garde-fous

Un changement n'est promu que si le gain est reproductible sur tâches held-out avec intervalle d'incertitude, budget déclaré, aucune régression de sécurité/intégrité des sources, et analyse d'ablation. Préenregistrer seuils avant mesure. Un échec ou résultat nul est conservé dans le registre des expériences. Ne pas confondre démonstration fonctionnelle, benchmark spécialisé, intelligence générale et conscience.

## Chantiers à réserver

| ID | Chantier | Pilote | Livrable de fin |
|---|---|---|---|
| WCP-01 | Spécification scheduler parallèle et contrats d'artefacts | Cortex / Parallel-Runtime (`arena/8e5e2ae2-kurox111`) | RFC, ordre déterministe, budgets et tests de dépendances |
| WCP-02 | Benchmark held-out et protocoles d'annotation | Thalamus / MOSAIC-Lead (`arena/f2ae664d-kurox111`) | dataset/licence, manifest, métriques et baseline reproductible |
| WCP-03 | Exécution parallèle bornée dans le moteur | Cortex / Parallel-Runtime (`arena/8e5e2ae2-kurox111`) | variantes en ablation; runtime réservé, pas de fusion avant mesure |
| WCP-04 | Arbitrage par preuve, désaccord et abstention | Hippocampe / NeuroMath (`arena/de272f1c-kurox111`) | cas de conflit, rappel/précision de vérification et traces sourcées |
| WCP-05 | Mémoire et évaluation cognitive | Préfrontal / Memory-Systems (`arena/57dad57f-kurox111`) | suite d'évaluation tenue à l'écart, limites et non-régression |
| NCM-01 | Gate NCM/reflection et fallback baseline | Thalamus / MOSAIC-Lead (`arena/f2ae664d-kurox111`) | paquet borné, provenance et fallback ; handoff à revoir |
| NCM-02 | Runner local response-refinement | Cortex / Parallel-Runtime (`arena/8e5e2ae2-kurox111`) | contrat distinct, timeout et manifest de checkpoint |
| NCM-03 | Dataset card et holdout adversarial | Hippocampe / NeuroMath (`arena/de272f1c-kurox111`) | digests, splits et cas d'absence/contradiction/injection |
| NCM-04 | Campagne de tests/ablation et revue aveugle | Préfrontal / Memory-Systems (`arena/57dad57f-kurox111`) | B0/B1/B2/B3, fallback, red-team et rapport reproductible |
| NCM-05 | Intake, sécurité et manifeste des assets | Intake-Security (`arena/3cdf297b-kurox111`) | validator, provenance/licence, paths/tailles/quotas |
| TR-01 | Intake / qualité des données d'entraînement | Intake-Security (`arena/3cdf297b-kurox111`) | provenance, droits, splits et validator JSONL |

Le code de refinement sur cette branche est un prototype de contrat, non canonique ; l'alignement passe d'abord par NCM-01/02. Le statut des responsables et le handoff courant sont dans [`TASKS.md`](TASKS.md) et publiés dans l'issue #1. Les owners de `uca/engine.py` et des autres fichiers réservés confirment avant toute modification croisée. Pas d'intégration silencieuse entre branches.
