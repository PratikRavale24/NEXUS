from fastapi import APIRouter, Cookie, Depends, Response

from ..auth import MOCK_SESSION_COOKIE, create_mock_session, current_user, delete_mock_session, development_only
from ..schemas.auth import AuthResponse, AuthUser, MockLoginRequest


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/mock/login", response_model=AuthResponse)
def mock_login(request: MockLoginRequest, response: Response):
    development_only()
    user = AuthUser(user_id=request.user_id, role=request.role, display_name=request.role.value.title())
    response.set_cookie(key=MOCK_SESSION_COOKIE, value=create_mock_session(user), httponly=True, secure=False, samesite="lax", max_age=60 * 60 * 8, path="/")
    return AuthResponse(user=user)


@router.get("/me", response_model=AuthResponse)
def get_me(user: AuthUser = Depends(current_user)):
    return AuthResponse(user=user)


@router.post("/mock/logout")
def mock_logout(response: Response, session_token: str | None = Cookie(default=None, alias=MOCK_SESSION_COOKIE)):
    delete_mock_session(session_token)
    response.delete_cookie(MOCK_SESSION_COOKIE, path="/")
    return {"status": "ok"}