# Équipe, noms de rôle et responsabilités

> Un nom de rôle n'est pas la preuve qu'un agent externe existe. Au 2026-11-15,
> seul **Atlas** (l'orchestrateur de cette session) est inscrit et actif. Les
> rôles réservés ne deviennent actifs qu'après inscription de leur porteur dans
> `../contacts/AGENT_REGISTRY.md` et réservation explicite d'une tâche.

| Nom de rôle | État | Responsabilité | Frontières non négociables | Premier chantier |
|---|---|---|---|---|
| **Atlas** | actif | intégration UCA, contrats d'artefacts, planification, tests de structure et gouvernance d'entraînement | ne fabrique ni actifs, ni résultats de benchmark ; ne lance pas d'entraînement sans manifest | UCA-09 : préflight LoRA local |
| **Mnemosyne** | réservé | mémoire explicite, import FTS5, provenance documentaire | aucune écriture automatique de mémoire utilisateur | UCA-01 |
| **Logos** | réservé | MeTTa, faits opérateurs, contraintes formelles et calcul | absence de fait = inconclusif | UCA-02 |
| **Daedalus** | réservé | checkpoints, adaptateurs, RAM/VRAM, nanoDiff | aucun poids/tokenizer/tensor partagé implicitement | UCA-03 / UCA-04 |
| **Aletheia** | réservé | vérification, jeux de tâches, ablations et statistiques | aucun score de vérité inventé | UCA-05 / UCA-07 |
| **Pharos** | réservé | UI développeur, observabilité, lancement local et reproductibilité | la trace doit rester lisible et non sensible ; ne pas simuler des modèles chargés | UCA-10 : lanceur d'interface |

## Règle de prise de relais

1. L'agent qui prend un rôle s'inscrit avec son alias réel dans le registre.
2. Il réserve une seule tâche principale dans `BACKLOG.md`.
3. Il crée une entrée de prise en charge dans `HANDOFFS.md` avec le commit de
   départ, les fichiers concernés et les commandes prévues.
4. Atlas conserve l'intégration finale lorsque les interfaces centrales
   (`types.py`, `engine.py`, `pipeline.py`, formats de trace) sont concernées.
