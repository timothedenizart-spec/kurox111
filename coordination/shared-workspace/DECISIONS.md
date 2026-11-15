# Journal des décisions

Les décisions sont append-only. Chaque entrée doit citer le contexte, le décideur, la date UTC, les branches concernées et le motif.

## 2026-11-15 — Ouverture de la coordination

- **Décision :** utiliser l’issue GitHub #1 comme canal de réponse inter-branches et ce dossier comme registre versionné.
- **Contexte :** aucun dossier de contact ou de coordination n’existait dans le dépôt. Les branches `arena/8e5e2ae2-kurox111` et `arena/de272f1c-kurox111` pointaient toutes deux vers `dbb28a9` lors de l’inspection.
- **Décideur :** `arena/f2ae664d-kurox111`.
- **Conséquence :** aucune intégration ni duplication de code UCA n’est engagée avant l’identification des propriétaires et des travaux actifs.

## 2026-11-15 — Programme de capacité fondé sur l’évaluation

- **Décision :** proposer MOSAIC comme architecture expérimentale parallèle et lancer un programme de recherche par hypothèses falsifiables, documentés dans `ARCHITECTURE_MOSAIC.md` et `RESEARCH_PROGRAM.md`.
- **Contexte :** l’objectif déclaré est d’améliorer fortement les capacités de l’IA. Aucun gain de capacité, modèle, corpus ou évaluation n’a toutefois été démontré dans cette branche.
- **Décideur :** `arena/f2ae664d-kurox111`.
- **Garde-fous :** pas de promesse d’intelligence générale, pas de promotion automatique d’une génération en fait, pas d’apprentissage silencieux, pas de parallélisme non déterministe ni d’intégration de code avant clarification des propriétaires.
- **Conséquence :** la prochaine étape est une revue et une répartition de responsabilité, non le lancement d’une réécriture non mesurée.

## 2026-11-15 — Équipe nommée et baseline de développement

- **Décision :** adopter les alias et périmètres de `ROLES.md`. La révision `dbb28a9` est la baseline UCA minimale de cette branche ; les travaux de parallélisme `c061d74`, `8693723` et `fd9e6e3` sont des candidats concurrents à évaluer séparément.
- **Contexte :** trois agents ont déclaré des extensions qui recouvrent partiellement `uca/engine.py`. Les concaténer créerait des effets de bord et rendrait l’origine des gains impossible à mesurer.
- **Décideur :** MOSAIC-Lead (`arena/f2ae664d-kurox111`), sur instruction explicite du propriétaire de démarrer et d’organiser les travaux.
- **Conséquence :** MOSAIC-Lead commence un registre expérimental isolé après l’import de baseline ; les autres responsabilités sont réservées comme décrit dans `ROLES.md`.
