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

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_in: int


class LoginResponse(BaseModel):
    user: UserResponse
    tokens: TokenPair
