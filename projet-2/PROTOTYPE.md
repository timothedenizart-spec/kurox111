# Prototype web — La dernière semaine, V0.3

## Lancer la démo

Depuis la racine du dépôt :

```bash
python3 -m http.server 4173 --bind 0.0.0.0
```

Ouvrir ensuite `http://localhost:4173` en local. Aucun paquet applicatif externe n’est nécessaire. Pour exécuter les contrôles automatisés :

```bash
npm run check
npm test
```

## Contenu intégré

- Horloge diégétique et passage du temps; les besoins sont rendus par des ressentis, sans jauges.
- Actions de survie et choix d’itinéraires dans plusieurs lieux.
- Habitants avec intentions/contextes et mémoire relationnelle; l’entraide peut compter davantage que l’argent après la rupture.
- Économie et services évoluant au fil de phases narratives fictionnelles.
- Contacts récents restitués comme signal narratif de prudence, sans diagnostic ou valeur médicale.
- Bulletin radio, événement quotidien de quartier, préparation de l’appartement et accès conditionnel à un refuge.
- Dix tests automatisés couvrant horloge, besoins, économie, entraide, exposition narrative, signaux, radio et abri.

Voir [`LIVRAISON_V0.3.md`](LIVRAISON_V0.3.md) pour les détails de livraison et le relais vers la suite.

## Limites connues

Il s’agit d’une tranche web locale, pas d’un jeu complet ni d’une simulation médicale. La crise et les infectés sont entièrement fictifs. Les données de partie ne sont pas sauvegardées; il n’y a ni multijoueur ni monde 3D. La simulation est volontairement bornée et les valeurs d’équilibrage restent à tester.

## Prochaine coordination

Le tableau prévoit P2-007 : rendre les habitants et les conséquences relationnelles plus différenciés, avec des tests pour chaque nouvel effet. Après retours de jeu, décider si une V0.4 ou un moteur dédié est justifié.
