# Architecture parallèle bornée d'UCA

UCA ne transforme pas des modèles distincts en un seul réseau de poids. Elle
met en parallèle uniquement les traitements réellement indépendants, puis les
réunit derrière des barrières de contexte immuables. Cela conserve l'objectif
d'origine : une intelligence locale à processus centralisé et traçable.

## Topologie implémentée : champ afférent + colonne délibérative

```text
requête
  │
  ├── Input Processing / plan cognitif / calcul exact              (barrière 1)
  │
  ├───┬─ mémoire explicite JSON ──────────────────────────────────┐
  │   ├─ recherche SQLite FTS5 ───────────────────────────────────┼─ merge canonique
  │   └─ MeTTa ou index de faits explicites ───────────────────────┘  (barrière 2)
  │
  ├── NCM conceptuel (si validé)                                  (séquentiel)
  ├── SmolLM2-135M : analyse indépendante                         (séquentiel)
  ├── SmolLM2-360M : revue critique                               (séquentiel)
  ├── nanoDiff masqué : proposition spécialisée, jamais remplacement auto
  ├── GlobalWorkspace : attention, diversité, conflits, couverture
  ├── vérification documentaire / symbolique / calculatoire
  └── réponse unique
```

Le mode `staged_parallel` parallélise seulement la mémoire, le FTS et le
traitement symbolique : chacun lit le **même snapshot post-input** et ne peut
pas observer les résultats de ses voisins. Le moteur réintègre ensuite les
résultats selon l'ordre canonique de pipeline, et produit un événement de trace
`parallel_afferent_fanout`. The current topology is visible in `uca status`,
`/api/status`, and `available_context.execution_topology` in developer traces.

Les modèles, NCM et nanoDiff restent séquentiels. Cette limite est volontaire :
leurs poids peuvent se disputer RAM/VRAM, leurs runtimes ne sont pas encore tous
validés, et une concurrence de GPU ne démontre aucune amélioration cognitive.

## Principes inspirants, traduits en invariants techniques

| Inspiration | Traduction UCA réelle | Ce que cela ne signifie pas |
|---|---|---|
| Voies sensorielles parallèles | Lectures mémoire/document/symbole concurrentes et isolées | Simulation d'un cerveau biologique |
| Mémoire de travail limitée | Sélection bornée, diversité de modalités et traçabilité | Oubli automatique de données utilisateur |
| Global workspace | Dossier commun avec provenance, contradictions et incertitudes | Vote majoritaire ou vérité émergente |
| Codage prédictif | Registre de faible ancrage lexical à vérifier | Preuve qu'une génération est fausse |
| Raisonnement formel | Arithmétique rationnelle AST restreinte | Vérification des prémisses du monde réel |
| Théorie de l'information | Entropie de diversité des modalités/producteurs | Mesure de qualité, vérité ou intelligence |

## Contrat de déterminisme et de sûreté

1. Les modules parallèles doivent déclarer `parallel_safe=True` et ne faire que
   lire leurs magasins locaux.
2. Ils reçoivent un snapshot JSON, jamais le contexte mutable central.
3. Les artefacts sont fusionnés par le coordinateur dans l'ordre du pipeline,
   jamais dans l'ordre d'arrivée des threads.
4. Un timeout ou une erreur est localisé au module ; un résultat tardif est
   ignoré et ne peut pas muter le contexte.
5. Aucun tokenizer, embedding, tenseur ou état de modèle ne franchit une
   frontière parallèle.

## Plan expérimental avant toute affirmation d'amélioration

Les propositions suivantes sont des chantiers, pas des capacités déclarées :

1. **Latence et déterminisme** — comparer `sequential`/`staged_parallel` sur un
   corpus local réel ; vérifier que les mêmes entrées donnent la même séquence
   d'artefacts hors UUID/timestamps.
2. **Ablation de diversité** — comparer `diversity_bonus = 0` et la valeur
   configurée sur des tâches annotées, avec rappel de sources, contradictions
   visibles et taux d'affirmations non ancrées.
3. **Boucle de recherche active** — seulement après corpus FTS réel : émettre
   des sous-requêtes explicites depuis les lacunes du workspace, avec budget,
   journal et arrêt borné.
4. **Contraintes symboliques** — seulement après runner MeTTa validé : faire
   vérifier les relations via règles fournies, sans compléter une absence.
5. **Délibération multi-modèle** — seulement après checkpoints réels : séparer
   générateur, critique et rédacteur, mesurer les corrections factuelles plutôt
   que le volume de texte.
6. **Gouverneur de ressources** — mesurer RAM/VRAM et décider par données si un
   modèle peut rejoindre une étape parallèle ; le mode séquentiel reste le
   repli sûr.

Aucun de ces chantiers ne doit être présenté comme une amélioration validée sans
jeu de tâches, configuration, traces et résultats reproductibles.
