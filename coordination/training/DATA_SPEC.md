# Schéma de données supervisées — UCA

Un fichier UTF-8 JSONL, une conversation par ligne. Exemple de structure :

```json
{"id":"ex-0001","split":"train","source":"source précise et vérifiable","license":"CC-BY-4.0","messages":[{"role":"user","content":"Calcule 19 × 23."},{"role":"assistant","content":"437"}]}
```

## Obligatoire

- `id` : identifiant stable, unique dans tout le dataset.
- `split` : exactement `train`, `validation` ou `test`.
- `source` : origine et identifiant du document / générateur, non vide.
- `license` : licence ou autorisation vérifiable, non vide ; `unknown`/`inconnue` ne passe pas le gate.
- `messages` : liste de `{role, content}` avec rôles `system`, `user`, `assistant`; au moins un message utilisateur et une réponse assistant finale non vide.

Les métadonnées sont extensibles, mais ne doivent pas inclure secret/token. Le validateur détecte erreurs de schéma, IDs répétés et conversations identiques entre splits. Il ne peut pas déterminer la légalité, la véracité, la qualité pédagogique, la présence de données personnelles ni la contamination paraphrasée : revue humaine nécessaire.

## Partitionnement et qualité

- Split par document/source/générateur avant la génération de variantes ; ne pas envoyer des reformulations quasi identiques vers train et test.
- Dédupliquer exact et quasi-doublons ; conserver la référence canonique et la trace de transformation.
- Les cibles de raisonnement doivent avoir une réponse vérifiée indépendamment (calcul exact, preuve/outil ou annotateur qualifié) et inclure des cas ambigus / impossibles où l'abstention est la bonne réponse.
- Pour chaque lot, documenter auteur, langue, domaine, méthode de collecte, droits, date, filtres, limites et hash du fichier.
- Le set test reste privé/gelé pour éviter l'optimisation accidentelle.
- Écarter données personnelles, conversations privées ou secrets par défaut. Une revue manuelle reste obligatoire même si le validateur indique `valid`.

## Validation locale

```bash
python3 scripts/validate_training_data.py coordination/training/training.jsonl
```

Le validateur ne déclenche aucun entraînement et n'importe pas de dépendance ML.
