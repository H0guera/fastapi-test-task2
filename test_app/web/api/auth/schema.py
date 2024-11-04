from pydantic import BaseModel


class UserBase(BaseModel):
    """Base user's model."""

    username: str


class UserCreate(UserBase):
    """DTO for creating new user model."""

    password: str
