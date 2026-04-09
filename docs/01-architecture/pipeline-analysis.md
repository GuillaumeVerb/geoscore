# Pipeline d’analyse

## Étapes (brouillon)

1. **Entrée** : URL, identifiants métier, paramètres géographiques ou de marché.
2. **Collecte** : données nécessaires aux règles (crawling, APIs tierces, etc.).
3. **Extraction** : structuration selon `docs/02-scoring/extraction-schema-v1.md`.
4. **Scoring** : application du moteur v1.
5. **Recommandations** : mapping depuis `docs/02-scoring/recommendations-mapping.md`.
6. **Sortie** : persistance + réponse API / rendu UI.

## Non-fonctionnel

- Timeouts, retries, files d’attente pour les étapes longues.
- Journalisation des échecs partiels.
