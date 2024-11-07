from datetime import timedelta
from typing import TYPE_CHECKING

import bcrypt
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy import select

from test_app.db.dependencies import get_db_session
from test_app.db.models.users import User
from test_app.services.redis.dependency import get_redis_pool
from test_app.settings import settings
from test_app.utils.ensure_types import ensure_bytes, ensure_str
from test_app.web.api.auth.schema import UserCreate
from test_app.web.api.exceptions import UserAlreadyExistsError

if TYPE_CHECKING:
    from redis.asyncio import ConnectionPool
    from sqlalchemy.ext.asyncio import AsyncSession


class UserDAO:
    """Class for accessing user table."""

    def __init__(
        self,
        session: "AsyncSession" = Depends(get_db_session),
        redis_pool: "ConnectionPool" = Depends(get_redis_pool),
    ) -> None:
        self.session = session
        self.redis_pool = redis_pool
        self.refresh_jwt_prefix = "token_refresh"

    async def _get_redis(self) -> Redis:
        async with Redis(connection_pool=self.redis_pool) as redis:
            return redis

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

    def _create_refresh_token_key(
        self,
        user_id: int,
        token: str,
    ) -> str:
        return f"{self.refresh_jwt_prefix}:user_{user_id}:{token}"

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

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve user by id."""
        stmt = select(User).where(User.id == user_id)
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

    async def save_refresh_token_to_redis(
        self,
        user: User,
        token: str,
        expire_days: int = settings.auth_jwt.refresh_token_expire_days,
    ) -> None:
        """Saves user's refresh token to redis."""
        redis = await self._get_redis()
        key = self._create_refresh_token_key(
            user_id=user.id,
            token=token,
        )
        await redis.setex(
            name=key,
            time=timedelta(days=expire_days),
            value=1,
        )
