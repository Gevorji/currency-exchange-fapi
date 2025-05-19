import base64
import uuid
from collections import namedtuple

from sqlalchemy import select, func

from currency_exchange.auth.dbmodels import TokenState, User

EncodedToken = namedtuple("EncodedToken", ["str", "header", "payload"])


async def get_token_state_from_db(token_id: str | uuid.UUID, session) -> TokenState:
	if isinstance(token_id, str):
		token_id = uuid.UUID(hex=token_id)
	res = await session.execute(select(TokenState).where(TokenState.id == token_id))
	token = res.scalar_one_or_none()
	return token


async def add_token_state_to_db(token_state: TokenState, session):
	async with session.begin():
		session.add(token_state)
	return token_state


async def get_user_from_db(user_id: int, session) -> User:
	res = await session.execute(select(User).where(User.id == user_id))
	return res.scalar_one()


async def count_users_in_db(username: str, session):
	res = await session.execute(
		select(func.count()).select_from(User).where(User.username == username)
	)
	return res.scalar_one()


def b64_encode_credentials(username: str, password: str):
	return base64.b64encode(f"{username}:{password}".encode()).decode()
