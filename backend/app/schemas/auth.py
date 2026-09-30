from pydantic import BaseModel

from ..models import UserRole


class MockLoginRequest(BaseModel):
    role: UserRole
    user_id: int | None = None


class AuthUser(BaseModel):
    user_id: int | None
    role: UserRole
    display_name: str


class AuthResponse(BaseModel):
    user: AuthUser