# Évaluation structurelle et épistémique d'UCA

`uca.evaluation.evaluate_context` inspecte une exécution terminée sans la
modifier. Son objectif est de détecter des régressions d'architecture avant de
faire des affirmations sur la qualité d'une IA.

## Ce qui est vérifié

- unicité des identifiants d'artefacts ;
- présence du producteur et résolution des dépendances déclarées ;
- séparation entre propositions générées et faits symboliques ;
- identifiant, contenu et provenance pour chaque document ;
- portée et statut des calculs exacts ;
- présence d'une réponse finale unique ;
- topologie d'exécution déclarée ;
- trace de fanout quand `staged_parallel` est demandé ;
- attentes propres à une tâche : calcul exact, topologie, fanout et minimum de
  sources documentaires.

Les attentes se placent dans un JSONL de benchmark :

```json
{
  "id": "exact-rational-001",
  "prompt": "Calcule 2*(3+4)/5",
  "expectations": {
    "expected_exact_computation": "14/5",
    "expected_topology": "staged_parallel",
    "require_parallel_fanout": true
  }
}
```

Lancez l'exemple local :

```bash
python -m uca benchmark benchmarks/architecture-invariants.example.jsonl \
  --variants uca_full_staged_parallel
```

Le rapport contient `structural_evaluation`. Un statut
`completed_with_structural_violations` signale une violation d'invariant, même
si l'exécution a produit une réponse.

## Ce que cela ne mesure pas

Cette évaluation ne mesure pas l'intelligence, la factualité générale, la
sécurité, la cohérence linguistique, la profondeur de raisonnement ou la valeur
d'un modèle. Ces dimensions demandent des tâches annotées, des sources réelles,
des juges validés et, selon le cas, une revue humaine. Une réussite structurelle
ne doit jamais être présentée comme une amélioration de qualité de modèle.
