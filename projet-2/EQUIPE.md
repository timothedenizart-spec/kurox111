# Rôles canoniques et correspondance historique — Projet 2

Les noms ci-dessous servent à attribuer et retrouver les contributions dans les documents et branches. Plusieurs noms ont été proposés dans des branches différentes; ils sont normalisés ici pour éviter les doubles affectations. Ils ne signifient pas que plusieurs agents autonomes ont participé à cette conversation.

## Rôles canoniques

| Nom canonique | Domaine | Responsabilités |
| --- | --- | --- |
| **ORBIT** | Coordination et intégration | Tableau, journal, dépendances, provenance, arbitrages et relais vers la personne responsable. |
| **LYRA** | Expérience et narration | Ton, rythme, information diégétique, rencontres et compréhension du joueur. |
| **ATLAS** | Simulation systémique | Phases du monde, liens entre crise, lieux, populations et services. |
| **NOVA** | Habitants et relations | Routines, perception, objectifs, mémoire, entraide et comportements des PNJ. |
| **MINT** | Économie et services | Revenu, prix, stocks, commerces, logistique et évolution des échanges. |
| **VITA** | Survie et confort | Faim, soif, repos, hygiène, besoins naturels, envies, indices et accessibilité sans jauges. |
| **FORGE** | Technique et intégration | Architecture, horloge, persistance, interface, performance et outils. |
| **ARGUS** | Vérification et cohérence | Tests, critères d’acceptation, revue croisée et traçabilité des risques. |

## Correspondance des alias rencontrés

| Alias ou rôle de branche | Rôle canonique le plus proche | Source / note |
| --- | --- | --- |
| **Sentinelle** (branche `arena/458e1a3c`) | ORBIT | Coordination/intégration. L’alias apparaît aussi pour la qualité dans une proposition initiale; ne pas le compter comme deux personnes. |
| **Pathogène**, **Épidémie** | ATLAS | Domaine de simulation fictionnelle de crise; ne constitue pas un modèle médical réel. |
| **Organisme**, **Vigile** | VITA | Besoins corporels et signaux sans jauge. |
| **Cité**, **Civitas**, **Noroît** | NOVA | Noroît a déclaré le rôle Cité dans l’issue #3, branche `arena/ef1aae95`; son prototype est archivé pour revue. |
| **Marché** | MINT | Économie et commerces. |
| **Monde**, **Chronos** | FORGE | Plateforme, temps, moteur et infrastructure; les décisions produit restent à valider. |
| **Vigie** | ARGUS | Tests et relecture. |
| **Orion**, **Nocturne**, **Éclipse** | Alias historiques de coordination, expérience ou prototype | Présents dans les documents de `arena/1dbdd8bb`; conservés comme provenance, non comme affectations distinctes. |

## Déclarations et limites

- La PR #2 documente un travail attribué fonctionnellement à ORBIT, LYRA, ATLAS, NOVA, MINT, VITA, FORGE et ARGUS; voir son historique et `JOURNAL.md`.
- La branche `arena/458e1a3c` a consigné un roster proposé où la plupart des postes restaient ouverts.
- L’issue #3 contient une déclaration de rôle Cité/Noroît, avec une mise en garde explicite qu’un seul agent est actif dans cette session.
- La branche `arena/1dbdd8bb` emploie des noms de pôles propres à son prototype; ses fichiers sont dans `contributions/arena-1dbdd8bb/`.

Les rôles sont des fonctions de travail. Une décision de produit revient à la personne responsable; une tâche concrète doit avoir un seul responsable de coordination et des fichiers/faits vérifiables.
