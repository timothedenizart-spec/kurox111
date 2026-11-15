# Lots de préparation à l'entraînement

| Lot | Propriétaire / session proposée | État | Livrable vérifiable |
|---|---|---|---|
| TR-00 — choisir tâche cible, model/checkpoint et budget | propriétaire du projet + MOSAIC-Lead (`arena/f2ae664d-kurox111`) | bloqué : checkpoint absent, confirmation demandée | décision et manifest d'expérience, hash du modèle, objectif et seuils |
| TR-01 — ingestion sûre et validator dataset | Intake-Security (`arena/3cdf297b-kurox111`) | commencé | schéma `DATA_SPEC.md`, validateur JSONL stdlib + tests |
| TR-02 — pipeline d'adaptation LoRA | Parallel-Runtime (`arena/8e5e2ae2-kurox111`) | proposé / non confirmé | script reproductible local, env pin, checkpoint immuable, output adapter |
| TR-03 — jeu raisonnement vérifiable | Arena-NeuroMathArchitect (`arena/de272f1c-kurox111`) | proposé / non confirmé | données synthétiques revues, split par règle, test non exposé |
| TR-04 — jeu d'évaluation mémoire | Préfrontal (`arena/57dad57f-kurox111`) | proposé / non confirmé | benchmark distinct du contenu mémoire personnel; mesure de rappel/oubli |
| TR-05 — baseline, métriques et gate de promotion | MOSAIC-Lead (`arena/f2ae664d-kurox111`) | proposé / non confirmé | protocole comparatif base vs adapter, coûts, seuils, rapport |

## Gate de démarrage

Aucun lot TR-02 ne peut lancer le calcul avant clôture de TR-00, validation par TR-01 et confirmation du dépôt des poids/données. Chaque agent confirme tâche et fichiers concernés dans l'issue #1. Aucun modèle n'est téléchargé ou entraîné automatiquement.
