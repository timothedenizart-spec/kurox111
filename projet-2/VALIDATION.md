# Validation et scénarios de revue — Projet 2

La base de référence est le prototype V0.3 (`app.js`, `simulation.js`, `tests/simulation.test.mjs`). Les prototypes antérieurs/concurrents sont inventoriés dans [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md); leurs contrôles ne remplacent pas ceux de la base retenue.

## Vérifications reproductibles — base V0.3

Depuis la racine :

```bash
npm run check
npm test
```

Résultat constaté après intégration sur la branche de session : analyse syntaxique réussie et **10 tests réussis**. Les tests couvrent horloge, signaux de besoins, économie, arrêt du travail, consommation d’eau, entraide, signaux narratifs de contacts, événement de quartier, radio et préparation de l’abri.

La branche `arena/1dbdd8bb-kurox111` ne publie pas de suite automatisée avec son prototype; son fichier `game/app.js` a passé `node --check`. La branche `arena/ef1aae95-kurox111` publie sept tests de fumée; ils ont passé dans un environnement CommonJS temporaire isolé. Leur lancement direct sous le `package.json` ESM de la base V0.3 échoue au chargement de `require`, point à corriger si cette contribution est reprise.

## Scénarios de conception à poursuivre

1. **Rythme des besoins** — vérifier que le joueur comprend les signaux, les durées d’action et les effets d’une journée chargée sans lire une jauge.
2. **Information partielle** — les rumeurs et nouvelles donnent des motifs de prudence sans certitude omnisciente.
3. **Économie locale** — les fermetures et ruptures de stock ont des causes observables; argent et entraide ont un rôle cohérent selon les phases.
4. **PNJ et relations** — les actions répétées modifient des comportements visibles et testables; la mémoire ne contredit pas l’historique.
5. **Persistance et reprise** — décider si la sauvegarde temps réel proposée par une branche parallèle est souhaitée, puis tester les retours après absence et les doublons d’événements.
6. **Accessibilité** — s’assurer que les indices diégétiques restent compréhensibles, avec options pour modérer l’intensité et le contenu.

## Conditions avant V0.4

- Revue humaine des changements et arbitrage des idées reprises des branches archivées.
- Ajouter un test automatisé pour chaque nouvelle règle et préserver les dix tests V0.3.
- Vérifier manuellement le rendu sur mobile et la cohérence de l’interface.
- Ne pas présenter les paramètres fictifs comme faits ou recommandations médicales.
