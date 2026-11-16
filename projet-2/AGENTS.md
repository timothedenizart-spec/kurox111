# Agents — Projet 2

## Rôles suggérés

| Rôle | Responsabilité |
| --- | --- |
| `coordination` | Découpe le travail, arbitre les dépendances et maintient le tableau |
| `analyse` | Clarifie le besoin, les risques et les critères d’acceptation |
| `implementation` | Réalise une tâche réservée dans son périmètre |
| `verification` | Relit les changements et exécute les contrôles nécessaires |
| `documentation` | Met à jour les guides, décisions et notes de livraison |

Un même agent peut tenir plusieurs rôles, mais ne doit réserver qu’une seule tâche de production à la fois.

## Protocole de réservation

1. Vérifier que la tâche est dans la colonne **À faire** et sans dépendance bloquante.
2. Écrire dans `TABLEAU.md` : `Responsable : <identifiant> — réservé le <YYYY-MM-DD HH:MM UTC>`.
3. Déplacer la tâche dans **En cours**.
4. Noter dans `JOURNAL.md` l’objectif, le périmètre et les fichiers prévus.

Une réservation expire après 24 heures sans mise à jour. Le coordinateur peut alors la remettre à disposition en laissant une trace dans le journal.

## Protocole de relais

Lorsqu’une tâche est prête :

- la déplacer dans **À relire** ;
- indiquer le résumé des changements, les contrôles effectués et les limites connues ;
- lier les décisions pertinentes ;
- laisser un message de relais dans `JOURNAL.md`.

Le relecteur ne modifie pas le périmètre de la tâche sans l’inscrire au préalable dans le journal.

## Conventions

- Toutes les dates sont en UTC au format `YYYY-MM-DD HH:MM`.
- Les faits, hypothèses et décisions sont distingués explicitement.
- Les blocages sont signalés immédiatement dans le tableau et le journal.
- Les informations sensibles ne sont jamais consignées dans cet espace.
