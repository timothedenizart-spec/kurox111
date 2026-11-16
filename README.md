# kurox111

## Projet 2 — coordination des agents (jeu d’apocalypse pandémique)

L’espace de coordination, de dépôt et de relais se trouve dans [`projet-2/`](projet-2/). La livraison actuelle est le prototype jouable **V0.3**.

- [Accueil et règles de coordination](projet-2/README.md)
- [Livraison V0.3 et relais](projet-2/LIVRAISON_V0.3.md)
- [Tableau des tâches](projet-2/TABLEAU.md)
- [Protocole des agents](projet-2/AGENTS.md)
- [Journal des transmissions](projet-2/JOURNAL.md)
- [Décisions](projet-2/DECISIONS.md)
- [Brief de production](projet-2/BRIEF.md)

## Prototype jouable

La démo web ne nécessite aucune dépendance externe :

```bash
python3 -m http.server 4173 --bind 0.0.0.0
```

Puis ouvrir `http://localhost:4173`. Les vérifications automatisées s’exécutent avec :

```bash
npm test
```
