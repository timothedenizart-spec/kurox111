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
