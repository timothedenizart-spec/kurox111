# Entraînement local contrôlé : LoRA SmolLM2-360M

UCA ne crée pas de modèle étudiant et ne fusionne pas des poids de modèles. Le
seul entraînement actuellement implémenté est un **adaptateur LoRA séparé** pour
un checkpoint local existant `SmolLM2-360M-Instruct` compatible Transformers.

## Prérequis non négociables

1. Un checkpoint local complet, avec `config.json` et tokenizer associé, indiqué
   par `models.smollm2_360.path`.
2. Un dataset JSONL local, sans mémoire utilisateur, où chaque ligne possède :

   ```json
   {"id":"...","text":"texte SFT déjà formaté", "source":"...", "license":"..."}
   ```

   `text` doit être la séquence d'entraînement déjà préparée pour le tokenizer
   du checkpoint. UCA ne devine pas de chat-template ni de modules LoRA.
3. Un manifeste basé sur [`manifest.template.json`](manifest.template.json),
   avec le hash SHA-256 réel du dataset, le fingerprint du checkpoint, droits confirmés et approbateur nommé.
4. Les modules cibles LoRA inspectés sur le checkpoint réel et renseignés dans
   `training.lora_target_modules`.
5. Un environnement local déjà préparé avec `torch` et `transformers` ; UCA
   n'installe ni ne télécharge de package, poids, corpus ou projet.

## Étapes

```bash
# Ne charge aucun modèle ; contrôle chemins, hash, droits, dataset et sortie.
python -m uca training-preflight --root .

# Seulement lorsque le rapport indique "can_train": true.
python -m uca train-lora-adapter --root . --confirm I_CONFIRM_LOCAL_TRAINING
```

La seconde commande :

- charge le checkpoint et son tokenizer depuis les chemins locaux ;
- gèle explicitement les poids de base et n'entraîne que les matrices LoRA locales ;
- sauvegarde un adaptateur séparé et `uca_training_report.json` ;
- ne fait jamais `merge_and_unload` ;
- refuse un dossier de sortie déjà non vide ;
- ne peut pas être appelée depuis le pipeline de conversation.

## Limites et validation

Un apprentissage terminé n'est pas une amélioration démontrée. Comparez
l'adaptateur au checkpoint de base avec des tâches annotées, données de
validation séparées, latence, RAM/VRAM, factualité et contrôles d'hallucination.
Consignez les résultats reproductibles dans l'espace de travail partagé avant
d'activer l'adaptateur dans UCA.
