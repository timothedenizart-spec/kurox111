# Exécution parallèle bornée — prototype WCP-03

## État

Prototype opt-in, non activé par défaut et non encore évalué avec des modèles/runner réels. Ce mécanisme optimise l'ordonnancement ; il ne rend pas les modèles sous-jacents plus capables par lui-même.

## Contrat

- L'opérateur déclare des `parallel_groups` ordonnés dans la configuration. Aucune tâche n'est parallélisée automatiquement par estimation sémantique.
- Un groupe ne peut contenir de relation de dépendance entre ses membres. Le moteur rejette ces groupes au démarrage.
- Tous les modules d'un groupe reçoivent une copie profonde indépendante du même snapshot, pris avant le démarrage du groupe.
- Chaque module retourne un `ModuleResult` isolé. Seul le moteur central fusionne les artefacts, dans l'ordre du pipeline, jamais selon l'ordre d'arrivée.
- Les modules absents/invalides et les exceptions sont rapportés individuellement. Un timeout reste « soft » (Python ne tue pas arbitrairement un thread) ; le résultat tardif n'est pas fusionné et son thread n'a accès qu'à sa copie.
- `max_parallel_workers` borne le nombre de workers. Le déchargement des ressources est fait après les fusions, sur le thread de coordination.
- La réponse et les statistiques d'exécution conservent la même frontière de provenance que le mode séquentiel.

## Activation locale

Dans `config/uca.toml`, après inspection des capacités des ressources locales :

```toml
[engine]
parallel_enabled = true
parallel_groups = [["user_memory", "knowledge_retrieval", "symbolic_processing", "ncm_concept_generation"]]
max_parallel_workers = 4
```

L'activation expérimentale n'est pas recommandée avec des runners qui mutent un état global ou partagent un même périphérique sans contrôle de concurrence. Le mode séquentiel reste la référence (`parallel_enabled = false`).

## Tests présents et tests encore requis

La suite vérifie l'exécution chevauchée via une barrière, l'isolation des snapshots, la fusion déterministe et le rejet d'une dépendance interne au groupe. Il reste à tester timeouts/erreurs simultanés, runners réels thread-safe, contention RAM/VRAM, accélérations et résultats qualité à budget identique. Aucun gain de performance n'est encore revendiqué.
