# Éclipse — chronique d’une ville en rupture

Prototype web narratif d’un jeu de survie pandémique réaliste : une maladie initialement humaine, contagieuse et mortelle déstabilise progressivement une ville. Au fil des jours, les institutions, l’économie et les liens sociaux s’effondrent, tandis que l’infection développe des comportements inédits.

Le projet privilégie les conséquences observables plutôt que les jauges : une montre, le contexte, les sons, les comportements et les messages du monde permettent au joueur de comprendre son état.

## Lancer le prototype

Aucune dépendance n’est nécessaire. Depuis la racine du dépôt :

```bash
python3 -m http.server 4173 --directory game --bind 0.0.0.0
```

Ouvrir ensuite `http://localhost:4173`. Le prototype conserve la partie dans le navigateur ; utilisez « Recommencer » dans le menu pour repartir de zéro.

## Ce qui est déjà amorcé

- horloge réelle persistante et besoins physiologiques sans barres de progression ;
- contamination par étapes et calendrier de mutation à l’échelle de jours réels ;
- habitants simulés avec rôle, foyer, ressources, mobilité, réseau de contacts, mémoire courte et état sanitaire caché ;
- contamination reliée aux présences communes dans l’épicerie, la pharmacie, la place et les trajets ;
- économie qui se fragilise, commerces ravitaillés par une tournée simulée puis limités ou fermés pour une cause locale visible ;
- relations de voisinage influencées par la parole, l’entraide, le partage d’information ou le retrait ;
- transactions, stock personnel, rumeurs sourcées mais incertaines, radio et carnet d’observations ;
- interface de prototype immersive, en français et sans dépendance externe.

## Coordination

La répartition des responsabilités, les décisions de simulation et le tableau de travail sont dans [`projet-2/`](projet-2/README.md). Aucun élément de ce prototype ne doit faire passer des seuils biologiques simulés pour des conseils médicaux.
