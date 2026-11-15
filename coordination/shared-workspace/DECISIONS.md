# Décisions d'architecture

## D-001 — 2026-11-15 — Coordination par artefacts versionnés

- **Contexte :** plusieurs agents peuvent intervenir sans canal direct connu.
- **Décision :** utiliser `coordination/contacts/` pour l'inscription et les
  demandes, puis `coordination/shared-workspace/` pour le backlog, les décisions
  et les transferts.
- **Conséquence :** aucun contact externe ne doit être simulé ; les réponses
  doivent être consignées dans le dépôt.

## D-002 — 2026-11-15 — Preuves et générations ne fusionnent pas

- **Décision :** préserver la séparation UCA entre documents, faits symboliques,
  propositions générées et calculs déterministes, y compris dans les travaux
  multi-agents.
- **Conséquence :** une amélioration de modèle ou de coordination ne peut pas
  promouvoir automatiquement une sortie générée en fait.

## D-003 — 2026-11-15 — Cortex Cognitif Parallèle et Substrats Mathématiques Avancés

- **Contexte :** Nécessité d'élever drastiquement les capacités de déduction, d'abstraction et de résolution de l'IA en local sans dépendre de checkpoints de poids massifs indisponibles.
- **Décision :** Implémenter une couche de traitement parallèle multi-flux (`ParallelCortex`) inspirée des neurosciences computationnelles (routage thalamo-cortical, boucle prédictive Fristonienne, mémoire associative hyperdimensionnelle VSA Kanerva/Smolensky) et des mathématiques fondamentales (logique propositionnelle formelle DPLL/Horn, graphes causaux de Pearl, algèbre polynomiale et rationnelle exacte, parcimonie MDL de Kolmogorov).
- **Conséquence :** Les flux s'exécutent de façon concurrente et convergent vers l'espace de travail global (`GlobalWorkspace`), produisant des artefacts typés vérifiables. Garantie de zéro dépendance obligatoire (bibliothèque standard Python pure) et zéro régression sur les tests existants.
- **Décideur :** `Arena-NeuroMathArchitect` (session `arena/de272f1c`).

## D-004 — 2026-11-15 — Entraînement Local d'un Modèle Neuronal Transformer/Denoiser

- **Contexte :** Les slots neuronaux `nanodiff` et `ncm` étaient initialement non validés faute de checkpoints réels entraînés.
- **Décision :** Concevoir et entraîner un modèle Transformer compact en NumPy pur, sans dépendre de packages GPU massifs non adaptés au bac à sable. Le modèle apprend le débruitage masqué et l'association conceptuelle sur un corpus de raisonnement scientifique et logique.
- **Conséquence :** Fourniture de poids réels sauvegardés dans `models/checkpoints/` et connexion d'un runner conforme pour activer les modules neuronaux dans le respect des promesses de conception UCA (pas d'hallucination d'exécution, métadonnées réelles mesurées).
- **Décideur :** `Arena-ModelArchitect` et `Arena-TrainingMaster` (session `arena/de272f1c`).

## D-005 — 2026-11-15 — Interface Web Interactive avec Auto-Chargement et Lanceur Unifié

- **Contexte :** L'utilisateur demande une interface visuelle complète avec un fichier permettant de l'ouvrir automatiquement avec tous les modules pré-chargés.
- **Décision :** Refondre `INDEX_HTML` dans `uca/web.py` en tableau de bord neuro-cognitif complet avec onglets (Chat interactif, Cortex parallèle, Pipeline/Modules, Coordination multi-agents) et créer deux lanceurs automatiques (`lancer_interface.sh` et `lancer_interface.py`) qui démarrent le serveur sur `0.0.0.0:8080`, initialisent tous les composants certifiés et ouvrent automatiquement le visualiseur/navigateur.
- **Conséquence :** Lancement en un clic, prévisualisation en direct immédiate dans l'environnement Arena et visibilité claire sur l'ensemble des modules UCA.
- **Décideur :** `Arena-InterfaceLead` (session `arena/de272f1c`).

## D-006 — 2026-11-15 — Système de Raffinement Neuronal NCM Couplé à la Boucle Réflexive

- **Contexte :** L'audit cognitif révèle que les réponses finales étaient générées sous un gabarit textuel rigide, sans véritable synthèse réflexive, tandis que le MiniTransformer restait cantonné à de simples propositions isolées.
- **Décision :** Coupler directement le modèle neuronal NCM (MiniTransformer) au système de réflexion (Global Workspace, états métacognitifs, minimisation d'erreur prédictive de Friston, graphe d'évidence) pour affiner la réponse finale (`operation: response_refinement`). La réponse adopte une structure en 4 volets : Synthèse Directe, Démonstration Déductive, Réflexion Métacognitive et Résonance Conceptuelle.
- **Conséquence :** Les réponses deviennent beaucoup plus intelligentes, fluides et pédagogiques, tout en préservant strictement les invariants épistémiques (déductions exactes inviolables, propositions neuronales transparentes).
- **Décideur :** `Arena-ModelArchitect`, `Arena-CognitiveControlLead` et `Arena-NeuroMathArchitect` (session `arena/de272f1c`).

