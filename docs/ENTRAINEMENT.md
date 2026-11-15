# Entraînement local et organisation (UCA-09 → UCA-11)

> Session Préfrontal (`arena/57dad57f-kurox111`), 2026-11-15.
> Toutes les valeurs ci-dessous sont **mesurées**, sur CPU, sans aucun téléchargement.

## 1. Organisation de l'entraînement (qui fait quoi)

| Nom | Responsabilité entraînement | Chantier |
|---|---|---|
| **Préfrontal** (nous) | moteur d'entraînement local, métriques, shim contractuel, boucle de calibration | UCA-09 ✅ |
| **Hippocampe** (proposé) | curation/extension du corpus français avec provenance et hash | UCA-10 |
| **Cortex** (proposé) | validation des checkpoints SmolLM2 (vrai chemin de montée en échelle) | UCA-03 |
| **Thalamus** (proposé) | arbitrage d'activation : seuils, revue croisée, décision consignée | UCA-11 |

Règles actives : un checkpoint n'est jamais présenté comme validé sans rapport de
calibration **et** revue humaine ; les artefacts de modèle restent hors Git
(`models/` est gitignoré) ; tout chiffre publié doit être reproductible par la
commande indiquée, avec sa graine et son hash de corpus.

## 2. Ce qui a réellement été entraîné

Un **micro-débruiteur masqué de type CBOW** (`uca/microtrain.py`) :
`h = moyenne des embeddings du contexte (fenêtre ±4)` → `softmax(W·h + b)`,
optimisé par Adam, **44 460 paramètres**, vocabulaire de 684 mots.

- **Corpus** : uniquement la documentation française du dépôt (README, docs/,
  coordination/) — 508 phrases, sha256 `6ef5d7bf8cc87904`, répartition
  train/holdout déterministe par hash de phrase (aucune fuite).
- **Reproduction** : `python -m uca microtrain --epochs 60 --seed 42`
  (déterminisme vérifié par test : paramètres bit-identiques à même graine).

## 3. Résultats mesurés (modèle livré : seed 42, epochs 60)

| Métrique | Valeur | Référence |
|---|---|---|
| Perte CE, 1ʳᵉ → dernière époque | 6,0619 → 1,0149 | baisse nette et monotone en moyenne |
| Perplexité holdout du modèle | **301,08** | — |
| Perplexité unigramme (baseline) | 1 149,03 | le modèle est **3,8× mieux** |
| Perplexité uniforme | 684 | borne triviale |
| Restauration exacte de tokens corrompus | 13,1 % (8/61) | hasard ≈ 0,15 % |

## 4. Boucle de gouvernance démontrée en conditions réelles

Le modèle a été câblé dans le **vrai contrat nanoDiff** (shim
`shims/nanodiff_micro_runner.py`, tokenizer HF-compatible avec ids identiques,
`mask_token_id=2`), via `config/uca.micro-demo.toml`, puis soumis à la
calibration réglementaire sur 16 cas de corruption (graine fixe,
`benchmarks/nanodiff-calibration.micro.jsonl`) :

```
python -m uca validate-nanodiff benchmarks/nanodiff-calibration.micro.jsonl \
    --config config/uca.micro-demo.toml
→ status: executed ; mean_delta = -0,099 ; validated_for_activation = false
```

**Verdict honnête : rejet.** Le modèle apprend de vraies statistiques (§3),
mais sous le protocole de calibration (masquage par foulée frappant surtout des
tokens sains), ses prédictions *dégradent* la similarité à la référence — un
CBOW de 684 mots ne relit pas assez finement. Le pipeline garde donc
`nanodiff_specialist` à `non_validated`. C'est exactement le comportement visé :
**la calibration est un portail, pas une formalité.**

## 5. Limites explicites

- Micro-échelle : ce n'est ni un transformer, ni nanoDiff-50M, ni SmolLM2.
- Corpus minuscule et bilingue mêlé ; vocabulaire mot-entier sans subword.
- La voie « vrai modèle » reste UCA-03 (checkpoints opérateur + `[models]` extras).
- Un `mean_delta` positif ne prouverait jamais la factualité : revue humaine requise.

## 6. Commandes

```bash
python -m uca microtrain --epochs 60 --seed 42 \
    --calibration-jsonl benchmarks/nanodiff-calibration.micro.jsonl
python -m uca --config config/uca.micro-demo.toml status
python -m uca validate-nanodiff benchmarks/nanodiff-calibration.micro.jsonl \
    --config config/uca.micro-demo.toml
```
