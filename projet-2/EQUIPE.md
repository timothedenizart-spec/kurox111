# Équipe des agents — Projet 2

Registre officiel des agents, de leur nom, de leur rôle et de leur branche.
**Règle :** un rôle n'est attribué qu'après une déclaration explicite de l'agent dans le canal de coordination (issue GitHub « Projet 2 — coordination des agents ») **et** ici.
Premier arrivé, premier servi. Un agent peut demander un échange de rôle dans le canal.

## Rôles et noms

| Nom de l'agent | Rôle | Responsabilités principales | Exigences couvertes | Branche | Statut |
| --- | --- | --- | --- | --- | --- |
| **Sentinelle** | Coordination & intégration | Tient le tableau, le journal, le registre ; arbitre les dépendances et les interfaces entre systèmes ; seule à fusionner vers la branche d'intégration après relecture ; relais avec l'utilisateur | Toutes (cohérence) | `arena/458e1a3c-kurox111` | ✅ Confirmé |
| **Pathogène** | Épidémiologie & mutation | Modèle de transmission (contacts, voies, charge infectieuse, incubation, létalité), exposition des habitants, chronologie des mutations vers l'infection zombie | E-01, E-02, E-03 | — | 🟡 Poste ouvert |
| **Organisme** | Physiologie & besoins | Faim, soif, sommeil, hygiène, besoins naturels, envies ; horloge biologique ; indices sans jauge qui s'intensifient ; montre facultative | E-07 à E-11 | — | 🟡 Poste ouvert |
| **Cité** | Population & PNJ intelligents | Habitants simulés individuellement (routines, mémoire, perception, peur, décisions, rumeurs), réaction collective à l'épidémie | E-04, E-02 | — | 🟡 Poste ouvert |
| **Marché** | Économie & effondrement | Revenus, prix, pénuries, inflation, fermeture progressive des commerces, perte de valeur de la monnaie, passage au troc | E-05, E-06 | — | 🟡 Poste ouvert |
| **Monde** | Moteur, temps & immersion | Architecture du jeu, boucle de simulation et échelle de temps, carte, rendu, son, ambiance sombre, interface sans jauge | E-08, E-12 | — | 🟡 Poste ouvert |
| **Vigie** | Réalisme, tests & sources | Vérifie les sources scientifiques des paramètres, écrit et lance les tests, assure l'équilibrage et relit chaque livraison | Toutes (qualité) | — | 🟡 Poste ouvert |

> Si moins de 7 agents sont présents, un agent peut cumuler deux rôles, en respectant cet ordre de cumul : Pathogène + Vigie, Organisme + Monde, Cité + Marché. Il ne réserve tout de même qu'**une seule tâche de production à la fois** (voir [`AGENTS.md`](AGENTS.md)).

## Interfaces entre rôles (à contractualiser avant tout code)

| Producteur → Consommateur | Donnée échangée |
| --- | --- |
| Monde → tous | Horloge de simulation (temps de jeu, rythme jour/nuit) |
| Pathogène ↔ Cité | Contacts et lieux fréquentés → risque d'exposition ; état infectieux → comportement |
| Pathogène → Organisme | Symptômes du joueur (fièvre, fatigue, perte d'appétit…) qui modifient les besoins et les indices |
| Pathogène → Marché | Phase épidémique → absentéisme, fermetures, pénuries |
| Marché ↔ Cité | Emplois, revenus, stocks, prix → décisions des PNJ (pillage, fuite, entraide) |
| Organisme → Monde | Indices perceptifs à afficher ou à faire entendre (vision floue, ventre qui gargouille, odeur…) |
| Vigie → tous | Fiches de sources, tests de réalisme, verdict de relecture |

## Déclaration attendue de chaque agent

À poster dans le canal de coordination :

```md
## Déclaration — <Nom choisi>
- Rôle revendiqué :
- Branche + commit :
- Compétences / outils prévus :
- Rôle de repli si déjà pris :
- Disponibilité / limites connues :
```
