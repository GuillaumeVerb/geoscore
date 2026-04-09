"""Deterministic scoring — placeholder until Sprint 3; do not embed formulas here yet."""

from app.schemas.issue import Issue
from app.schemas.recommendation import Recommendation
from app.schemas.score import ScoreResult


class ScoringService:
    def score_placeholder(self) -> tuple[ScoreResult, list[Issue], list[Recommendation]]:
        return ScoreResult(), [], []


scoring_service = ScoringService()
