"""Domain enums aligned with docs/01-architecture/api-design.md and pipeline page types."""

from enum import Enum


class ScanStatus(str, Enum):
    """Lifecycle values from api-design.md (status lifecycle)."""

    CREATED = "created"
    QUEUED = "queued"
    FETCHING = "fetching"
    RENDERING = "rendering"
    EXTRACTING = "extracting"
    SCORING_RULES = "scoring_rules"
    SCORING_LLM = "scoring_llm"
    AGGREGATING = "aggregating"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class PageType(str, Enum):
    """Page types from docs/01-architecture/pipeline-analysis.md."""

    HOMEPAGE = "homepage"
    LANDING_PAGE = "landing_page"
    PRODUCT_PAGE = "product_page"
    PRICING_PAGE = "pricing_page"
    ARTICLE = "article"
    ABOUT_PAGE = "about_page"
    APP_PAGE = "app_page"
    OTHER = "other"


class AnalysisConfidence(str, Enum):
    """Coarse confidence label for analysis_confidence (explicit, not black-box)."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"
    LIMITED = "limited"
