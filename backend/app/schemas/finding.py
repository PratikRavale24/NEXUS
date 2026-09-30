from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FindingSubject(BaseModel):
    entity_id: str
    name: str | None = None


class EvidenceReference(BaseModel):
    evidence_id: str
    source_type: str | None = None
    timestamp: datetime | None = None
    case_id: str | None = None


class FindingSummary(BaseModel):
    finding_id: str
    finding_type: str
    status: str

    description: str

    model: str | None = None
    model_score: float | None = None

    subjects: list[FindingSubject] = Field(
        default_factory=list
    )

    location_name: str | None = None
    participant_count: int | None = None

    window_start: datetime | None = None
    window_end: datetime | None = None


class FindingDetail(FindingSummary):
    reasons: list[str] = Field(
        default_factory=list
    )

    evidence: list[EvidenceReference] = Field(
        default_factory=list
    )

    method: str | None = None

    case_ids: list[str] = Field(
        default_factory=list
    )

    review_notes: str | None = None


class FindingReviewRequest(BaseModel):
    status: Literal[
        "NEW",
        "UNDER_REVIEW",
        "CONFIRMED",
        "REJECTED",
    ]
    review_notes: str | None = None