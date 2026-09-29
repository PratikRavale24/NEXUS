from backend.app.schemas.finding import (
    FindingReviewRequest,
)


def test_valid_review_request():

    request = FindingReviewRequest(
        status="UNDER_REVIEW",
        review_notes=(
            "Requires further investigator verification."
        ),
    )

    assert (
        request.status
        == "UNDER_REVIEW"
    )


def test_review_request_without_notes():

    request = FindingReviewRequest(
        status="NEW"
    )

    assert request.review_notes is None