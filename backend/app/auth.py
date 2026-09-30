from __future__ import annotations

from secrets import token_urlsafe
from typing import Callable

from fastapi import Cookie, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .models import UserRole
from .schemas.auth import AuthUser


MOCK_SESSION_COOKIE = "nexus_mock_session"
_sessions: dict[str, AuthUser] = {}


def development_only() -> None:
    if settings.app_env.lower() != "development":
        raise HTTPException(status_code=403, detail="Mock authentication is disabled outside development.")


def create_mock_session(user: AuthUser) -> str:
    development_only()
    token = token_urlsafe(32)
    _sessions[token] = user
    return token


def get_session_user(session_token: str | None) -> AuthUser | None:
    if settings.app_env.lower() != "development" or not session_token:
        return None
    return _sessions.get(session_token)


def delete_mock_session(session_token: str | None) -> None:
    if session_token:
        _sessions.pop(session_token, None)


def _header_fallback(role: str | None, user_id: int | None) -> AuthUser | None:
    if settings.app_env.lower() != "development" or role is None:
        return None
    try:
        parsed_role = UserRole(role.upper())
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Prototype role is not permitted.") from exc
    return AuthUser(user_id=user_id, role=parsed_role, display_name=parsed_role.value.title())


def resolve_user(
    session_token: str | None,
    prototype_role: str | None = None,
    prototype_user_id: int | None = None,
) -> AuthUser | None:
    if not isinstance(session_token, str):
        session_token = None
    session_user = get_session_user(session_token)
    if session_token and session_user is None:
        raise HTTPException(status_code=401, detail="The mock session is invalid or expired.")
    return session_user or _header_fallback(prototype_role, prototype_user_id)


def current_user(session_token: str | None = Cookie(default=None, alias=MOCK_SESSION_COOKIE)) -> AuthUser:
    user = resolve_user(session_token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication is required.")
    return user


def request_user(request: Request) -> AuthUser | None:
    raw_user_id = request.headers.get("X-Prototype-User-Id")
    try:
        user_id = int(raw_user_id) if raw_user_id else None
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Prototype user id is not permitted.") from exc
    return resolve_user(
        request.cookies.get(MOCK_SESSION_COOKIE),
        request.headers.get("X-Prototype-Role"),
        user_id,
    )


class MockAuthMiddleware(BaseHTTPMiddleware):
    public_prefixes = ("/health", "/auth")

    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path in ("/health", "/auth") or request.url.path.startswith(("/health/", "/auth/")):
            return await call_next(request)
        if settings.app_env.lower() != "development":
            return JSONResponse(status_code=401, content={"detail": "Authentication is required; configure Entra/OIDC authentication."})
        try:
            user = request_user(request)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        if user is None:
            return JSONResponse(status_code=401, content={"detail": "Authentication is required."})
        request.state.user = user
        return await call_next(request)