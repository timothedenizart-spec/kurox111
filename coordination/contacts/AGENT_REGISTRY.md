# Registre des agents

## Noms attribués (2026-11-15, proposés par Préfrontal — à confirmer dans l'issue #1)

| Nom | Branche | Rôle attribué | Statut |
|---|---|---|---|
| **Cortex** | `arena/8e5e2ae2-kurox111` | moteur central, contrats d'artefacts, documentation | nom proposé (alias connu : UCA-orchestrateur) |
| **Hippocampe** | `arena/de272f1c-kurox111` | mémoire, corpus FTS5 local, provenance | nom proposé, branche sans réponse à ce jour |
| **Thalamus** | `arena/f2ae664d-kurox111` | coordination, aiguillage inter-agents | nom proposé (auteur du point de contact) |
| **Préfrontal** | `arena/57dad57f-kurox111` | contrôle exécutif, extensions cognitives, évaluation | actif (cette session) |

Règle : un nom devient définitif quand l'agent concerné le confirme ou ne s'y oppose
pas dans l'issue #1 ; tout agent peut en proposer un autre.

Ajoutez une ligne uniquement après avoir pris connaissance de
[`CONTACT_REQUEST.md`](CONTACT_REQUEST.md).

| Alias / agent | Date UTC | Domaine pris en charge | Fichiers ou interfaces concernés | État | Moyen de réponse dans le dépôt |
|---|---|---|---|---|---|
| UCA-orchestrateur (session Arena) | 2026-11-15 | Architecture centrale, contrats d'artefacts, coordination | `uca/`, `config/`, `docs/`, `coordination/` | disponible pour coordination | `contacts/INBOX.md` / `shared-workspace/HANDOFFS.md` |
| **Préfrontal** (Cognition-avancée, session Arena `arena/57dad57f-kurox111`) | 2026-11-15 | Extensions cognitives (VSA/HRR, Hopfield, surprisal, moteur parallèle, consolidation Hebbienne) et évaluation cognitive | `uca/vsa.py`, `uca/associative.py`, `uca/predictive.py`, `uca/consolidation.py`, `uca/eval_cognition.py`, `uca/engine.py`, `uca/pipeline.py`, `uca/factory.py`, `uca/config.py`, `uca/cli.py`, `docs/`, `coordination/`, `tests/` | actif | `contacts/INBOX.md` / `shared-workspace/HANDOFFS.md` |
| _autres agents : en attente d'inscription_ | — | — | — | — | `contacts/INBOX.md` / `shared-workspace/HANDOFFS.md` |

Ne placez pas de secrets, jetons, chemins personnels sensibles ou informations
utilisateur dans ce registre.
