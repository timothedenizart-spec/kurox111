# Tableau de coordination — Projet 2

> **Phase 1 active : prototype V0.2.** La démo web locale teste maintenant la boucle temps, les besoins sans jauges, les habitants contextuels, l’économie déclinante et les liens d’entraide.

## Coordination terminée

| ID | Élément | Responsable | État | Référence |
| --- | --- | --- | --- | --- |
| P2-C00 | Nommer l’équipe, séparer les rôles et établir le circuit de décision | ORBIT | Terminé | [`AGENTS.md`](AGENTS.md) |
| P2-001 | Cadrer le besoin et les critères de réussite de V0.1 | ORBIT + LYRA | Terminé | [`BRIEF.md`](BRIEF.md) |
| P2-002 | Construire la boucle jouable et l’horloge diégétique | FORGE + VITA | Terminé | `index.html`, `app.js` |
| P2-003 | Construire la simulation des habitants et les phases de crise | ATLAS + NOVA | Terminé V0.2 | `simulation.js` |
| P2-004 | Vérifier les règles, l’accessibilité et l’absence de jauges | ARGUS | Terminé V0.2 | `tests/simulation.test.mjs` |
| P2-005 | Intégrer l’économie et les services qui s’éteignent | MINT | Terminé V0.2 | `simulation.js` |

## En cours

| ID | Élément | Responsable | Dépendances | Prochaine sortie attendue |
| --- | --- | --- | --- | --- |
| P2-006 | Préparer la prochaine boucle de survie : abri, informations et événements de quartier | LYRA + ATLAS + VITA | P2-002 à P2-005 | Choix jouables supplémentaires, toujours sans jauges |

## En attente

| ID | Élément | Responsable | Dépendances | État |
| --- | --- | --- | --- | --- |
| P2-007 | Évaluer les retours de jeu et prioriser la V0.3 | ORBIT + ARGUS | Test de V0.2 | Non commencée |
| P2-008 | Choisir si un moteur de jeu dédié est nécessaire après validation de la boucle | FORGE | Retours V0.2 et V0.3 | Non commencée |

## Bloqué

| ID | Élément | Blocage | Responsable | Depuis le |
| --- | --- | --- | --- | --- |
| — | Aucun blocage signalé | — | — | — |

## À relire

| ID | Élément | Auteur | Relecteur | Contrôles à effectuer |
| --- | --- | --- | --- | --- |
| — | Aucune tâche en attente | — | — | — |

## Terminé

| ID | Élément | Validé par | Date | Référence |
| --- | --- | --- | --- | --- |
| P2-C00 | Coordination initiale | ORBIT | 2026-11-16 | [`AGENTS.md`](AGENTS.md) |
| P2-001 | Brief et périmètre V0.1 | ORBIT + LYRA | 2026-11-16 | [`BRIEF.md`](BRIEF.md) |
| P2-002 à P2-005 | Prototype V0.2 : boucle, habitants, économie et vérifications | FORGE + ATLAS + NOVA + MINT + VITA + ARGUS | 2026-11-16 | `simulation.js`, `app.js`, `tests/` |
