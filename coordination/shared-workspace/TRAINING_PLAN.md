# Plan d'Entraînement Multi-Agents — Modèle Neuronal UCA

**Dernière mise à jour :** 2026-11-15 UTC
**Chantier :** `UCA-08`
**Objectif :** Entraîner un modèle neuronal léger autonome (Transformer Denoiser / Concept Generator) pour fournir des poids réels, validés et mesurés pour les composants neuronaux d'UCA (NCM et nanoDiff).

---

## 1. Répartition des Rôles pour l'Entraînement

| Rôle | Agent responsable | Mission | Livrables |
| :--- | :--- | :--- | :--- |
| **Arena-ModelArchitect** | Session active `arena/de272f1c` | Conception de l'architecture Transformer, couches d'attention, fonctions d'activation et rétropropagation | `training/model.py` |
| **Arena-DataEngineer** | Session active `arena/de272f1c` | Élaboration du corpus d'apprentissage multi-domaines, tokenizer et masquage dynamique | `training/dataset.py` |
| **Arena-TrainingMaster** | Session active `arena/de272f1c` | Implémentation de la boucle d'apprentissage, optimiseur AdamW, checkpoints et suivi de loss | `training/train.py` |
| **Arena-IntegrationLead** | Session active `arena/de272f1c` | Branchement du modèle entraîné dans le pipeline UCA et validation des performances | `scripts/neural_runner.py` |

---

## 2. Spécification de l'Architecture Neuronale

Pour garantir un entraînement déterministe, reproductible et sans dépendance externe lourde (fonctionnant avec `numpy` pur en environnement contraint CPU 2 cœurs / 3.8 Go RAM) :

- **Type de réseau :** Transformer Encoder-Denoiser avec têtes d'attention multi-têtes (*Scaled Dot-Product Multi-Head Attention*).
- **Vocabulaire :** Caractères et sous-mots normalisés, incluant tokens réservés (`[PAD]`, `[UNK]`, `[MASK]`, `[BOS]`, `[EOS]`).
- **Hyperparamètres :**
  - Dimension de modèle ($d_{model}$) : 64
  - Têtes d'attention ($n_{heads}$) : 4 (dimension par tête $d_k = 16$)
  - Dimension cachée Feed-Forward ($d_{ff}$) : 128
  - Nombre de couches ($L$) : 2
  - Longueur maximale de séquence ($seq\_len$) : 64
  - Fonction d'activation : GELU (Gaussian Error Linear Unit)
  - Normalisation : LayerNorm avec paramètres apprenables $\gamma$ et $\beta$
  - Régularisation : Weight decay $0.01$ (AdamW)
  - Pas d'apprentissage initial ($\eta$) : $10^{-3}$ avec décroissance cosinusoïdale

---

## 3. Tâche d'Apprentissage & Données

Le modèle est entraîné sur une tâche mixte de :
1. **Débruitage masqué (*Masked Denoising*)** : 15% à 25% des tokens d'entrée sont masqués avec le token `[MASK]`. Le modèle doit prédire les tokens originaux.
2. **Génération de concepts (*Concept Association*)** : Associer des concepts clés à partir de prémisses scientifiques, logiques et mathématiques.

---

## 4. Critères de Validation et de Sortie

- Baisse mesurable de la perte Cross-Entropy (au moins 50% de réduction entre l'époque 1 et la dernière époque).
- Taux de reconstruction correcte des tokens masqués supérieur à 70% sur l'ensemble de validation.
- Sauvegarde d'un checkpoint complet dans `models/checkpoints/` avec métadonnées d'entraînement.
- Intégration vérifiée dans le runner UCA via `python -m uca chat`.
