import asyncio
from getpass import getpass

from currency_exchange.db.session import async_session_factory
from .dbmodels import User, UserCategory


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
