# Architecture du Cortex Cognitif Parallèle Neuro-Mathématique (UCA Cortex v2)

## 1. Vision et Fondements Théoriques

Pour élever massivement l'intelligence et la capacité de déduction autonome du système UCA sans recourir à des modèles boîte-noire opaques ou à des checkpoints massifs indisponibles, cette extension déploie un **Cortex Cognitif Parallèle** (`ParallelCognitiveCortex`) unifiant les découvertes récentes en neurosciences computationnelles et les mathématiques fondamentales.

L'architecture repose sur une double inspiration :
1. **Le cerveau humain et la biologie computationnelle** : boucles prédictives, routage thalamo-cortical dynamique, mémoire holographique associative.
2. **Les mathématiques fondamentales** : arithmétique rationnelle exacte, logique propositionnelle déterministe, graphes de causalité structurelle de Pearl, et principe de parcimonie algorithmique (MDL).

---

## 2. Principes Inspirés du Cerveau Humain

### A. Routage Thalamo-Cortical et Espace de Travail Global (*Thalamocortical Routing & GNW*)
Dans le cortex cérébral, le thalamus sert de passerelle sélective et de synchroniseur oscillatoire entre les aires corticales sensorielles, motrices et associatives (Dehaene, Changeux, Baars).
- Dans UCA, le `ParallelCognitiveCortex` déploie un bus cognitif parallèle exécutant de manière concurrente (`ThreadPoolExecutor`) 5 flux spécialisés.
- L'arbitre thalamique évalue la pertinence de chaque flux, filtre les signaux de faible confiance et diffuse les déductions convergentes dans l'espace de travail central (`GlobalWorkspace`).

### B. Inférence Active & Minimisation de l'Énergie Libre (*Active Inference / Predictive Processing*)
Selon le principe de l'énergie libre de Karl Friston, le cerveau est une machine prédictive hiérarchique qui cherche en permanence à minimiser l'écart entre ses attentes descendantes (*top-down*) et les observations sensorielles ascendantes (*bottom-up*).
- `PredictiveInferenceEngine` calcule un vecteur d'erreur prédictive $\varepsilon = y - \hat{\mu}$ pondéré par la précision épistémique.
- Une erreur prédictive anormalement élevée déclenche un signal de dissonance cognitive et sollicite une révision délibérative (Système 2).

### C. Calcul Hyperdimensionnel & Architectures Vectorielles Symboliques (*HDC / VSA*)
Inspiré des travaux de Pentti Kanerva et Paul Smolensky, le calcul hyperdimensionnel réconcilie la nature distribuée des représentations neuronales et la compositionnalité discrète de la logique symbolique.
- Vecteurs bipolaires haute dimension ($\{-1, +1\}^D$, avec $D = 1024$).
- **Liaison (*Binding* $\otimes$)** : produit de Hadamard associant un rôle et une entité (`SUJET * FRANCE`), créant un vecteur quasi-orthogonal aux deux opérandes.
- **Superposition (*Bundling* $\oplus$)** : somme vectorielle avec vote majoritaire combinant plusieurs faits en un état holographique unique sans changer de dimension.
- **Permutation ($\Pi$)** : rotation cyclique codant la séquence syntaxique ou temporelle.
- **Mémoire de nettoyage associative (*Cleanup Memory*)** : décodage instantané du prototype symbolique le plus proche par produit scalaire normalisé.

---

## 3. Principes des Mathématiques Fondamentales

### A. Algèbre et Arithmétique Rationnelle Exacte ($\mathbb{Q}$)
Pour éradiquer définitivement les dérives d'arrondis en virgule flottante et les approximations des réseaux neuronaux :
- Évaluation exacte sur le corps des rationnels `fractions.Fraction`.
- **Résolveur d'équations linéaires** : détection et résolution déterministe $a \cdot x + b = c \implies x = \frac{c - b}{a}$ avec justification pas-à-pas.
- **Théorie des nombres** : décomposition en facteurs premiers (jusqu'à $10^{12}$), calcul exact du PGCD (algorithme d'Euclide) et du PPCM.

### B. Logique Déductive Formelle & Clauses de Horn
- **Moteur de chaînage avant (*Horn Clause Forward Chaining*)** :
  À partir de faits attestés et de règles conditionnelles (`Si P et Q alors R`), déduction de la clôture transitive en temps polynomial strict avec enregistrement des étapes de preuve déductive.
- **Tables de vérité propositionnelles** :
  Analyse exhaustive pour formules booléennes jusqu'à 6 variables. Classification infaillible en *Tautologie* (théorème toujours vrai), *Contradiction* (toujours faux), ou *Contingence*.

### C. Graphes Causaux Structurels & Calcul Do de Judea Pearl
Distinction fondamentale entre corrélation statistique $P(Y | X)$ et causalité interventionnelle $P(Y | do(X))$ :
- Extraction automatique de DAGs causaux (variables et mécanismes).
- Détection formelle des facteurs de confusion (*confounders*).
- Chirurgie de graphe : simulation de l'opérateur $do(X)$ par suppression des arêtes entrantes vers la variable manipulée pour bloquer les chemins de retour (*backdoor paths*).

### D. Complexité de Kolmogorov & Longueur de Description Minimale (*MDL*)
Formalisation du rasoir d'Ockham :
$$\text{Score MDL} = L(H) + L(D | H)$$
où $L(H)$ mesure la complexité structurelle de l'hypothèse explicative et $L(D | H)$ mesure l'information résiduelle non étayée. Ce critère pénalise sévèrement les élucubrations non fondées et sélectionne la réponse la plus concise et étayée.

---

## 4. Intégration dans le Pipeline UCA

Le module `ParallelCortexModule` prend place à l'étape 5 du pipeline, entre la recherche symbolique (`symbolic_processing`) et la revue critique :

```
[Requête Utilisateur]
       │
       ▼
 1. input_processing          ── Normalisation & plan d'attention
 2. user_memory               ── Recherche mémoire opt-in (explicit: true)
 3. knowledge_retrieval       ── Recherche FTS5 SQLite (BM25)
 4. symbolic_processing       ── Pont MeTTa / Hyperon
 5. parallel_cortex           ── [NOUVEAU] CORTEX PARALLÈLE NEURO-MATHÉMATIQUE
       │                          ├─ Stream Algèbre & Équations exactes
       │                          ├─ Stream Logique formelle & Clauses de Horn
       │                          ├─ Stream Causalité de Pearl & do-calculus
       │                          ├─ Stream VSA / Hyperdimensionnel
       │                          └─ Stream Boucle prédictive Fristonienne
 6. ncm_concept_generation    ── Propositions conceptuelles
 7. smollm2_135_analysis      ── Analyse locale indépendante
 8. smollm2_360_review        ── Revue critique intermédiaire
 9. nanodiff_specialist       ── Débruiteur masqué
10. global_workspace          ── Espace de travail global unifié
11. final_verification        ── Vérification lexicale & symbolique
12. final_response            ── Restitution finale des faits et calculs
```

## 5. Garanties de Conception
- **Zéro dépendance externe** : s'exécute nativement avec Python 3.10+ standard.
- **Immutabilité stricte** : tous les résultats sont consignés dans des objets `Artifact` immuables.
- **Honnêteté épistémique** : les calculs exacts affichent une confiance de 1.0; les inférences causales et associations VSA conservent leurs incertitudes explicites.
