# Stratégie LLM

## Usage envisagé

- Résumés, reformulations, ou extraction assistée **uniquement** si cadré par des schémas et validations.

## Garde-fous

- Données sensibles : politique de rétention et d’anonymisation.
- Coûts : budget par analyse, modèles par tâche.
- Fiabilité : sorties structurées (JSON schema), rejet / retry sur parse invalide.

## Hors scope LLM (à confirmer)

- Calcul du score final sans règles déterministes documentées.
