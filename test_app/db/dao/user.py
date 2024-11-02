from typing import TYPE_CHECKING

import bcrypt
from fastapi import Depends

from test_app.db.dependencies import get_db_session
from test_app.utils.ensure_types import ensure_bytes, ensure_str

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserDAO:
    """Class for accessing user table."""

    def __init__(self, session: "AsyncSession" = Depends(get_db_session)) -> None:
        self.session = session

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return ensure_str(bcrypt.hashpw(password=ensure_bytes(password), salt=salt))
