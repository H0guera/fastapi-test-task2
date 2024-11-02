from sqlalchemy.orm import DeclarativeBase

from test_app.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
