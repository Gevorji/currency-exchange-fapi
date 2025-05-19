import asyncio
import datetime
from getpass import getpass

from sqlalchemy import delete

from currency_exchange.db.session import async_session_factory
from .dbmodels import User, UserCategory, TokenState


async def _save_user_to_db(user: User):
    try:
        async with async_session_factory() as session:
            session.add(user)
            await session.commit()
    except Exception as e:
        print(e)


def create_admin():
    username = input("Enter admin username: ")
    while True:
        password1 = getpass("Enter admin password: ")
        password2 = getpass("Repeat password again: ")

        if password1 == password2:
            break
        else:
            print("Passwords don't match")

    asyncio.run(_save_user_to_db(User(username=username, password=password1, category=UserCategory.ADMIN)))

    print("Admin account created")


def remove_expired_tokens():
    asyncio.run(_remove_expired_tokens())


async def _remove_expired_tokens():
    async with async_session_factory() as session:
        async with session.begin():
            res = await session.execute(
                delete(TokenState).where(TokenState.expiry_date < datetime.datetime.now()).returning(TokenState.id)
            )
        print(f'Removed {len(res.fetchall())} expired tokens')
