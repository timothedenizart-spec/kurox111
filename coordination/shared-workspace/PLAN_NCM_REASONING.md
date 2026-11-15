# Plan inter-agents — UCA-11 : raisonnement traçable et affinement NCM

**Émis :** 2026-11-15 UTC · **Pilote d'intégration :** Atlas · **État :** actif,
mais aucun autre agent ni runner NCM réel n'est actuellement inscrit/disponible.

## Objectif mesurable

Ajouter un *affinement NCM de raisonnement* qui peut aider à cibler la
vérification et l'organisation de la réponse finale, sans :

- présenter une sortie NCM comme un fait ou comme une vérité majoritaire ;
- fusionner des poids, tokenizers, embeddings ou espaces latents ;
- exécuter/télécharger un runtime absent ;
- stocker de nouvelles données personnelles ;
- revendiquer une hausse d'intelligence, de factualité ou de qualité sans
  évaluation annotée.

La sortie NCM est toujours une proposition `NON_VERIFIE`. Le vérificateur doit
l'évaluer séparément contre les documents, faits symboliques et calculs exacts
locaux ; la réponse finale ne peut retenir que ce qui est déjà traçable dans
ces sources. Le rôle du NCM est donc un signal de *contrôle/attention*, pas une
autorité épistémique.

## Séquencement et barrières

1. **État initial / tests de régression — Atlas + Aletheia**
   - Exécuter compilation, tests unitaires, benchmark structurel et scénarios
     dégradés ; consigner les limites et les modules indisponibles.
   - Définir des invariants testables : provenance, séparation
     propositions/faits, bornage de la correction, pipeline ordonné,
     fonctionnement sans actif NCM.
2. **Contrat NCM local — Daedalus + Atlas**
   - Ajouter un contrat JSON versionné `reasoning_refinement` qui ne transporte
     que du texte et des IDs d'artefacts ; chaque modèle conserve son tokenizer.
   - Garder la capacité `non_validated` jusqu'à ce qu'un opérateur fournisse un
     runner, un chemin local et un test d'intégration réel.
3. **Contrôle de raisonnement — Logos + Mnemosyne**
   - Faire produire au NCM des cibles de revue et un plan de synthèse, jamais un
     fait. Le vérificateur examine ces cibles indépendamment et marque les
     absences de preuve comme inconclusives.
   - Conserver le candidat NCM dans le registre de propositions avec
     provenance, incertitude et liens vers le dossier de raisonnement.
4. **Composition et observabilité — Pharos + Atlas**
   - Exposer l'état, les cibles contrôlées et les limites dans la trace
     développeur. La réponse normale n'affirme pas qu'un texte NCM est vérifié.
5. **Ablations / décision d'activation — Aletheia**
   - Comparer `uca_full` et `uca_without_ncm` sur des tâches annotées, mêmes
     actifs et mêmes budgets. Rapporter séparément couverture de vérification,
     précision humaine, cohérence, coût/latence et erreurs ; laisser les
     métriques sans annotations à `null`.
   - Une activation requiert contrat validé, résultats reproductibles et revue
     humaine ; elle ne découle pas du simple passage des tests structurels.

## Matrice de responsabilité

| Rôle | Livrable avant intégration | Preuve exigée | Ne doit pas faire |
|---|---|---|---|
| Atlas | intégration, garde-fous, tests de régression | diff, tests, trace de module | simuler un runner ou un gain qualitatif |
| Mnemosyne | cas d'évidence/provenance et mémoire explicite | fixtures locales, requêtes FTS | écrire une mémoire depuis le chat |
| Logos | invariants faits/propositions et cas de conflit | tests de non-promotion | déduire l'opposé d'une absence |
| Daedalus | shim NCM local et contrat de version | chemin local, commande, sortie JSON | télécharger ou deviner une architecture |
| Aletheia | tâches annotées, ablations et protocole | jeux versionnés, rapport | produire une note de vérité non étayée |
| Pharos | trace/UI des états et limites | test UI/API | masquer une indisponibilité |

## Rythme de coordination

- Toute prise en charge exige inscription dans `coordination/contacts/AGENT_REGISTRY.md`, réservation d'une seule tâche dans `BACKLOG.md`, et entrée de démarrage dans `HANDOFFS.md`.
- Les propositions qui changent `types.py`, `engine.py`, `pipeline.py` ou un contrat JSON sont d'abord ajoutées à `DECISIONS.md` avec alternatives et risques.
- Atlas intègre seulement des changements avec un test ciblé, la suite complète
  et un état honnête des actifs. En l'absence de réponse, il peut avancer sur
  les garde-fous et fixtures synthétiques, mais pas prétendre effectuer le
  travail assigné aux rôles réservés.

## Résultats structurels observés (sans prétention qualitative)

- **Avant intégration :** compilation et 22 tests unitaires réussis ; benchmark
  structurel de deux tâches pour `uca_full_staged_parallel` et
  `uca_without_ncm` réussi en mode dégradé ; pipeline de 11 étapes et NCM
  désactivé.
- **Après intégration :** compilation et 27 tests unitaires réussis ; les mêmes
  deux variantes et tâches passent leurs invariants structurels avec un pipeline
  de 12 étapes. `uca_without_ncm` retire désormais les deux étapes NCM.
- **Fixture locale :** un petit shim Python temporaire a exercé le contrat
  `reasoning_refinement`, la non-promotion en fait, l'ancrage documentaire
  indépendant et la correction bornée. Ce shim n'est ni un checkpoint NCM, ni
  une évaluation de la qualité de réponse.
- **État par défaut :** `ncm_reasoning_refinement` est
  `disabled_voluntarily`; aucun runner/checkpoint réel, corpus annoté ou score
  qualitatif n'est disponible.

## Critères de fini UCA-11

- le pipeline contient une étape NCM de contrôle reliée au dossier de
  raisonnement et à la vérification ;
- cette étape est désactivée/non validée par défaut sans runner réel ;
- chaque proposition NCM reste explicitement non vérifiée et hors du bin de
  faits ;
- un test local de shim exerce le contrat sans le confondre avec un modèle réel ;
- les ablations incluent l'absence de **toutes** les étapes NCM ;
- les résultats d'évaluation distinguent structure, disponibilité et qualité
  annotée.
