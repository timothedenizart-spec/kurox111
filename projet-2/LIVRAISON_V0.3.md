# Livraison V0.3 — La dernière semaine

## Dépôt

- **Version :** `0.3.0`
- **Branche :** `arena/59647e61-kurox111`
- **Dernier commit de livraison :** `f641ec0` — `feat: add neighborhood signals and shelter choices`
- **Revue :** [pull request #2](https://github.com/timothedenizart-spec/kurox111/pull/2)
- **État :** déposé pour relecture ; non fusionné à ce stade.

## Contenu livré

| Domaine | Livré | Fichiers principaux |
| --- | --- | --- |
| Expérience | Interface web responsive, montre diégétique, actions et journal | `index.html`, `styles.css`, `app.js` |
| Temps et besoins | Faim, soif, sommeil, hygiène, toilettes et besoin de lien exprimés par ressentis | `simulation.js` |
| Habitants | Emplacements, intentions, états fictionnels, mémoire des interactions et confiance | `simulation.js` |
| Crise | Cinq phases fictionnelles, évolution des services et des comportements | `simulation.js` |
| Économie | Travail et argent au début, prix instables puis entraide et ressources | `simulation.js` |
| Quartier | Signal quotidien, radio, abri préparé, refuge collectif | `simulation.js`, `app.js` |
| Qualité | Tests de la progression, des besoins, de l’entraide, de la radio, de l’abri et des signaux | `tests/simulation.test.mjs` |

## Validation effectuée

```bash
npm run check
npm test
```

Résultat attendu à cette livraison : **10 tests réussis**. La démo se sert localement avec :

```bash
python3 -m http.server 4173 --bind 0.0.0.0
```

Aucune dépendance applicative externe n’est requise.

## Contraintes conservées

- La crise, la contamination et les infectés sont des éléments de fiction.
- Le prototype n’est ni un modèle médical ni un conseil sanitaire.
- Les besoins ne sont pas représentés par des jauges ; ils reposent sur l’horloge et des signaux textuels.
- Les données de partie sont actuellement en mémoire : il n’y a pas encore de sauvegarde.
- La simulation est volontairement une verticale de jeu locale, pas un monde 3D ou un modèle épidémiologique réel.

## Relais vers P2-007

| Rôle | Relais attendu |
| --- | --- |
| `NOVA` | Donner aux habitants des préférences, souvenirs et réactions plus différenciés, sans casser le déterminisme des tests. |
| `LYRA` | Écrire des rencontres courtes qui dépendent de la confiance, de la phase et du lieu. |
| `ATLAS` | Vérifier les conséquences entre confiance, abri, économie et horaires des habitants. |
| `MINT` | S’assurer que les relations et ressources prennent bien le relais des crédits aux dernières phases. |
| `VITA` | Vérifier que les nouveaux choix restent lisibles sans jauge ni surcharge d’interface. |
| `FORGE` | Garder le prototype statique et sans dépendance tant que la boucle n’est pas validée. |
| `ARGUS` | Ajouter un test pour chaque relation ou conséquence durable introduite. |
| `ORBIT` | Mettre à jour le tableau, le journal et les décisions avant de déclarer la prochaine livraison prête. |

## Critères d’acceptation de P2-007

- Au moins trois habitants possèdent une réaction reconnaissable à une interaction répétée.
- Les choix du joueur ont une conséquence sociale visible dans le journal ou les actions disponibles.
- Aucune nouvelle mécanique n’introduit de jauge corporelle, d’information médicale réelle ou de dépendance externe.
- Les tests existants continuent de réussir et les comportements ajoutés sont couverts.
