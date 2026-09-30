from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
)

from ..graph import driver
from ..schemas.finding import (
    FindingDetail,
    FindingReviewRequest,
    FindingSummary,
)
from ..services.finding_service import (
    get_finding,
    list_findings,
    review_finding,
)


router = APIRouter(
    prefix="/findings",
    tags=["Findings"],
)


@router.get(
    "",
    response_model=list[FindingSummary],
)
def get_all_findings():

    return list_findings(driver)


@router.get(
    "/{finding_id}",
    response_model=FindingDetail,
)
def get_finding_by_id(
    finding_id: str,
):

    finding = get_finding(driver, finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return finding


@router.post(
    "/{finding_id}/review",
)
def review_finding_by_id(
    finding_id: str,
    request: FindingReviewRequest,
):

    try:
        result = review_finding(
            driver,
            finding_id,
            request.status,
            request.review_notes,
        )

        if result is None:

            raise HTTPException(
                status_code=404,
                detail="Finding not found.",
            )

        return {
            "status": "ok",
            "finding": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

