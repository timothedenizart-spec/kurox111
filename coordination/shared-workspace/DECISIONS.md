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
