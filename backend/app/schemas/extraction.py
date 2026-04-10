from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExtractionSchema(BaseModel):
    """
    Normalized extraction object — top-level sections from docs/02-scoring/extraction-schema-v1.md.
    Values are placeholders (dict/list) until the extraction pipeline is implemented.
    """

    schema_version: str = Field(default="v1-placeholder", description="Extraction schema version string")
    scan_id: str | None = None
    url_info: dict[str, Any] = Field(default_factory=dict)
    fetch_info: dict[str, Any] = Field(default_factory=dict)
    render_info: dict[str, Any] = Field(default_factory=dict)
    page_detection: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    headings: dict[str, Any] = Field(default_factory=dict)
    content: dict[str, Any] = Field(default_factory=dict)
    links: dict[str, Any] = Field(default_factory=dict)
    media: dict[str, Any] = Field(default_factory=dict)
    structured_data: dict[str, Any] = Field(default_factory=dict)
    trust_signals: dict[str, Any] = Field(default_factory=dict)
    page_features: dict[str, Any] = Field(default_factory=dict)
    derived_metrics: dict[str, Any] = Field(default_factory=dict)
    limitations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Limitations emitted during extraction (distinct from report-level Limitation list)",
    )
    llm_payload_candidate: dict[str, Any] = Field(default_factory=dict)
    pipeline_context: dict[str, Any] | None = Field(
        default=None,
        description="Scoring/fetch hints: partial, is_probably_spa, primary_fetch_method (optional)",
    )


ExtractionSchemaPlaceholder = ExtractionSchema
