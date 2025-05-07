import secrets
import string

import pytest
import asyncpg

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncConnection
from httpx import AsyncClient, ASGITransport

from currency_exchange.config import auth_settings
from currency_exchange.config import db_conn_settings
from currency_exchange.db.base import Base as BaseModel
import currency_exchange.db.session
import currency_exchange.auth.repos
import currency_exchange.currency_exchange.fapiadoption.appadapter

TEST_DB_NAME = f'test_{db_conn_settings.DB_NAME}'


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
async def create_test_database(anyio_backend):
    conn_params = dict(
        host=db_conn_settings.HOST,
        port=db_conn_settings.PORT,
        user=db_conn_settings.USERNAME,
        password=db_conn_settings.PASSWORD,
        database=db_conn_settings.DB_NAME
    )
    connection = await asyncpg.connect(**conn_params)

    db_conn_settings.DB_NAME = TEST_DB_NAME

    await connection.execute(f'DROP DATABASE IF EXISTS {TEST_DB_NAME};')
    await connection.execute(f'CREATE DATABASE {TEST_DB_NAME};')
    connection.close()

    yield
    connection = await asyncpg.connect(**conn_params)
    await connection.execute(f'DROP DATABASE IF EXISTS {TEST_DB_NAME};')
    connection.close()


@pytest.fixture(scope="session")
async def sqlalchemy_engine(create_test_database):
    db_conn_settings.DB_NAME = TEST_DB_NAME
    engine = create_async_engine(
        URL.create(
                drivername=f'{db_conn_settings.DBMS}+{db_conn_settings.DRIVER}',
                host=db_conn_settings.HOST,
                port=db_conn_settings.PORT,
                username=db_conn_settings.USERNAME,
                password=db_conn_settings.PASSWORD,
                database=db_conn_settings.DB_NAME,
        ), echo=True
    )

    yield engine
    await engine.dispose(close=True)


@pytest.fixture(scope="session")
async def create_db_schema(sqlalchemy_engine):
    async with sqlalchemy_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


@pytest.fixture(scope="session")
async def db_connection(create_db_schema, sqlalchemy_engine) -> AsyncConnection:
    connection = await sqlalchemy_engine.connect()
    yield connection
    await connection.close()


@pytest.fixture(autouse=True)
async def rollback_changes_made_to_db(db_connection): # changes made during each test are rolled back
    transaction = await db_connection.begin()
    yield
    await transaction.rollback()


@pytest.fixture(scope="session")
async def local_sessionmaker(db_connection):
    return async_sessionmaker(bind=db_connection, expire_on_commit=False, join_transaction_mode='create_savepoint')


@pytest.fixture(autouse=True)
async def mock_auth_app_sessionmaker(monkeypatch, local_sessionmaker):
    monkeypatch.setattr(currency_exchange.auth.repos,
                        'async_session_factory', local_sessionmaker)

@pytest.fixture(autouse=True)
async def mock_currency_exchange_app_sessionmaker(monkeypatch, local_sessionmaker):
    monkeypatch.setattr(currency_exchange.currency_exchange.fapiadoption.appadapter,
                        'async_session_factory', local_sessionmaker)

@pytest.fixture
async def db_session(local_sessionmaker) -> AsyncSession:
    session = local_sessionmaker()
    yield session
    await session.close()


@pytest.fixture
async def asgi_transport(app):
    return ASGITransport(app=app)


@pytest.fixture
async def request_client(asgi_transport):
    client = AsyncClient(transport=asgi_transport, base_url='http://127.0.0.1')
    yield client
    await client.aclose()


@pytest.fixture(scope='session')
def get_random_password():

    def _get_random_password(length: int):
        charset = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(charset) for i in range(length))

    return _get_random_password

