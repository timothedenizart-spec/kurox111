# Veille — Chroniques d'une contagion

Prototype jouable d'un jeu de survie narratif en français. Le joueur traverse les premiers jours d'une épidémie, puis l'effondrement progressif de la ville et l'apparition d'une menace infectée qui évolue vers l'horreur zombie.

## Lancer le prototype

Aucune dépendance à installer. Depuis la racine du dépôt :

```sh
python3 -m http.server 8000 --bind 0.0.0.0
```

Ouvrir ensuite `http://localhost:8000`. La partie est sauvegardée dans le stockage local du navigateur.

Pour lancer les tests de fumée (Node.js requis) :

```sh
node --test
```

## Boucle de jeu actuelle

- Lire sa montre et les signes narratifs de faim, soif, fatigue, hygiène et besoins naturels — **sans jauges**.
- Choisir une destination, se déplacer, fouiller, parler aux habitants, acheter, aider l'épicier contre rémunération, manger, boire ou se reposer.
- Quand les commerces se replient, le troc au point de rassemblement prend progressivement le relais de l'argent.
- Les actions font avancer l'horloge; l'épidémie, les comportements des habitants et l'économie évoluent avec le temps.
- Les décisions et l'exposition aux lieux fréquentés influent sur les risques et les ressources.

Les nombres et rythmes de l'épidémie sont des abstractions ludiques d'une maladie entièrement fictive, pas un modèle médical. Voir [docs/conception.md](docs/conception.md), [docs/coordination.md](docs/coordination.md) et le [canal officiel Projet 2](https://github.com/timothedenizart-spec/kurox111/issues/3).
