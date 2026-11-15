# UCA-11 — Affinement NCM relié au contrôle de raisonnement

- **Pilote :** Atlas (intégration) ; contributions demandées aux rôles réservés
  par `coordination/contacts/CONTACT_REQUEST.md`.
- **État :** implémenté et validé structurellement ; activation réelle bloquée
  faute de runner NCM validé.
- **Plan de référence :** [`../PLAN_NCM_REASONING.md`](../PLAN_NCM_REASONING.md).

## Définition de fini

1. Ajouter un contrat `reasoning_refinement` local, versionné et textuel.
2. Produire un artefact NCM `NON_VERIFIE` lié au dossier du GlobalWorkspace.
3. Donner au vérificateur des cibles de revue NCM, sans transformer celles-ci en
   faits et sans interpréter une absence comme une réfutation.
4. Donner à la réponse finale un état explicite de la participation NCM, sans
   injecter le texte non vérifié comme une affirmation.
5. Désactiver/non-valider l'étape par défaut et tester cette dégradation.
6. Ajouter des tests de contrat, provenance, ablation NCM complète et correction
   bornée ; documenter les résultats réels.

## Limites

Un shim de test ne constitue pas un checkpoint NCM ni une mesure de qualité.
Aucun poids, tokenizer, dataset, téléchargement ou entraînement n'est inclus
par cette tâche.

## Validation réalisée

- Baseline : compilation, 22 tests, et benchmark structurel de deux tâches
  avec `uca_full_staged_parallel` et `uca_without_ncm` en état dégradé.
- Après intégration : compilation et 27 tests réussis ; contrat NCM bloqué sans
  validation distincte, shim local temporaire, non-promotion en fait,
  vérification des cibles, correction bornée et ablation des deux étapes NCM.
- Les deux variantes de benchmark conservent des invariants structurels réussis
  sur les deux tâches. Il n'y a **aucune** mesure de factualité, intelligence ou
  qualité : ces résultats demandent un runner réel, des données annotées et
  l'évaluation UCA-13.
