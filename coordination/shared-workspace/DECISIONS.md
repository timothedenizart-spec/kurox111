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

## D-003 — 2026-11-15 — Parallélisme afférent borné, délibération séquentielle

- **Contexte :** l'amélioration de la latence ne doit pas créer une course entre
  modules, une fusion implicite des modèles ou une modification non déterministe
  du contexte central.
- **Décision :** paralléliser seulement la mémoire explicite, le FTS et le
  symbole lorsqu'ils sont `parallel_safe`, depuis un même snapshot post-input.
  Le moteur réintègre ensuite les artefacts dans l'ordre canonique. NCM et les
  modèles restent séquentiels derrière cette barrière.
- **Conséquence :** l'architecture peut exploiter un parallélisme réel de
  lectures indépendantes, mais aucun gain qualitatif, de latence ou de VRAM
  n'est revendiqué avant benchmark sur actifs locaux réels.

## D-004 — 2026-11-15 — NCM comme signal de revue, jamais comme autorité de fait

- **Contexte :** la demande UCA-11 veut relier un affinement NCM au contrôle de
  raisonnement et à la réponse finale, alors qu'aucun runner/checkpoint NCM
  réel n'est actuellement fourni.
- **Décision :** ajouter seulement un contrat local, textuel et explicitement
  désactivé/non validé par défaut. Lorsqu'il est validé par un opérateur, le NCM
  émet un plan de revue et des cibles de vérification dans un artefact
  `PROPOSAL` `NON_VERIFIE`, relié au dossier GlobalWorkspace. Le vérificateur
  confronte ces cibles aux sources/faits/calculs indépendants ; la composition
  finale ne convertit pas le texte NCM en assertion factuelle.
- **Conséquence :** le NCM peut améliorer la couverture et l'ordre de contrôle,
  mais ne prouve rien, ne remplace pas automatiquement une réponse et ne peut
  être décrit comme améliorant la qualité sans ablation annotée reproductible.
