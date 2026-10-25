from pydantic import EmailStr, Field

from backend.app.schemas.common import StrictModel


class RegisterRequest(StrictModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)


class LoginRequest(StrictModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(StrictModel):
    id: int
    email: EmailStr
    display_name: str
    role: str


class TokenResponse(StrictModel):
    access_token: str
    token_type: str = "bearer"
