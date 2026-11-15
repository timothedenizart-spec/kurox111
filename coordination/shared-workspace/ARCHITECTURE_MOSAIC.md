# MOSAIC — architecture expérimentale pour une intelligence plus fiable et plus capable

> **Statut : proposition de recherche, non implémentée.** MOSAIC signifie *Modular, Observable, Search-and-Inference Cognition*. Le nom désigne une hypothèse d’architecture ; il ne prouve ni conscience, ni équivalence au cerveau, ni amélioration de capacité avant évaluation.

## Intention

Le but n’est pas de remplacer un modèle de langage par une métaphore du cerveau. Le but est de combiner, de manière traçable :

- perception et récupération d’évidence ;
- mémoire explicitement gouvernée ;
- calcul exact et vérification formelle lorsque le domaine le permet ;
- génération d’hypothèses ;
- planification et recherche à temps d’inférence ;
- critique indépendante, calibration et synthèse fondée sur les sources.

Les analogies biologiques sont limitées à des principes de contrôle utiles : mémoire de travail bornée, compétition de priorités, intégration globale et détection d’écart entre prédiction et évidence. Elles ne constituent pas un modèle neuroscientifique du cerveau.

## Principe fondateur : plusieurs voies, aucune autorité magique

Une réponse n’est jamais promue par le simple nombre de modèles qui la répètent. Les voies parallèles produisent des artefacts immuables, ensuite arbitrés par une politique explicite.

```text
requête
  │
  ├─► voie P : perception, segmentation, détection de tâche
  ├─► voie R : récupération documentaire et mémoire explicite
  ├─► voie F : calcul exact, logique, solveur / vérificateur si disponible
  ├─► voie H : hypothèses génératives indépendantes
  ├─► voie S : planification et recherche de programmes / outils
  └─► voie C : estimation des coûts, risques et besoins d'information
             │                (barrière déterministe)
             ▼
       espace de travail / graphe d'évidence
             │
  ┌──────────┼──────────┐
  ▼          ▼          ▼
critique   vérification  recherche supplémentaire ciblée
             │
             ▼
      synthèse avec citations, limites et statut épistémique
```

Les voies P/R/F/C peuvent s’exécuter en parallèle depuis le même instantané de requête. Les voies H/S reçoivent ensuite un paquet d’évidence compacté. Toute fusion passe par une barrière : aucun module ne peut modifier rétroactivement les sorties d’un autre module.

## Contrat commun de connaissance

L’artefact UCA append-only doit évoluer vers un contrat plus précis, sans casser la provenance existante.

| Catégorie | Producteur autorisé | Peut soutenir une réponse ? | Peut devenir un fait ? |
| --- | --- | ---:| ---: |
| `evidence_document` | récupération locale / import contrôlé | oui, avec provenance | non automatiquement |
| `memory_explicit` | opérateur ou utilisateur, consentement explicite | seulement comme mémoire déclarée | non |
| `computation_exact` | noyau déterministe vérifié | oui, dans son périmètre formel | non documentaire |
| `derivation_checked` | preuve, solveur ou règle déclarée | oui, si hypothèses citées | non sans règles et hypothèses |
| `claim_generated` | modèle ou heuristique | non seule | jamais automatiquement |
| `plan_candidate` | planificateur | non | non |
| `verification_report` | vérificateur indépendant | informe la synthèse | non |
| `decision_record` | contrôleur déterministe | explique le routage | non |

Chaque affirmation substantielle porte au minimum : identifiant, entrée(s), producteur, version du module, références, niveau de confiance **calibré ou absent**, limites et statut parmi `observed`, `exact`, `derived`, `supported`, `proposed`, `disputed`, `inconclusive`.

## Mémoire à trois vitesses

1. **Mémoire de travail** — ensemble borné d’artefacts prioritaires ; la priorité alloue du calcul, elle ne mesure pas la vérité.
2. **Mémoire épisodique explicite** — éléments créés uniquement par une action de l’utilisateur ou d’un opérateur autorisé ; pas d’apprentissage silencieux à partir de conversations.
3. **Mémoire sémantique documentaire** — index de documents avec version, provenance, date et stratégie de rétention. Les passages restent des sources, non des croyances.

