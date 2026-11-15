# Extensions cognitives : nouvelles architectures inspirées du cerveau et des mathématiques

> Contribution de la session `arena/57dad57f-kurox111` (2026-11-15), sur socle UCA `1120d24`.
> Toutes les extensions ci-dessous sont **déterministes, stdlib uniquement, testées**, et
> respectent les invariants épistémiques d'UCA : ni les similarités, ni les convergences
> d'attracteurs, ni les surprises ne sont jamais présentées comme des vérités.

## 1. Mémoire vectorielle hyperdimensionnelle (VSA / HRR) — `uca/vsa.py`

**Inspiration.** Les aires cérébrales ne stockent pas des symboles localisés mais des
*représentations distribuées* à très haute dimension. Les architectures vectorielles
symboliques (Holographic Reduced Representations de Plate, 2003 ; Sparse Distributed
Memory de Kanerva, 1988) transforment cette observation en mathématiques utilisables.

**Fondements implémentés.** Chaque symbole est un vecteur bipolaire de dimension 2048,
dérivé de façon déterministe (graine SHA-256 du nom). Deux opérations algébriques :

- **liaison** `bind(a,b) = a ⊙ b` (produit composante par composante) — involutif ;
- **superposition** `bundle` (somme re-binarisée, bris d'égalité déterministe).

Un fait structuré est encodé holographiquement :
`f = bundle(bind(S, R_sujet) ⊕ bind(P, R_prédicat) ⊕ bind(O, R_objet))`.

**Capacités réelles.**
- *Complétion par ré-encodage* : à partir de `(sujet, prédicat)`, on ré-encode les
  hypothèses candidates et on les compare aux faits stockés. Un triplet exactement
  reconstitué atteint une similarité cosinus de 1,0 ; les distracteurs restent au plancher
  de bruit statistique des vecteurs aléatoires.
- *Auto-diagnostic de fidélité* (`reconstruct_check`) : la mémoire vérifie elle-même que
  chaque fait encodé rappelle son propre objet — une mesure de la capacité du canal,
  jamais une validation des faits.
- *Transfert analogique* : les profils d'entités sont des superpositions de leurs rôles
  `(prédicat ⊗ objet)` ; deux entités partageant des rôles deviennent structurellement
  proches (sémantique distributionnelle holographique). Une lacune de prédicat chez une
  entité est comblée par transfert pondéré depuis ses voisines structurelles — émis comme
  **proposition `NON_VERIFIE`**, explicitement marquée hypothèse.

**Limite honnête.** Une similarité cosinus n'est pas une probabilité de vérité ; les
propositions analogiques n'entrent jamais dans le registre des faits.

## 2. Réseau de Hopfield — `uca/associative.py`

**Inspiration.** La complétion de motifs du cortex (l'analogue classique : le réseau CA3
de l'hippocampe) est capturée par les attracteurs de Hopfield (1982) : une mémoire
adressable par contenu dont les motifs stockés sont des minima d'énergie.

**Fondements implémentés.** Apprentissage hebbien en un coup `W = (1/n) Σ p pᵀ` (diagonale
nulle), énergie de Lyapunov `E(x) = -½ xᵀ W x`, descente asynchrone en ordre fixe donc
**convergence déterministe garantie** (E décroît monotonement).

**Limites honnêtes, appliquées par le code.** La capacité classique est ≈ 0,15·n motifs ;
au-delà les attracteurs parasites dominent. Le réseau **refuse** de stocker au-delà de sa
capacité plutôt que de corrompre silencieusement les rappels. Un rappel convergé est le
motif appris le plus proche — un rappel, pas une vérification.

## 3. Moniteur de surprisal — `uca/predictive.py`

**Inspiration.** Le codage prédictif décrit le cerveau comme une machine à minimiser
l'erreur de prédiction ; la théorie de l'information de Shannon donne la mesure :
`s(w) = -log₂ P(w | contexte)`.

**Fondements implémentés.** Un bigramme adaptatif (lissage additif) entraîné
*uniquement* sur les preuves locales (documents FTS + faits symboliques) mesure le
surprisal moyen de chaque analyse générée et le compare au fond statistique du corpus
(moyenne du corpus d'entraînement lui-même). Un texte dont le surprisal dépasse 1,6× le
fond est **marqué pour vérification** — signal symétrique du registre d'écarts d'ancrage
du GlobalWorkspace, jamais un verdict de fausseté. Sans corpus, le module le déclare
inconclusif plutôt que d'inventer des attentes.

## 4. Moteur parallèle par niveaux topologiques — `uca/engine.py`

**Inspiration.** Le cerveau est massivement parallèle ; l'orchestrateur séquentiel
historique ne l'était pas. Les mathématiques de l'ordonnancement (algorithme de Kahn,
1962) fournissent le parallélisme *sans* renoncer au déterminisme.

**Fondements implémentés.** Le graphe de dépendances déclarées est découpé en niveaux
**contigus** dans l'ordre du pipeline : les modules indépendants d'un même niveau
s'exécutent réellement en parallèle sur un snapshot gelé partagé, puis leurs résultats
sont appliqués à l'ordre canonique. Aplatir les niveaux reproduit exactement l'ordre du
pipeline — une exécution parallèle produit donc **bit-à-bit** les mêmes artefacts que
l'exécution séquentielle (vérifié par test de parité), tout en réduisant le temps mural
dès que des modèles lourds sont présents. Les niveaux actuels :

```text
L0 input_processing
L1 user_memory | knowledge_retrieval | associative_consolidation
L2 symbolic_processing
L3 analogical_memory | ncm_concept_generation
L4 smollm2_135_analysis
L5 smollm2_360_review
L6 surprisal_monitor | nanodiff_specialist
L7 global_workspace  ·  L8 final_verification  ·  L9 final_response
```

Les dépendances déclarées ont été auditées pour refléter réellement les lectures de
chaque module (`symbolic_processing` lit les documents ; `global_workspace` agrège
surprisal et nanoDiff). `engine.execution_mode = "sequential"` restaure l'ordre
historique à tout moment.

## 5. Consolidation hors-ligne de type Hebb — `uca/consolidation.py`

**Inspiration.** Le sommeil consolide les apprentissages diurnes en rejouant les traces
(mémoire épisodique → sémantique). Ici : **hors de tout chat**, une passe rejoue les
faits opérateurs contre le corpus FTS local et renforce les paires d'entités qui
co-occurrent — *« neurons that fire together wire together »* (Hebb, 1949).

**Fondements implémentés.** Force = indice de Jaccard sur les documents
`co / (n_a + n_b − co)` ; chaque arête conserve les identifiants des documents qui la
soutiennent ; rejouer les mêmes entrées donne bit-à-bit le même fichier (identifiant de
consolidation SHA-256). Exécution : `python -m uca consolidate --root .`.
Le module `associative_consolidation` publie ensuite chaque arête comme **proposition
`NON_VERIFIE`** traçable ; l'absence du fichier est un état `unavailable` explicite.

## Essai reproductible

```bash
python -m uca init --root .
python -m uca import-documents --root . passages.jsonl   # corpus local opérateur
# éditer data/operator_facts.json avec de vrais faits structurés
python -m uca consolidate --root .
python -m uca chat --root . "Quelle est la capitale de la Bretagne ?" --developer
python -m unittest discover -s tests -v                   # 27 tests
```

## Ce que ces extensions ne prétendent pas

- Aucune conscience, aucune équivalence biologique, aucune chaîne de pensée cachée.
- Aucune probabilité de vérité dérivée d'une similarité, d'une énergie ou d'un surprisal.
- Aucune amélioration « mesurée » sans évaluateur validé ou annotation humaine
  (le harnais de benchmark continue de laisser ces métriques `null`).
