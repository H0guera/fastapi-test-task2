from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from test_app.db.base import Base


class User(Base):
    """Represents a user entity."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(
        String(length=55),
        unique=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024),
        nullable=False,
    )
