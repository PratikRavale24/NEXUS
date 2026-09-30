from fastapi.testclient import TestClient

from backend.app.api.cases import require
from backend.app.config import settings
from backend.app.main import app
from backend.app.models import UserRole
from backend.app.schemas.case import PrototypeIdentity


client = TestClient(app)


def test_mock_login_me_and_logout_use_httponly_cookie(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "development")

    login = client.post("/auth/mock/login", json={"role": "ANALYST"})
    assert login.status_code == 200
    assert "nexus_mock_session=" in login.headers["set-cookie"]
    assert "HttpOnly" in login.headers["set-cookie"]
    assert login.json()["user"]["role"] == "ANALYST"

    assert client.get("/auth/me").json()["user"]["role"] == "ANALYST"
    assert client.post("/auth/mock/logout").status_code == 200
    assert client.get("/auth/me").status_code == 401


def test_mock_auth_fails_closed_outside_development(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")

    assert client.post("/auth/mock/login", json={"role": "ADMIN"}).status_code == 403
    assert client.get("/health").status_code == 200
    assert client.get("/entities/search?q=alice").status_code == 401


def test_case_role_boundary_preserves_status_restriction():
    investigator = PrototypeIdentity(user_id=None, role=UserRole.INVESTIGATOR)
    supervisor = PrototypeIdentity(user_id=None, role=UserRole.SUPERVISOR)

    assert require(supervisor, UserRole.SUPERVISOR) is supervisor
    try:
        require(investigator, UserRole.SUPERVISOR, UserRole.ADMIN)
    except Exception as error:
        assert error.status_code == 403
    else:
        raise AssertionError("investigators must not update case status")