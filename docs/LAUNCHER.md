# Lancement automatique de l'interface UCA

Le fichier principal à ouvrir est :

```text
Lancer_UCA.py
```

Il se place automatiquement à la racine du dépôt, initialise la configuration
UCA, démarre le serveur local sur un port libre et ouvre le navigateur par
défaut quand le serveur est prêt.

Des raccourcis supplémentaires sont fournis :

```text
Lancer_UCA.sh   # Linux / macOS
Lancer_UCA.bat  # Windows
```

L'équivalent terminal est :

```bash
python Lancer_UCA.py
# ou
python -m uca launch --root .
```

Le lanceur écoute par défaut sur `127.0.0.1` et demande un port libre au système,
ce qui évite de dépendre de 8080. Il affiche l'URL, la topologie et le bilan
réel des modules avant d'ouvrir le navigateur. Arrêtez-le avec `Ctrl+C` dans le
terminal qui l'a lancé.

## Ce qui est chargé

Au démarrage, UCA charge son moteur, sa configuration, ses magasins locaux et
le tableau d'état des modules. L'interface, ses styles et son JavaScript sont
servis localement sans CDN ni API distante.

Les checkpoints modèles restent chargés paresseusement et conservent le statut
`unavailable` ou `non_validated` quand leurs actifs locaux sont absents. Le
lanceur ne simule pas de poids, ne télécharge rien, et ne force pas tous les
modèles en RAM/VRAM : cela préserverait mal le mode séquentiel et pourrait faire
échouer une machine locale. Une fois des actifs locaux valides configurés, leur
chargement suit les politiques UCA existantes.
