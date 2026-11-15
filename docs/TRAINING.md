# Gouvernance et entraînement d'adaptateur UCA

## Portée actuelle

UCA implémente un chemin explicite d'entraînement **LoRA séparé** pour un
checkpoint local existant `SmolLM2-360M-Instruct`. Il ne crée pas de modèle
étudiant, ne distille pas d'autre modèle, ne télécharge aucun actif et ne fusionne
jamais les poids de l'adaptateur avec le checkpoint de base.

Le code est dans `uca/training.py`. L'entraînement reste désactivé par défaut.

## Préflight obligatoire

```bash
python -m uca training-preflight --root .
```

Le préflight ne charge aucun modèle. Il contrôle :

- checkpoint local et tokenizer local ;
- dataset JSONL, IDs, texte non vide, source et licence par record ;
- SHA-256 du dataset ;
- manifeste d'approbation ;
- interdiction explicite de distillation ;
- interdiction de mémoire utilisateur dans le dataset ;
- modules cibles LoRA explicitement déclarés ;
- sortie distincte et vide.

Un préflight bloqué est le comportement attendu tant que les chemins de la
configuration sont vides. Il ne faut pas contourner ces erreurs.

## Manifeste

Copiez `training/manifest.template.json` en dehors des fichiers de démonstration.
Exécutez le preflight une première fois pour obtenir
`base_checkpoint_fingerprint`, puis renseignez cette valeur, le hash du dataset
réel, l'approbateur et les confirmations. Le manifest doit contenir exactement :

```json
{
  "schema": "uca.training-manifest.v1",
  "target": "smollm2_360_lora",
  "base_model_id": "SmolLM2-360M-Instruct",
  "base_checkpoint_fingerprint": "…",
  "dataset_sha256": "…",
  "distillation": false,
  "contains_user_memory": false,
  "data_rights_confirmed": true,
  "approved_by": "…"
}
```

## Exécution explicite

Après préflight réussi, dans un environnement local déjà préparé avec les dépendances de modèle :

```bash
python -m uca train-lora-adapter --root . --confirm I_CONFIRM_LOCAL_TRAINING
```

La phrase de confirmation évite le lancement accidentel. La commande écrit un
adaptateur LoRA local séparé (`uca.local-lora.v1`), une référence de tokenizer,
un manifest de compatibilité non validé et un rapport de run dans
`training.output_dir`. Elle ne fusionne pas l'adaptateur avec les poids de base.

## Déploiement et évaluation

Ne déclarez jamais un adaptateur utile seulement parce que la perte baisse. Avant
activation, il faut au minimum :

1. un jeu de validation séparé et documenté ;
2. un benchmark base vs adaptateur ;
3. une revue des réponses factuelles, de la sécurité, de la cohérence et des
   régressions linguistiques ;
4. des mesures de temps, RAM et VRAM ;
5. un manifest de compatibilité avec le checkpoint exact.

Les modules TIES/DARE ne sont pas utilisés par cette commande. Ils restent des
techniques d'administration distinctes, à valider séparément.
