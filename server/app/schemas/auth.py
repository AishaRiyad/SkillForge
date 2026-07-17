from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserResponse


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=128,
        repr=False,
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> str:
        return str(value).strip().lower()


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1,
        repr=False,
    )


class LogoutRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1,
        repr=False,
    )


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_in: int


class LoginResponse(BaseModel):
    user: UserResponse
    tokens: TokenPair


class LogoutAllResponse(BaseModel):
    message: str
    revoked_sessions: int
