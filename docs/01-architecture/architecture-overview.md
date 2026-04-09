# Vue d’ensemble architecture

## Composants

- **API** : FastAPI — exposition des endpoints métier et orchestration légère.
- **Frontend** : Next.js — interface utilisateur et appels API.
- **Moteur de scoring** : logique déterministe + éventuellement enrichissement LLM selon `docs/02-scoring/llm-strategy.md`.
- **Persistance** : base relationnelle ou adaptée au schéma défini dans `database-schema.md`.

## Principes

- Séparation scoring / ingestion / présentation.
- Traçabilité des exécutions d’analyse (audit, debug).
