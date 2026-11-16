# Cahier des charges — Projet 2 : jeu d'apocalypse pandémique

> Reformulation de la demande de l'utilisateur (2026-11-16). Ce document **décrit le besoin**; il distingue les exigences de la solution technique.
> La production a depuis été autorisée par l'utilisateur; le prototype web V0.3 est une tranche exploratoire, pas une validation de tous les choix produit. Toute modification d'exigence reste à consigner dans [`DECISIONS.md`](DECISIONS.md).

## Vision

Un jeu de survie **très réaliste et immersif** : le joueur vit dans un monde sombre où une maladie très mortelle et très contagieuse apparaît, puis **mute progressivement** jusqu'à devenir une **infection zombie**. On passe petit à petit de la survie face à une épidémie à une apocalypse zombie.

**Priorité absolue : le réalisme.**

## Exigences de l'utilisateur

| ID | Domaine | Exigence |
| --- | --- | --- |
| E-01 | Épidémie | Contamination **progressive** et réaliste dans la population. |
| E-02 | Épidémie | **Exposition simulée** des habitants (contacts, lieux, contamination). |
| E-03 | Épidémie | La maladie **mute au fil du jeu** : d'abord une maladie mortelle et contagieuse, puis une évolution graduelle vers une infection zombie. |
| E-04 | Population | Habitants et **PNJ très intelligents**, simulés individuellement. |
| E-05 | Économie | L'économie **s'effondre de façon réaliste** : au début l'argent compte et il faut en gagner ; à la fin il n'a plus aucune valeur. |
| E-06 | Économie | Les **commerces et magasins ferment petit à petit**. |
| E-07 | Besoins | Faim, soif, sommeil, hygiène et besoins naturels (uriner, déféquer). |
| E-08 | Besoins | **Aucune jauge** à l'écran. Le joueur ne connaît l'heure que s'il possède une **montre** ; le temps qui passe est son seul repère. |
| E-09 | Besoins | Les intervalles s'appuient sur les **intervalles réels** d'un être humain entre chaque besoin. |
| E-10 | Besoins | Chaque besoin se manifeste par des **indices** (signes corporels, perceptifs, comportementaux) qui **s'intensifient** au fil du temps. |
| E-11 | Besoins | Un **système d'envies naturelles** de toutes sortes (envies alimentaires, de repos, de confort, sociales, etc.). |
| E-12 | Ambiance | Monde **sombre** et immersif. |

## État actuel et décisions encore ouvertes

- L'utilisateur a ensuite demandé de poursuivre le travail; le prototype web local V0.3 est une première tranche exploratoire documentée dans [`LIVRAISON_V0.3.md`](LIVRAISON_V0.3.md).
- Le web et le solo sont retenus uniquement comme périmètre provisoire du prototype. Le moteur final, la vue, l'échelle temporelle et la direction artistique restent à valider (voir [`QUESTIONS_OUVERTES.md`](QUESTIONS_OUVERTES.md)).
- Les exigences E-01 à E-12 demeurent le besoin produit; elles ne signifient pas que toutes sont déjà implémentées. Les éléments réalisés sont décrits dans la livraison et l'inventaire des contributions.
