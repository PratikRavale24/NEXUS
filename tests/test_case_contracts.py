from datetime import datetime

import pytest

from backend.app.api.cases import prototype_identity, require
from backend.app.models import CaseStatus, UserRole
from backend.app.schemas.case import CaseStatusUpdate, TimelineEntry


def test_case_status_and_timeline_contracts():
    request = CaseStatusUpdate(status=CaseStatus.UNDER_REVIEW)
    event = TimelineEntry(
        action="STATUS_UPDATED",
        resource_type="CASE",
        resource_id="42",
        timestamp=datetime(2026, 9, 30),
        result="SUCCESS",
    )

    assert request.status is CaseStatus.UNDER_REVIEW
    assert event.resource_id == "42"


def test_prototype_role_matrix_allows_read_and_restricts_status():
    investigator = prototype_identity(None, None)
    assert investigator.role is UserRole.INVESTIGATOR
    assert require(investigator, UserRole.INVESTIGATOR) is investigator

    with pytest.raises(Exception):
        require(investigator, UserRole.SUPERVISOR, UserRole.ADMIN)


def test_prototype_identity_fails_closed_outside_development(monkeypatch):
    monkeypatch.setattr("backend.app.api.cases.settings.app_env", "production")

    with pytest.raises(Exception) as error:
        prototype_identity("ADMIN", 7)

    assert error.value.status_code == 401