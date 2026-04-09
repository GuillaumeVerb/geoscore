# Design API

## Conventions

- Préfixe versionné recommandé : `/api/v1`.
- Réponses JSON ; erreurs avec structure stable (ex. `error`, `message`, `details`).

## Ressources à spécifier

- Authentification (si applicable)
- CRUD ou actions métier (analyses, rapports, comptes)
- Pagination et filtres communs

## Évolution

- Dépréciation annoncée sur au moins une version ; changelog produit côté doc ou OpenAPI.
