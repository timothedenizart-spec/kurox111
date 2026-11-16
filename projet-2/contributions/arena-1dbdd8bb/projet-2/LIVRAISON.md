# Dépôt de travail — incrément 3

> État déposé le 16 novembre 2026 · branche `arena/1dbdd8bb-kurox111`

Ce document est le point de reprise unique pour les pôles de **Projet 2**. Il distingue ce qui est réellement intégré dans le prototype de ce qui reste une intention de conception.

## Objet livré

Le vertical slice web dans [`../game/`](../game/) contient désormais une boucle locale complète :

1. une montre et une sauvegarde en temps réel ;
2. des besoins interprétés par indices, sans jauges ;
3. une propagation fictionnelle par lieux partagés ;
4. un voisinage avec mémoire, réseau de contacts et rumeurs incertaines ;
5. une économie locale avec commerces, stocks internes et tournée de livraison ;
6. des choix de voisinage : parler, aider, transmettre une information ou se retirer.

## Référence de dépôt

| Incrément | Commit | Contenu principal |
| --- | --- | --- |
| Socle | `9f82857` | Prototype web, besoins sans jauges, quartier et phases de crise. |
| Simulation locale | `c9753cf` | Lieux partagés, contamination, rumeurs, sommeil persistant et causes de fermeture. |
| Solidarité et logistique | `58a07ee` | Relations joueur–PNJ, entraide, mémoire sociale, stock et livraison journalière. |

## Contrat de reprise par pôle

| Pôle | Ce qui est déposé | Prochaine responsabilité | Critère de passage |
| --- | --- | --- | --- |
| **Orion** | Tableau, décisions et journal à jour. | Ordonner les quatre chantiers du cycle suivant et éviter les dépendances circulaires. | Chaque tâche possède un propriétaire, une limite et un scénario de validation. |
| **Épidémie** | Exposition dans les lieux partagés et états sanitaires cachés. | Calibrer la progression avec des scénarios reproductibles, sans prétention médicale. | La crise est lente au départ, lisible au milieu et ne bascule pas arbitrairement. |
| **Civitas** | Réseau de contacts, mémoire et relation qualitative avec le joueur. | Faire évoluer les relations **entre** PNJ : alliance, dette, rupture, rumeur contredite. | Une décision sociale a une conséquence observable hors de la fiche du voisin. |
| **Atlas** | Stock invisible, notes d’arrivage et tournée de Noé. | Relier les demandes de quartier aux réserves et aux itinéraires de livraison. | Une rupture de stock est causale, annoncée et évitable au moins en partie. |
| **Vigile** | Intervalles réels et signaux corporels. | Ajouter des conséquences contextuelles aux besoins critiques. | Deux actions identiques donnent un résultat différent lorsque le personnage est épuisé, assoiffé ou isolé, sans afficher de compteur. |
| **Chronos** | Horloge, persistance et résolution de repos. | Vérifier les sauts de temps, les reprises après absence et les changements de jour. | Aucune sauvegarde ne produit de doublon de livraison, rumeur ou incident nocturne. |
| **Nocturne** | Carnet, radio, rumeurs et causalité des lieux. | Définir les préférences d’intensité et les formulations alternatives. | L’horreur peut être atténuée sans perdre les informations de jeu. |
| **Sentinelle** | Smoke tests, migration de sauvegarde et contrôle des fichiers. | Écrire la matrice de tests de régression du vertical slice. | Tous les scénarios de reprise, achat, relation et livraison sont vérifiés avant extension. |

## Règles de travail pour le cycle suivant

- **Un seul propriétaire de modification par fichier logique à la fois** : `app.js` exige un découpage annoncé dans le journal avant une intervention simultanée.
- **Tout nouvel état persistant doit migrer les sauvegardes précédentes** ; aucune version n’est cassée silencieusement.
- **Aucun système ne révèle une valeur cachée** de contamination, de relation ou de besoin par un chiffre, une barre ou un pourcentage.
- **Toute action sociale garde une alternative de retrait** : le joueur ne doit pas être forcé à aider pour pouvoir poursuivre la partie.
- **Toute conséquence inquiétante doit posséder une formulation de faible intensité** avant sa mise en scène plus forte.

## Vérifications déposées

- `node --check game/app.js` ;
- contrôle des espaces Git avec `git diff --check` ;
- smoke test de sauvegarde v3 et interaction de voisinage ;
- simulation de plusieurs jours avec tournée logistique ;
- vérification HTTP du serveur statique sur la racine, `app.js` et `styles.css`.

Les scripts de test sont reproductibles depuis les commandes consignées dans l’historique de travail ; ils seront formalisés par Sentinelle avant le prochain élargissement du prototype.
