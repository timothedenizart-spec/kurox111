# Transferts de travail

Utilisez ce modèle pour démarrer, transférer ou clôturer un chantier :

```md
## YYYY-MM-DD — UCA-XX — alias
- **Type :** prise en charge | transfert | clôture | blocage
- **Commit de départ / arrivée :**
- **Périmètre de fichiers :**
- **Changement ou constat :**
- **Commandes exécutées et résultat réel :**
- **Risques, limites ou actifs manquants :**
- **Action suivante / destinataire :**
```

## 2026-11-15 — UCA-07 — Cognition-avancée (`arena/57dad57f-kurox111`)

- **Type :** prise en charge
- **Commit de départ / arrivée :** merge tracé d'`arena/8e5e2ae2-kurox111` @ `1120d24` → nouveaux commits sur `arena/57dad57f-kurox111`
- **Périmètre de fichiers :** ajoutés `uca/vsa.py`, `uca/associative.py`, `uca/predictive.py`, `uca/consolidation.py`, `docs/EXTENSIONS_COGNITIVES.md`, `tests/test_advanced_cognition.py` ; modifiés `uca/engine.py`, `uca/pipeline.py`, `uca/config.py`, `uca/factory.py`, `uca/cli.py`, `config/uca.toml`, `README.md`, `docs/ARCHITECTURE.md`
- **Changement ou constat :** mémoire hyperdimensionnelle VSA/HRR (complétion holographique, auto-fidélité, transfert analogique), réseau de Hopfield à capacité honnête, moniteur de surprisal de Shannon, consolidation Hebbienne hors-ligne, moteur parallèle par niveaux contigus (sorties bit-identiques au séquentiel, vérifié par test de parité)
- **Commandes exécutées et résultat réel :** `python3 -m unittest discover -s tests` → 27/27 OK ; démo CLI (init → import FTS5 → consolidate → chat --developer → status avec niveaux) fonctionnelle
- **Risques, limites ou actifs manquants :** bases SmolLM2/MeTTa/nanoDiff toujours indisponibles (statuts honnêtes inchangés) ; `engine.execution_mode = "sequential"` restaure l'ordre historique
- **Action suivante / destinataire :** revue par UCA-orchestrateur ; proposer cette branche comme référence d'intégration dans l'issue #1

_Aucun autre transfert n'est encore enregistré._
