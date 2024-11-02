from pydantic import BaseModel


class UserCreate(BaseModel):
    """DTO for creating new user model."""

    username: str
    password: str
