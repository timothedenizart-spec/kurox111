# Tableau de coordination — Projet 2

> **Phase 1 active : prototype V0.3.** La démo web locale associe désormais besoins sans jauges, habitants contextuels, économie déclinante, entraide, abri et événements de quartier.

## Coordination terminée

| ID | Élément | Responsable | État | Référence |
| --- | --- | --- | --- | --- |
| P2-C00 | Nommer l’équipe, séparer les rôles et établir le circuit de décision | ORBIT | Terminé | [`AGENTS.md`](AGENTS.md) |
| P2-001 | Cadrer le besoin et les critères de réussite de V0.1 | ORBIT + LYRA | Terminé | [`BRIEF.md`](BRIEF.md) |
| P2-002 | Construire la boucle jouable et l’horloge diégétique | FORGE + VITA | Terminé | `index.html`, `app.js` |
| P2-003 | Construire la simulation des habitants et les phases de crise | ATLAS + NOVA | Terminé V0.3 | `simulation.js` |
| P2-004 | Vérifier les règles, l’accessibilité et l’absence de jauges | ARGUS | Terminé V0.3 | `tests/simulation.test.mjs` |
| P2-005 | Intégrer l’économie et les services qui s’éteignent | MINT | Terminé V0.2 | `simulation.js` |
| P2-006 | Ajouter les choix d’abri, d’information et d’événements de quartier | LYRA + ATLAS + VITA | Terminé V0.3 | `simulation.js`, `app.js` |

## En cours

| ID | Élément | Responsable | Dépendances | Prochaine sortie attendue |
| --- | --- | --- | --- | --- |
| P2-007 | Enrichir les relations persistantes et les comportements propres à chaque habitant | NOVA + LYRA | P2-003, P2-006 | Rencontres plus différenciées et conséquences sociales durables |

## En attente

| ID | Élément | Responsable | Dépendances | État |
| --- | --- | --- | --- | --- |
| P2-008 | Évaluer les retours de jeu et prioriser la V0.4 | ORBIT + ARGUS | Test de V0.3 | Non commencée |
| P2-009 | Choisir si un moteur de jeu dédié est nécessaire après validation de la boucle | FORGE | Retours V0.3 et V0.4 | Non commencée |

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
| P2-006 | Prototype V0.3 : signaux de quartier, radio, abri et refuge | LYRA + ATLAS + VITA + ARGUS | 2026-11-16 | `simulation.js`, `app.js`, `tests/` |
