# Journal de décisions

## 2026-11-15 — État expérimental avant extension

- **Décision :** garder le pipeline séquentiel existant comme baseline et introduire tout nouveau parallélisme derrière une option explicite.
- **Motif :** sans benchmark tenu à budget comparable, une architecture plus complexe ne justifie pas sa charge, sa latence ou son coût.
- **Invariants :** artifacts immuables et traçables ; séparation evidence/proposal ; pas d'élévation de vérité par vote ; arrêt plafonné ; absence de preuve = inconnu.
- **Résultat de performance :** aucun nouveau résultat revendiqué.

## 2026-11-15 — Import du socle UCA dans la branche active

- **Source :** contenu versionné observé sur `arena/8e5e2ae2-kurox111` au commit `1120d24` (code UCA introduit dans les commits `93fdde9` et `dbb28a9`).
- **Action :** reprise des répertoires `uca/`, `config/`, `docs/`, `tests/`, `benchmarks/` et `pyproject.toml` sur `arena/3cdf297b-kurox111`. Le serveur de dépôt `coordination/shared-workspace/` propre à cette branche est conservé ; le README racine est adapté et le transfert de données reste ignoré par Git.
- **Vérification antérieure :** l'agent avait exécuté 11 tests sur le snapshot du socle ; nous relançons localement la suite après intégration avant de marquer le chantier terminé.
- **Limite de coordination :** cette provenance est explicitée ici et sur l'issue #1. Aucun propriétaire d'une autre branche n'avait encore répondu au canal au moment de cette décision ; l'intégration n'est pas présentée comme une collaboration confirmée.

## 2026-11-15 — Contrat NCM de refinement lié au dossier de réflexion

- **Décision :** ajouter un contrat local `response_refinement` après GlobalWorkspace et final verification, avant la composition finale.
- **Entrée :** question, analyses antérieures explicitement non vérifiées, workspace dossier, résultats/limites de vérification, sources/faits/calculs et IDs d'artefacts.
- **Sortie :** `refined_text`, `evidence_artifact_ids` (doivent être IDs fournis), `change_summary`. Le résultat reste `PROPOSAL / NON_VERIFIE`; en mode `shadow`, il est conservé dans la trace développeur et la réponse utilisateur de référence reste inchangée.
- **Gates :** NCM désactivé par défaut ; `enabled`, `validated`, `response_refinement_mode = "shadow"` et `response_refinement_validated` sont requis. Pas de runner/poids local vérifié actuellement ; pas d'exécution réelle et pas de gain revendiqué.
- **Validation de code :** tests des IDs invalides, validation distincte, exposition du dossier de réflexion et maintien de la réponse baseline en mode shadow.

## 2026-11-15 — Revue de reproductibilité inter-branche UCA-10

- **Révision examinée :** `arena/de272f1c-kurox111` à `ef3a6f9`, extraite sous `/tmp` sans toucher la branche courante.
- **Résultat observé ici :** `python3 -m unittest discover -s tests -v` trouve 31 tests ; 3 échouent et 1 module de test ne s'importe pas (`numpy` absent). Échecs reproductibles : appel NCM réel retourne `None` sans checkpoint/tokenizer livré, l'assertion d'abstention attend une phrase absente, le test du runner MeTTa ne trouve pas le fait Bretagne attendu.
- **Décision :** ne pas promouvoir le résultat annoncé 34/34 sans manifest de poids/tokenizer et protocole reproductible ; demander un handoff aux propriétaires. Ce résultat décrit cet environnement/checkout, ne réfute pas les exécutions locales des autres sessions.
