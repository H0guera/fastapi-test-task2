from typing import TYPE_CHECKING

import bcrypt
from fastapi import Depends
from sqlalchemy import select

from test_app.db.dependencies import get_db_session
from test_app.db.models.users import User
from test_app.utils.ensure_types import ensure_bytes, ensure_str
from test_app.web.api.auth.schema import UserCreate
from test_app.web.api.exceptions import UserAlreadyExistsError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserDAO:
    """Class for accessing user table."""

    def __init__(self, session: "AsyncSession" = Depends(get_db_session)) -> None:
        self.session = session

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return ensure_str(bcrypt.hashpw(password=ensure_bytes(password), salt=salt))

    async def get_user_by_username(self, username: str) -> User | None:
        """Retrieve user by username."""
        stmt = select(User).where(User.username == username)
        result = await self.session.scalars(stmt)
        return result.one_or_none()

    async def create_user_model(
        self,
        user_create: UserCreate,
    ) -> User | None:
        """
        Add single user to session.

        :param user_create: user credentials.
        :return: created user instance or raise exception.
        """
        existing_user = await self.get_user_by_username(user_create.username)
        if existing_user is not None:
            raise UserAlreadyExistsError

        hashed_password = self._hash_password(user_create.password)
        user = User(username=user_create.username, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        return user
