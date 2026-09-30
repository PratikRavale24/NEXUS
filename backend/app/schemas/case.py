from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..models import CaseStatus, ProcessingStatus, UserRole


class CaseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_number: str
    title: str
    status: CaseStatus
    created_at: datetime


class DocumentMetadata(BaseModel):
    id: int
    filename: str
    document_type: str
    sha256_hash: str
    ingested_at: datetime
    processing_status: ProcessingStatus
    provenance: str


class TimelineEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action: str
    resource_type: str
    resource_id: str | None
    timestamp: datetime
    result: str | None


class CaseDetail(CaseSummary):
    description: str | None
    documents: list[DocumentMetadata]
    timeline: list[TimelineEntry]


class CaseStatusUpdate(BaseModel):
    status: CaseStatus


class ProcessingStart(BaseModel):
    document_id: int
    job_id: int
    status: ProcessingStatus


class PrototypeIdentity(BaseModel):
    user_id: int | None
    role: UserRole