La consolidation éventuelle est un travail différé : elle produit une proposition de résumé et requiert une validation humaine ou une règle déterministe, avec journal d’audit et possibilité de suppression.

## Noyau mathématique et raisonnement

MOSAIC sépare nettement trois formes de raisonnement.

### 1. Substrat exact

Étendre l’arithmétique rationnelle déjà proposée vers :

- expressions typées et unités ;
- algèbre symbolique limitée ;
- vérification de contraintes par SMT/SAT ou solveur certifié, seulement si installé localement ;
- traçage de chaque hypothèse, règle, version de solveur et contre-exemple éventuel.

Une réussite de solveur prouve la conséquence dans son formalisme et ses hypothèses, jamais la vérité d’une prémisse issue du monde réel.

### 2. Raisonnement probabiliste et calibration

Les sorties prédictives peuvent être accompagnées d’intervalles, de prédictions conformes ou de probabilités calibrées **après mesure sur un jeu de validation séparé**. Une valeur numérique ne doit jamais être appelée « confiance » si aucune calibration n’a été mesurée.

### 3. Recherche à temps d’inférence

Pour les tâches décomposables, le système génère des plans ou programmes candidats, vérifie les étapes exécutables, puis conserve un arbre de recherche limité par budget. Un score de sélection peut prendre la forme :

```text
utilité = gain d'information attendu
        + couverture d'évidence
        + vérifiabilité
        - coût de calcul
        - risque estimé
```

Ce score est un mécanisme d’allocation et non une probabilité de vérité. Ses termes, poids et décisions doivent être enregistrés.

## Orchestrateur parallèle déterministe

La version actuelle d’UCA est séquentielle. Le mode expérimental doit introduire un DAG déclaré :

- `ModuleSpec` : schéma d’entrées/sorties, dépendances, capacités, niveau de confiance, coût maximal, droits d’effets de bord ;
- exécution par **super-étapes** : modules indépendants en parallèle, réduction stable triée par ID de module puis ID d’artefact ;
- instantané immuable par super-étape ;
- limites distinctes CPU, mémoire, GPU, durée, nombre de candidats et taille d’artefact ;
- modules externes dans des sous-processus arrêtables, plutôt que des threads Python non interruptibles ;
- journal de planification : tâches lancées, annulées, ignorées et raison budgétaire.

L’exécution parallèle ne doit pas être activée pour les modules qui écrivent un stockage ou emploient des ressources non isolées. Ces modules restent sérialisés derrière une transaction explicite.

## Global workspace et arbitre

Le workspace ne « pense » pas à la place des modules. Il maintient un graphe de dépendance et appelle l’arbitre pour :

1. détecter les affirmations incompatibles ;
2. chercher une preuve, une source ou un calcul discriminant ;
3. décider qu’une réponse est inconclusive lorsque le budget est épuisé ;
4. choisir un format de réponse proportionné à l’évidence.

L’arbitre est déterministe dans sa politique par défaut. Tout arbitre appris doit publier son modèle, son jeu d’évaluation, son calibration report et des tests de régression avant d’influencer une réponse utilisateur.

## Boucle d’amélioration, sans auto-illusion

```text
benchmark versionné → exécution instrumentée → analyse d'erreurs
      → hypothèse de changement → ablation contrôlée
      → revue humaine / seuils préenregistrés → intégration ou rejet
```

L’apprentissage en ligne à partir des réponses ou de l’auto-évaluation du modèle est exclu du chemin par défaut. Les améliorations de poids, prompts, politiques de routage ou index passent par versionnage, validation hors échantillon, canari et possibilité de retour arrière.

## Invariants non négociables

- Aucun mélange de tokeniseurs, tenseurs ou embeddings entre modèles hétérogènes.
- Aucune écriture de mémoire personnelle sans consentement explicite.
- Aucune absence de résultat promue en preuve négative.
- Aucune proposition générée promue automatiquement en fait.
- Aucune métrique de capacité annoncée sans baseline, ablations et protocole reproductible.
- Aucune commande externe, donnée locale ou poids non approuvé ne devient une dépendance implicite.
