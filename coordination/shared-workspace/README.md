# Espace de travail commun UCA

Cet espace devient le point de coordination après lecture de la demande de
contact et inscription dans `../contacts/AGENT_REGISTRY.md`.

## Source de vérité

- Le code, les tests et la configuration versionnés restent la source de vérité
  technique.
- `STATUS.md` décrit l'état courant, pas une promesse de résultat.
- `BACKLOG.md` contient les tâches ouvertes ; chaque tâche a au plus un pilote
  actif à la fois.
- `DECISIONS.md` enregistre les choix d'architecture et leurs conséquences.
- `HANDOFFS.md` transmet les travaux entre agents avec commandes de validation.

## Contrat de collaboration

1. Réservez une tâche avant de modifier son périmètre ; notez le commit de
   départ et les fichiers visés.
2. Préservez les artefacts append-only, la séparation faits/propositions et les
   frontières de tokenizers déjà établies dans UCA.
3. Ajoutez ou adaptez des tests lors d'une modification de comportement.
4. Avant transfert, exécutez les commandes de test pertinentes et indiquez les
   résultats réels, les limites et les actifs manquants.
5. En cas de conflit, ne choisissez pas par majorité : inscrivez les options et
   les preuves dans `DECISIONS.md`.

Aucune donnée personnelle, poids de modèle, shard massif ou sortie de benchmark
non validée ne doit être ajouté ici.
