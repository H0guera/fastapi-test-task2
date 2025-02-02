from typing import Any, AsyncGenerator

import bcrypt
import pytest
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import ConnectionPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from test_app.db.dependencies import get_db_session
from test_app.db.models.tasks import Task
from test_app.db.models.users import User
from test_app.db.utils import create_database, drop_database
from test_app.services.redis.dependency import get_redis_pool
from test_app.settings import settings
from test_app.utils.ensure_types import ensure_bytes, ensure_str
from test_app.utils.task_status import TaskStatus
from test_app.web.application import get_app

USER_PASSWORD = "VedroKumisa"  # noqa: S105
TODO_TASK_STATUS = TaskStatus.TODO
DONE_TASK_STATUS = TaskStatus.DONE


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from test_app.db.meta import meta
    from test_app.db.models import load_all_models

    load_all_models()

    await create_database()

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    """
    Get instance of a fake redis.

    :yield: FakeRedis instance.
    """
    server = FakeServer()
    server.connected = True
    pool = ConnectionPool(connection_class=FakeConnection, server=server)

    yield pool

    await pool.disconnect()


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
    fake_redis_pool: ConnectionPool,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession
    application.dependency_overrides[get_redis_pool] = lambda: fake_redis_pool
    return application


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test", timeout=2.0) as ac:
        yield ac


@pytest.fixture
async def user(
    dbsession: AsyncSession,
) -> User:
    """Fixture for creating existing user."""
    claim_password = USER_PASSWORD
    hashed_password = ensure_str(
        bcrypt.hashpw(password=ensure_bytes(claim_password), salt=bcrypt.gensalt()),
    )
    new_user = User(username="NoskiSNachesom", hashed_password=hashed_password)
    dbsession.add(new_user)
    await dbsession.commit()
    return new_user


@pytest.fixture
async def another_user(
    dbsession: AsyncSession,
) -> User:
    """Fixture for creating another user."""
    claim_password = USER_PASSWORD
    hashed_password = ensure_str(
        bcrypt.hashpw(password=ensure_bytes(claim_password), salt=bcrypt.gensalt()),
    )
    new_user = User(username="AnotherUser", hashed_password=hashed_password)
    dbsession.add(new_user)
    await dbsession.commit()
    return new_user


@pytest.fixture
async def authenticated_headers(
    user: User,
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> dict:
    """Creates access and refresh authorization headers for user."""
    url = fastapi_app.url_path_for("login_user")
    username = user.username
    password = USER_PASSWORD

    response = await client.post(
        url,
        data={"username": username, "password": password},
    )
    tokens = response.json()
    return {
        "access_header": {"Authorization": f"Bearer {tokens['access_token']}"},
        "refresh_header": {"Authorization": f"Bearer {tokens['refresh_token']}"},
    }


@pytest.fixture
async def another_user_access_header(
    another_user: User,
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> dict:
    """Creates access header for another user."""
    url = fastapi_app.url_path_for("login_user")
    username = another_user.username
    password = USER_PASSWORD

    response = await client.post(
        url,
        data={"username": username, "password": password},
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
async def todo_task(
    user: User,
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> Task:
    """Fixture for creating existing task."""
    new_task = Task(
        title="NewTask",
        description="very long description",
        status=TODO_TASK_STATUS,
        user_id=user.id,
    )
    dbsession.add(new_task)
    await dbsession.commit()
    return new_task


@pytest.fixture
async def done_task(
    user: User,
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> Task:
    """Fixture for creating another task."""
    new_task = Task(
        title="AnotherNewTask",
        description="very long description",
        status=DONE_TASK_STATUS,
        user_id=user.id,
    )
    dbsession.add(new_task)
    await dbsession.commit()
    return new_task
