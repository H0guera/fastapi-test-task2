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

    def _verify_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        return bcrypt.checkpw(
            ensure_bytes(plain_password),
            ensure_bytes(hashed_password),
        )

    async def get_user_by_username(self, username: str) -> User | None:
        """Retrieve user by username."""
        stmt = select(User).where(User.username == username)
        result = await self.session.scalars(stmt)
        return result.one_or_none()

    async def authenticate(
        self,
        username: str,
        password: str,
    ) -> User | None:
        """Authenticate and return a user following an username and a password."""
        user = await self.get_user_by_username(username)
        if not user:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self._hash_password(password)
            return None

        verified = self._verify_password(
            plain_password=password,
            hashed_password=user.hashed_password,
        )
        if verified:
            return user
        return None

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
