from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import AuditLog, Case, CaseStatus, Document, ProcessingJob, ProcessingStatus


def list_cases(db: Session, *, status: CaseStatus | None = None, offset: int = 0, limit: int = 25):
    query = select(Case).order_by(Case.created_at.desc()).offset(offset).limit(limit)
    if status:
        query = query.where(Case.status == status)
    return list(db.scalars(query))


def get_case(db: Session, case_id: int) -> Case | None:
    return db.get(Case, case_id)


def get_documents(db: Session, case_id: int) -> list[Document]:
    return list(db.scalars(select(Document).where(Document.case_id == case_id).order_by(Document.ingested_at.desc())))


def get_audit(db: Session, case_id: int) -> list[AuditLog]:
    return list(db.scalars(select(AuditLog).where(AuditLog.case_id == case_id).order_by(AuditLog.timestamp.desc())))


def record_audit(db: Session, *, user_id: int | None, case_id: int, action: str, resource_type: str, resource_id: str | None, result: str = "SUCCESS") -> AuditLog:
    audit = AuditLog(user_id=user_id, case_id=case_id, action=action, resource_type=resource_type, resource_id=resource_id, result=result)
    db.add(audit)
    return audit


def start_processing(db: Session, *, case: Case, document: Document, user_id: int | None) -> ProcessingJob:
    job = ProcessingJob(document_id=document.id, job_type="FIR_PIPELINE", status=ProcessingStatus.PENDING)
    document.processing_status = ProcessingStatus.PENDING
    db.add(job)
    record_audit(db, user_id=user_id, case_id=case.id, action="PROCESSING_STARTED", resource_type="DOCUMENT", resource_id=str(document.id))
    return job


def update_status(db: Session, *, case: Case, status: CaseStatus, user_id: int | None) -> Case:
    case.status = status
    record_audit(db, user_id=user_id, case_id=case.id, action="STATUS_UPDATED", resource_type="CASE", resource_id=str(case.id))
    return case