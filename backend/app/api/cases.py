from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from ..config import settings
from ..auth import MOCK_SESSION_COOKIE, resolve_user
from ..database import get_db
from ..models import CaseStatus, Document, UserRole
from ..schemas.case import CaseDetail, CaseStatusUpdate, CaseSummary, DocumentMetadata, ProcessingStart, PrototypeIdentity, TimelineEntry
from ..services.case_service import get_audit, get_case, get_documents, list_cases, start_processing, update_status

router = APIRouter(prefix="/cases", tags=["Cases"])


def prototype_identity(
    x_prototype_role: str | None = Header(default=None),
    x_prototype_user_id: int | None = Header(default=None),
    session_token: str | None = Cookie(default=None, alias=MOCK_SESSION_COOKIE),
) -> PrototypeIdentity:
    identity = resolve_user(session_token, x_prototype_role, x_prototype_user_id)
    if identity is None and settings.app_env.lower() == "development" and not x_prototype_role:
        return PrototypeIdentity(user_id=x_prototype_user_id, role=UserRole.INVESTIGATOR)
    if identity is None:
        raise HTTPException(status_code=401, detail="Authentication is required.")
    return PrototypeIdentity(user_id=identity.user_id, role=identity.role)


def require(identity: PrototypeIdentity, *roles: UserRole) -> PrototypeIdentity:
    if identity.role not in roles:
        raise HTTPException(status_code=403, detail="This action is not permitted for the current role.")
    return identity


def _documents(documents: list[Document]) -> list[DocumentMetadata]:
    return [DocumentMetadata(id=d.id, filename=d.filename, document_type=d.document_type, sha256_hash=d.sha256_hash, ingested_at=d.ingested_at, processing_status=d.processing_status, provenance=d.storage_path) for d in documents]


@router.get("", response_model=list[CaseSummary])
def get_cases(status: CaseStatus | None = None, offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db), identity: PrototypeIdentity = Depends(prototype_identity)):
    require(identity, UserRole.INVESTIGATOR, UserRole.ANALYST, UserRole.SUPERVISOR, UserRole.ADMIN)
    return list_cases(db, status=status, offset=offset, limit=limit)


@router.get("/{case_id}", response_model=CaseDetail)
def get_case_detail(case_id: int, db: Session = Depends(get_db), identity: PrototypeIdentity = Depends(prototype_identity)):
    require(identity, UserRole.INVESTIGATOR, UserRole.ANALYST, UserRole.SUPERVISOR, UserRole.ADMIN)
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    audit = get_audit(db, case_id)
    return CaseDetail(id=case.id, case_number=case.case_number, title=case.title, status=case.status, created_at=case.created_at, description=case.description, documents=_documents(get_documents(db, case_id)), timeline=[TimelineEntry.model_validate(item) for item in audit])


@router.get("/{case_id}/documents", response_model=list[DocumentMetadata])
def get_case_documents(case_id: int, db: Session = Depends(get_db), identity: PrototypeIdentity = Depends(prototype_identity)):
    require(identity, UserRole.INVESTIGATOR, UserRole.ANALYST, UserRole.SUPERVISOR, UserRole.ADMIN)
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="Case not found.")
    return _documents(get_documents(db, case_id))


@router.get("/{case_id}/timeline", response_model=list[TimelineEntry])
def get_case_timeline(case_id: int, db: Session = Depends(get_db), identity: PrototypeIdentity = Depends(prototype_identity)):
    require(identity, UserRole.INVESTIGATOR, UserRole.ANALYST, UserRole.SUPERVISOR, UserRole.ADMIN)
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="Case not found.")
    return [TimelineEntry.model_validate(item) for item in get_audit(db, case_id)]


@router.get("/{case_id}/audit", response_model=list[TimelineEntry])
def get_case_audit(case_id: int, db: Session = Depends(get_db), identity: PrototypeIdentity = Depends(prototype_identity)):
    require(identity, UserRole.SUPERVISOR, UserRole.ADMIN)
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="Case not found.")
    return [TimelineEntry.model_validate(item) for item in get_audit(db, case_id)]


@router.post("/{case_id}/processing", response_model=ProcessingStart)
def initiate_processing(case_id: int, document_id: int, db: Session = Depends(get_db), identity: PrototypeIdentity = Depends(prototype_identity)):
    require(identity, UserRole.INVESTIGATOR, UserRole.SUPERVISOR, UserRole.ADMIN)
    case = get_case(db, case_id)
    document = db.get(Document, document_id)
    if not case or not document or document.case_id != case_id:
        raise HTTPException(status_code=404, detail="Case document not found.")
    job = start_processing(db, case=case, document=document, user_id=identity.user_id)
    db.commit()
    db.refresh(job)
    return ProcessingStart(document_id=document.id, job_id=job.id, status=job.status)


@router.patch("/{case_id}/status", response_model=CaseSummary)
def change_case_status(case_id: int, request: CaseStatusUpdate, db: Session = Depends(get_db), identity: PrototypeIdentity = Depends(prototype_identity)):
    require(identity, UserRole.SUPERVISOR, UserRole.ADMIN)
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    update_status(db, case=case, status=request.status, user_id=identity.user_id)
    db.commit()
    db.refresh(case)
    return case