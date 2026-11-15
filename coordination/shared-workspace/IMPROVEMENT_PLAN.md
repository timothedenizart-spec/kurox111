# Plan d'Amélioration Multi-Agents UCA & Système de Raffinement NCM Réflexif

**Date :** 2026-11-15 UTC  
**Chantier :** UCA-10  
**Auteurs & Pilotes :**  
- `Arena-NeuroMathArchitect` (Cortex Parallèle & Raisonnement Hybride)
- `Arena-ModelArchitect` & `Arena-NCMLead` (Modèle Neuronal MiniTransformer & Raffineur NCM)
- `Arena-CognitiveControlLead` (Global Workspace & Métacognition)
- `Arena-BenchmarkingLead` (Audit, Diagnostics & Métriques Qualitatives)
- `Arena-InterfaceLead` (Visualisation Réflexive dans l'UI)
- Opérateur / Propriétaire (`timothedenizart-spec`)

---

## 1. Contexte & Diagnostic Initial

À la suite de l'audit systématique mené via `scripts/run_cognitive_audit.py`, les constats suivants ont été établis :
1. **Force déterminée :** Le cortex parallèle (`uca/parallel_cortex.py`) et le moteur arithmétique exact résolvent avec 100% de rigueur les équations rationnelles, les clauses de Horn et les graphes causaux de Pearl.
2. **Faiblesse 1 (Gabarit rigide) :** 100% des réponses finales utilisaient un gabarit statique répétitif (`"Réponse UCA — synthèse locale traçable."`) manquant cruellement de fluidité, d'élégance rédactionnelle et de profondeur explicative.
3. **Faiblesse 2 (Sous-utilisation de NCM) :** Le MiniTransformer entraîné (UCA-08) n'était sollicité que pour émettre des propositions isolées de concepts sans participer à l'articulation intelligente de la réponse.
4. **Faiblesse 3 (Déconnexion de la réflexion) :** Les signaux métacognitifs avancés calculés dans le Global Workspace (couverture de preuves, incertitude métacognitive, registres d'incohérences, minimisation d'énergie libre de Friston) n'étaient pas synthétisés pour éclairer l'utilisateur sur le degré de certitude de l'architecture.

---

## 2. Objectifs du Chantier UCA-10

1. **Couplage Réflexif Métacognitif :** Connecter l'état métacognitif global (mémoire de travail bornée, graphe d'évidence, prédictions ascendantes/descendantes) au générateur de réponse finale.
2. **Raffineur Neuronal NCM (`NCM Refinement System`) :** Utiliser les couches d'attention du `MiniTransformer` pour projeter et synthétiser les concepts clés, puis affiner le texte final pour le rendre articulé, intelligent, pédagogique et naturel.
3. **Structure de Réponse en 4 Niveaux Cognitifs :**
   - 💡 **Synthèse Directe :** Réponse concise et limpide à l'interrogation.
   - 📐 **Démonstration & Preuves Formelles :** Étapes de déduction pas-à-pas (algèbre, logique, causalité, citations documentaires).
   - 🧠 **Réflexion Métacognitive :** Évaluation réflexive du degré de certitude, ancrage des preuves et alerte sur les données manquantes.
   - 🧬 **Résonance Conceptuelle NCM :** Concepts associés générés par le réseau de neurones, strictement marqués comme hypothèses non vérifiées.
4. **Invariants Épistémiques Inviolables :**
   - Aucune hallucination neuronale ne peut être promue au rang de fait certifié.
   - Les calculs exacts et déductions de Horn restent préservés bit-à-bit.
   - Les absences de données restent explicitement identifiées (honnêteté épistémique).

---

## 3. Répartition des Rôles & Lots de Travail (Work Packages)

- **WP1 — Diagnostics & Audit Continu (`Arena-BenchmarkingLead`)** :
  - Script d'audit automatique `scripts/run_cognitive_audit.py`.
  - Mesure de la régression, de la fluidité et du taux de gabarit statique (objectif : 0%).

- **WP2 — Modèle Neuronal & Contrat NCM (`Arena-ModelArchitect` & `Arena-NCMLead`)** :
  - Extension du contrat runner dans `scripts/neural_runner.py` avec l'opération `response_refinement`.
  - Projection attentionnelle des concepts de réflexion via le MiniTransformer entraîné.

- **WP3 — Intégration Pipeline & Contrôle Cognitif (`Arena-CognitiveControlLead` & `Arena-NeuroMathArchitect`)** :
  - Mise à jour de `ExternalNcmAdapter` dans `uca/model_adapters.py`.
  - Refonte de `FinalResponseModule` dans `uca/pipeline.py` et injection via `uca/factory.py`.
  - Traitement complet de tous les types de calculs (Causalité Pearl, VSA, Horn, Rationnel).

- **WP4 — Dashboard & Visualisation Réflexive (`Arena-InterfaceLead`)** :
  - Affichage visuel des métriques de réflexion (Erreur Friston $\epsilon$, Certitude, Graphe d'évidence) dans l'interface Web (`uca/web.py`).
  - Préréglages enrichis pour tester la boucle réflexive en un clic.

---

## 4. Critères de Validation & Définition de Fini

- 100% des tests unitaires réussis (`unittest discover tests`).
- Taux de gabarit rigide réduit à 0% dans l'audit.
- Rapport d'audit consigné dans `coordination/shared-workspace/AUDIT_REPORT.json`.
- Décision architecturale D-006 enregistrée dans `DECISIONS.md`.
- Publication transparente sur GitHub Issue #1.
