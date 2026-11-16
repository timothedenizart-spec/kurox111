# Contrats de travail entre pôles

## Vocabulaire partagé

- **Jour réel** : vingt-quatre heures écoulées depuis le début de la partie. Le prototype ne convertit pas arbitrairement une minute en une journée de survie.
- **Signal** : indice ressenti ou observé (phrase, animation, son, comportement, horaire, environnement). Un signal n’est pas une jauge.
- **État caché** : information de simulation utilisable par les systèmes, mais jamais affichée de façon clinique au joueur.
- **Phase** : moment global de la crise. Elle modifie les probabilités, les commerces et le langage du monde sans annuler l’historique du joueur.

## Interface minimale de simulation

Chaque habitant possède, au minimum :

```text
id, prénom, foyer, métier, quartier, ressources,
mobilité, confiance, contacts[], lieuCourant,
étatSanitaire, exposition{lieu, instant, source},
dernièreMiseÀJour, mémoireCourte[]
```

L’état sanitaire reste interne : `sain`, `exposé`, `incubation`, `symptomatique`, `grave`, `disparu`, `altéré`. Les PNJ ne connaissent pas tous l’état des autres ; ils agissent d’après des observations, une rumeur ou leurs intérêts. À chaque heure simulée, un horaire détermine leur présence dans un lieu ; l’exposition n’est possible qu’en présence d’un contact infectieux dans ce même lieu.

Une rumeur du monde possède :

```text
instant, texte, source, degréDIncertain, relais[]
```

La source et l’incertitude sont des éléments jouables. Elles ne doivent jamais être remplacées par un « vrai / faux » omniscient dans l’interface.

Chaque relation du joueur possède :

```text
affinitéInterne, dernierGeste, dernierInstant,
mémoirePartageable, confianceDuPNJ
```

L’affinité reste une donnée interne : le joueur lit seulement une formulation qualitative telle que « vous vous connaissez à peine » ou « un lien de confiance se construit ».

Le stock d’un commerce possède :

```text
articles{}, dernierArrivage, noteDeLivraison,
jourLogistiqueTraité
```

Les clients ne voient jamais la valeur brute des rayons. Atlas expose plutôt des indices : comptoir réduit, derniers articles, arrivage incomplet ou fermeture.

Chaque besoin du joueur possède :

```text
dernièreAction, intervalleConfort, intervalleAlerte,
intervalleCritique, indices[phase], conséquenceContextuelle
```

L’interface ne lit que `indices` et les conséquences ; elle ne rend ni compteur ni valeur normalisée.

## Ordre d’intégration

1. **Chronos** fournit `elapsedRealHours`, la sauvegarde et l’horloge visible si le joueur a une montre.
2. **Vigile** met à jour les besoins à partir des derniers instants d’action.
3. **Épidémie** applique les transitions sanitaires des habitants à chaque heure écoulée.
4. **Civitas** choisit les déplacements, interactions, achats et réactions selon l’état du monde.
5. **Atlas** calcule disponibilité, prix, horaires et statut des lieux.
6. **Nocturne** transforme le résultat en texte, ambiance et événements observables.

## Garde-fous de conception

- Pas de diagnostic médical réel, pas de notice thérapeutique, pas de pseudo-conseil de santé.
- Les besoins naturels sont traités avec sobriété et consentement : fatigue, intimité, sécurité et dignité sont prioritaires à l’effet de choc.
- La mutation vers des comportements « zombies » est fictionnelle ; elle ne prétend pas décrire une pathologie existante.
- La souffrance humaine n’est pas une récompense : l’entraide, la préparation et les choix sociaux doivent aussi être viables.
