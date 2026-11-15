# UCA-10 — Lancement automatique de l'interface locale

- **Responsable :** Atlas
- **État :** terminé et validé sans actifs modèles
- **Portée :** un fichier ouvrable démarre UCA depuis n'importe quel répertoire,
  sélectionne un port local libre, initialise la configuration disponible,
  affiche l'état réel, puis ouvre le navigateur.

## Limites convenues

- Aucun téléchargement, checkpoint synthétique ou statut de module fictif.
- Les composants sans actifs locaux restent explicitement indisponibles ou non
  validés dans l'interface.
- Les modèles demeurent à chargement paresseux ; le lanceur ne les garde pas
  tous en mémoire afin de préserver les contrôles VRAM séquentiels.

## Fichiers prévus

- `Lancer_UCA.py` (entrée unique Python)
- `Lancer_UCA.sh` et `Lancer_UCA.bat` (raccourcis de plateforme)
- `uca/launcher.py` (cycle de vie serveur, readiness et navigateur)
- `docs/LAUNCHER.md` (emploi et comportements honnêtes)

## Validation réalisée

- `python -m py_compile uca/*.py tests/*.py Lancer_UCA.py` : réussi.
- `python -m unittest discover -s tests -v` : 22 tests réussis, dont les tests
  de port libre, endpoint d'état, absence de création d'actifs et demande
  d'ouverture du navigateur.
- Smoke réel avec `Lancer_UCA.py --no-browser` depuis un répertoire courant
  arbitraire : URL `127.0.0.1` dynamique et `/api/status` fonctionnels.
- Smoke CLI `python -m uca launch --root . --no-browser --port 0` : métadonnée
  de préparation présente et modules sans poids correctement `unavailable`.

L'ouverture d'un navigateur réel n'a pas été présentée comme une validation UI
interactive : le test unitaire vérifie la demande à `webbrowser.open`, tandis
que les smokes sans navigateur vérifient le serveur et l'état honnête.
