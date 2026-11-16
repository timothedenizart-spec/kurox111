# Cahier des charges — Projet 2 : jeu d'apocalypse pandémique

> Reformulation fidèle de la demande de l'utilisateur (2026-11-16). Ce document **décrit le besoin**, il ne fixe aucune solution technique.
> Toute modification d'une exigence doit être validée par l'utilisateur et inscrite dans [`DECISIONS.md`](DECISIONS.md).

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

## Hors périmètre à ce stade

- Pas de choix du moteur, de la plateforme, de la 2D ou de la 3D, ni de la direction artistique avant validation (voir [`QUESTIONS_OUVERTES.md`](QUESTIONS_OUVERTES.md)).
- **Aucun travail de production** (code, assets, conception détaillée) avant le feu vert de l'utilisateur (décision D-P2-001).
