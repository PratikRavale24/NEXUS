from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
)

from ..config import settings
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
from neo4j import GraphDatabase


router = APIRouter(
    prefix="/findings",
    tags=["Findings"],
)


def get_driver():
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(
            settings.neo4j_user,
            settings.neo4j_password,
        ),
    )


@router.get(
    "",
    response_model=list[FindingSummary],
)
def get_all_findings():

    driver = get_driver()

    try:

        driver.verify_connectivity()

        return list_findings(
            driver
        )

    finally:
        driver.close()


@router.get(
    "/{finding_id}",
    response_model=FindingDetail,
)
def get_finding_by_id(
    finding_id: str,
):

    driver = get_driver()

    try:

        driver.verify_connectivity()

        finding = get_finding(
            driver,
            finding_id,
        )

        if finding is None:

            raise HTTPException(
                status_code=404,
                detail="Finding not found.",
            )

        return finding

    finally:
        driver.close()


@router.post(
    "/{finding_id}/review",
)
def review_finding_by_id(
    finding_id: str,
    request: FindingReviewRequest,
):

    driver = get_driver()

    try:

        driver.verify_connectivity()

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

    finally:
        driver.close()