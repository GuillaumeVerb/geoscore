# Instructions pour les agents (Cursor / automation)

## Contexte

Geoscore est décrit dans `README.md` et structuré par la documentation sous `docs/`. Les règles Cursor dans `.cursor/rules/` complètent ce fichier.

## Priorités

1. Respecter la vision produit et l’architecture documentées avant d’introduire de nouvelles dépendances ou patterns.
2. Pour le scoring, se référer à `docs/02-scoring/` ; ne pas inventer de pondérations non documentées sans le signaler explicitement.
3. Backend Python : conventions dans `.cursor/rules/backend-fastapi.mdc`.
4. Frontend : `.cursor/rules/frontend-nextjs.mdc`.

## Workflow

- Petites itérations, commits logiques.
- Si une spécification manque, proposer une mise à jour courte du doc concerné plutôt que des hypothèses longues dans le code seul.
