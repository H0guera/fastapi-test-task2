from pydantic import BaseModel


class UserBase(BaseModel):
    """Base user's model."""

    username: str


class UserCreate(UserBase):
    """DTO for creating new user model."""

    password: str


class TokenInfo(BaseModel):
    """Success login/refresh response model."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
