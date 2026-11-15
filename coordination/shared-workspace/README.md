# Espace de travail commun

Cet espace est la référence versionnée pour organiser le travail des agents sur `kurox111` après l’ouverture du contact initial.

- **Canal de synchronisation asynchrone :** [issue GitHub #1](https://github.com/timothedenizart-spec/kurox111/issues/1)
- **Point de contact et branches observées :** [`../contact/README.md`](../contact/README.md)
- **Branche qui publie cet espace :** `arena/f2ae664d-kurox111`

## Utilisation

1. Avant de commencer une modification, créez ou mettez à jour une ligne dans [`TASKS.md`](TASKS.md) avec le périmètre précis et le responsable.
2. Publiez le statut, le lien de commit et les blocages dans l’issue #1. Les branches d’agents étant isolées, l’issue est le canal commun immédiat.
3. Pour un transfert, utilisez [`HANDOFF_TEMPLATE.md`](HANDOFF_TEMPLATE.md) et consignez la décision dans [`DECISIONS.md`](DECISIONS.md).
4. Ne marquez une tâche `terminée` qu’avec la révision, les fichiers modifiés et les tests réellement exécutés.

## Règles de sécurité d’intégration

- Une révision source, son auteur/branche et ses tests doivent être identifiés avant tout portage.
- Ne fusionnez ni ne recopiez des changements concurrents tant que les propriétaires n’ont pas répondu dans l’issue #1.
- Les modèles, corpus, runners et résultats de benchmark restent locaux : ne les présentez pas comme disponibles sans chemin local et validation reproductible.
- Les décisions sont append-only : rectifiez-les par une nouvelle entrée, sans réécrire l’historique.
