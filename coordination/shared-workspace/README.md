# Espace de travail multi-agent

Un point de dépôt partagé et simple à lancer. Le lanceur démarre le serveur, attend sa disponibilité puis ouvre automatiquement le tableau de bord. Celui-ci charge au démarrage la liste de tous les fichiers déjà déposés (noms, tailles et liens de téléchargement). Il permet d'envoyer des fichiers de tout type et des dossiers complets par blocs de 8 Mio, en conservant l'arborescence. Aucun plafond de taille applicatif n'est imposé : la limite pratique est l'espace disque disponible. Les transferts écrivent directement sur disque côté serveur.

## Lancer

**Linux / macOS** : depuis la racine du dépôt, exécuter `./coordination/shared-workspace/start.sh`, puis ouvrir <http://localhost:8765>.

**Windows** : double-cliquer sur `coordination/shared-workspace/start.bat`, puis ouvrir <http://localhost:8765>.

Ou lancer directement `python3 coordination/shared-workspace/server.py` (Windows : `py coordination/shared-workspace/server.py`). Python 3.10 ou plus récent est recommandé ; aucune dépendance externe n'est requise. Pour changer l'adresse ou le port : `WORKSPACE_HOST=0.0.0.0 WORKSPACE_PORT=8765 python3 coordination/shared-workspace/server.py`.

Le serveur écoute par défaut sur toutes les interfaces afin de fonctionner dans l'aperçu Arena. Sur un réseau partagé, utilisez-le uniquement dans un environnement de confiance : l'interface n'a pas d'authentification. Ne l'exposez pas directement à Internet et ne téléversez pas de secrets ou de données sensibles.

## Dépôt et partage entre agents

Les téléversements vont dans `inbox/`, sous ce dossier. Les données de `inbox/` et les blocs temporaires `.uploads/` sont ignorés par Git : partagez des documents utiles en les ajoutant explicitement à Git après vérification, ou utilisez le canal de synchronisation convenu par l'équipe. Cette interface ne diffuse pas automatiquement les fichiers vers d'autres sessions isolées.

Les fichiers existants ne sont jamais écrasés : un suffixe est ajouté en cas de doublon. Les fichiers partiels restent dans `.uploads/` après une interruption et peuvent être supprimés manuellement quand le serveur est arrêté. Il n'y a pas de reprise automatique après interruption du navigateur.
