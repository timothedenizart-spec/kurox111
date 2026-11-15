# Équipe, alias et périmètres

Ce registre attribue les responsabilités afin que les expérimentations restent intégrables. Une attribution est une réservation de périmètre, non une approbation automatique du code déjà produit.

## Noms de travail

| Alias | Branche | État | Responsabilité réservée | Fichiers / interfaces protégés |
| --- | --- | --- | --- | --- |
| **Thalamus** | `arena/f2ae664d-kurox111` | actif | Coordination, préflight d’entraînement, provenance, registre d’expériences, benchmark et décisions d’acceptation. | `uca/experiment_registry.py`, `training/`, `coordination/shared-workspace/` |
| **Cortex** | `arena/8e5e2ae2-kurox111` | actif | Baseline UCA, ordonnanceur parallèle déterministe et futur runner local LoRA. | `uca/engine.py`, tests de parité du scheduler, contrat de trainer |
| **Hippocampe** | `arena/de272f1c-kurox111` | confirmé dans l’issue #1 | Corpus, Data Cards, partitions disjointes et modules neuro-mathématiques déterministes. | `data/`, `uca/parallel_cortex.py`, `uca/symbolic_math.py`, `uca/cognitive.py`, tests associés |
| **Préfrontal** | `arena/57dad57f-kurox111` | actif | Mémoire associative, signaux de nouveauté, évaluation cognitive et non-régression. | `uca/vsa.py`, `uca/associative.py`, `uca/predictive.py`, `uca/consolidation.py`, harnais d’évaluation |
| **Intake-Security** | `arena/3cdf297b-kurox111` | en attente de publication | Interface locale de dépôt/import par blocs et sa revue de sécurité. | Non réservé tant que la branche ou le commit n’est pas publié. |

## Voie interface à lancement automatique

- **Thalamus** crée le lanceur autonome `OPEN_UCA.py` et `uca/launcher.py` : il initialise les stores vides, construit l’application, effectue le préflight de disponibilité, démarre le serveur et ouvre le navigateur local.
- **Cortex** conserve la responsabilité de l’évolution visuelle et du statut d’exécution dans `uca/web.py` afin d’éviter une collision de fichier.
- **Intake-Security** ne rejoint l’interface qu’après publication de son code et revue des limites de taille, chemins, authentification locale et données sensibles.
- « Tout chargé » signifie que la configuration et les stores sont initialisés et que les états de disponibilité ont été lus. Cela ne signifie jamais qu’un checkpoint absent a été téléchargé ou qu’un modèle a été simulé.

## Voie NCM-REFINE

- **Thalamus** possède le contrat de réflexion, le gate de provenance et `uca/ncm_refinement.py` ; il ne modifie le pipeline partagé qu’après tests croisés.
- **Cortex** possède l’adaptateur et le runner de raffinement `ncm_refine_response` dans `uca/model_adapters.py` / la configuration. Le NCM existant de génération de concepts n’est pas requalifié automatiquement comme raffineur de réponse.
- **Hippocampe** fournit les cas sourcés et contradictoires ; **Préfrontal** effectue l’évaluation/red-team ; **Intake-Security** revoit tout import de poids ou corpus.
- Le NCM reste `off` par défaut et ses sorties sont toujours des propositions jusqu’au passage d’un gate de vérification indépendant.

## Règle de conflit

`uca/engine.py`, `uca/pipeline.py`, `uca/config.py`, `uca/factory.py` et `uca/cli.py` sont des points d’intégration à forte collision. Aucun agent ne les modifie en parallèle sans tâche explicitement attribuée et protocole de portage.

- **Cortex** détient provisoirement le scheduler et le futur runner de fine-tuning dans `uca/engine.py` / son contrat dédié.
- **Préfrontal** isole ses extensions dans des modules nouveaux ; ses changements de moteur déjà présents seront comparés comme variante, pas fusionnés aveuglément.
- **Hippocampe** expose son cortex via une interface de module et fournit les splits de données avant toute modification du moteur commun.
- **Thalamus** ne fusionne aucune variante ni aucun adaptateur tant que la baseline, les tests, les ablations et le manifeste d’entraînement ne sont pas disponibles.

## Séquence d’intégration

1. Le noyau UCA `dbb28a9` devient la baseline de développement minimale.
2. Chaque extension est d’abord testée seule contre cette baseline.
3. Les variantes concurrentes du moteur sont comparées par parité, déterminisme, ressources et qualité — elles ne sont pas concaténées.
4. Une intégration retient une interface stable et ajoute des tests de régression avant de modifier le pipeline par défaut.

## Engagement de reporting

Chaque alias met à jour l’issue #1 avec sa révision, les fichiers, les tests exécutés, les ressources locales requises et les risques. Une tâche non déclarée n’est pas intégrable.
