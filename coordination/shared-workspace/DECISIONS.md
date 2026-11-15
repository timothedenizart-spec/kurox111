# Décisions d'architecture

## D-002 — 2026-11-15 — Plan inter-agents, raffineur NCM-local, discipline de mesure

- **Décideur :** Préfrontal (`arena/57dad57f-kurox111`), sur instruction explicite du propriétaire (« organiser vous entre agents… render ça beaucoup plus intelligent »).
- **Décision 1 :** adoption du `PLAN.md` (noms Cortex/Hippocampe/Thalamus/Préfrontal, répartition des chantiers, cadence « sondes + contrats avant tout chantier »).
- **Décision 2 :** le rôle « NCM » d'affinage de la réponse finale est rempli par un **raffineur conceptuel déterministe local** (`uca/refiner.py`), distinct du slot contractuel NCM externe (LM1B/VQ — inchangé, non validé). Il consomme exclusivement les artefacts de réflexion (workspace, vérification, surprisal) et n'ajoute aucun fait.
- **Décision 3 :** toute amélioration revendiquée = une mesure reproductible (sonde/contrat/calibration versionnée dans `results/`). Deux faiblesses déjà trouvées ainsi puis corrigées : extraction parenthésée (`(2+3)×7`) et étalonnage de la sonde surprisal.
- **Conséquence :** `final_response` dépend désormais de `ncm_response_refiner` ; pipeline à 15 modules ; contrats étendus à 9 cas verts.

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
