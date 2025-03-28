from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from currency_exchange.config import db_conn_settings, general_settings

engine = create_async_engine(
    URL.create(
        drivername=f'{db_conn_settings.DBMS}+{db_conn_settings.DRIVER}',
        host=db_conn_settings.HOST,
        port=db_conn_settings.PORT,
        username=db_conn_settings.USERNAME,
        password=db_conn_settings.PASSWORD,
        database=db_conn_settings.DB_NAME,
    ), echo=general_settings.DEBUG
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
