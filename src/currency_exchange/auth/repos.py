from collections.abc import Awaitable, Callable
from uuid import UUID

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from currency_exchange.db.session import async_session_factory
from .schemas import (
	UserDbOut,
	UserDbIn,
	UserDbUpdate,
	TokenStateDbOut,
	TokenStateDbIn,
	TokenStateDbUpdate,
)
from currency_exchange.db.repoabc import RepositoryABC
from currency_exchange.db.crud import AsyncCrudMixin
from .dbmodels import User, TokenState
from . import errors


class ExceptionHandlerMixin:
	_db_exception_handlers: dict[
		type[Exception], Callable[[Exception], ...] | Awaitable[...]
	] = {}

	async def _handle_db_exception(self, coro: Awaitable):
		try:
			return await coro
		except errors.DataError:
			raise
		except sqlalchemy.exc.DBAPIError as e:
			handlers = getattr(self, "_db_exception_handlers", None)
			if not handlers:
				self._handle_sqlalchemy_dbapi_exc(e)
			for exc_type in type(e).mro():
				if exc_type is sqlalchemy.exc.DBAPIError:
					self._handle_sqlalchemy_dbapi_exc(e)
				exc_handler = self._db_exception_handlers.get(exc_type)
				if exc_handler:
					exc_handler(self, e)

	def _handle_sqlalchemy_dbapi_exc(self, exc: sqlalchemy.exc.DBAPIError) -> None:
		raise errors.DataError(f"Error while performing operation: {exc.orig}")


class UsersRepository(AsyncCrudMixin, ExceptionHandlerMixin, RepositoryABC):
	_root_model = User
	_object_does_not_exist_error = errors.UserDoesNotExistError
	_input_model = UserDbIn
	_output_model = UserDbOut
	_db_exception_handlers = {}

	def __init__(self, db_session_maker: async_sessionmaker[AsyncSession]):
		self._session_factory = db_session_maker

	async def get(self, user_identity: str | int) -> UserDbOut:
		criteria, criteria_str = self._get_identity_criteria(user_identity)
		return await self._get_object(criteria, f"No such user with {criteria_str}")

	async def get_all(self) -> list[UserDbOut]:
		return await self._get_all_objects()

	async def save(self, user: UserDbIn | UserDbUpdate) -> UserDbOut | None:
		if isinstance(user, UserDbUpdate):
			await self.update(user)
			return
		user_model = await self._handle_db_exception(self._save_object(user))
		return UserDbOut.model_validate(user_model)

	async def update(self, user: UserDbUpdate) -> None:
		update_values = user.model_dump(
			exclude={"old_username", "id"}, exclude_unset=True
		)
		criteria, criteria_str = self._get_identity_criteria(
			user.id or user.old_username
		)
		if update_values:
			await self._handle_db_exception(
				self._update_object(
					criteria, update_values, f"No such user with {criteria_str}"
				)
			)

	async def delete(self, user_identity: str | int) -> None:
		criteria, criteria_str = self._get_identity_criteria(user_identity)
		await self._delete_object(criteria, f"No such user with {criteria_str}")

	@staticmethod
	def create_root_model_from_dto(dto: UserDbIn) -> User:
		return User(**dto.model_dump())

	def process_final_model(self, model: User) -> None:
		if (
			not model.has_hashed_password()
		):  # password assignment was straight, therefore has a raw value
			model.set_password(model.password)

	@staticmethod
	def _get_identity_criteria(user_identity: str | int):
		if isinstance(user_identity, str) and not user_identity.isdigit():
			criteria = User.username == user_identity
			criteria_str = (
				f"username {user_identity}"  # for informative exception message
			)
		else:
			criteria = User.id == int(user_identity)
			criteria_str = f"id {user_identity}"
		return criteria, criteria_str

	def _handle_sqlalchemy_integrity_exception(
		self, exc: sqlalchemy.exc.IntegrityError
	) -> None:
		exc_txt = str(exc.orig)
		if "unique" in exc_txt and "username" in exc_txt:
			raise errors.UserAlreadyExistsError(
				"User with such username already exists"
			)

	_db_exception_handlers.update(
		{sqlalchemy.exc.IntegrityError: _handle_sqlalchemy_integrity_exception}
	)


class TokenStateRepository(AsyncCrudMixin, ExceptionHandlerMixin, RepositoryABC):
	_root_model = TokenState
	_object_does_not_exist_error = errors.TokenDoesNotExistError
	_input_model = TokenStateDbIn
	_output_model = TokenStateDbOut
	_db_exception_handlers = {}

	def __init__(self, db_session_maker: async_sessionmaker[AsyncSession]):
		self._session_factory = db_session_maker

	async def get(self, token_id: str | UUID) -> TokenStateDbOut:
		token_id = self._normalize_uuid(token_id)
		return await self._get_object(
			TokenState.id == token_id, f"No such token with {token_id}"
		)

	async def get_all(self) -> list[TokenStateDbOut]:
		return await self._get_all_objects()

	async def save(
		self, token_state: TokenStateDbIn | TokenStateDbUpdate
	) -> TokenStateDbOut | None:
		if isinstance(token_state, TokenStateDbUpdate):
			await self.update(token_state)
			return

		token_state_model = await self._handle_db_exception(
			self._save_object(token_state)
		)
		return TokenStateDbOut.model_validate(token_state_model)

	async def update(self, token_state: TokenStateDbUpdate) -> None:
		update_values = token_state.model_dump(exclude={"id"}, exclude_unset=True)
		if update_values:
			await self._handle_db_exception(
				self._update_object(
					self._root_model.id == token_state.id,
					update_values,
					f"No such token with id {token_state.id.hex}",
				)
			)

	async def delete(self, token_id: str | UUID) -> None:
		token_id = self._normalize_uuid(token_id)
		await self._delete_object(
			self._root_model.id == token_id, f"No such token with id {token_id.hex}"
		)

	async def get_users_tokens_per_device(
		self, user_id: int, device_id: str
	) -> list[TokenStateDbOut]:
		async with self._session_factory() as session:
			res = await session.execute(
				select(TokenState).where(
					TokenState.user_id == user_id,
					TokenState.device_id == device_id,
					TokenState.revoked == False,
				)
			)
		return [
			TokenStateDbOut.model_validate(t_model) for t_model in res.scalars().all()
		]

	async def get_users_tokens(self, user_id: int):
		async with self._session_factory() as session:
			res = await session.execute(
				select(TokenState).where(
					TokenState.user_id == user_id, TokenState.revoked == False
				)
			)
		return [
			TokenStateDbOut.model_validate(t_model) for t_model in res.scalars().all()
		]

	async def get_users_tokens_by_jti(
		self, user_id: int, jtis: list[str]
	) -> list[TokenStateDbOut]:
		async with self._session_factory() as session:
			res = await session.execute(
				select(TokenState).where(
					TokenState.user_id == user_id,
					TokenState.id.in_(jtis),
					TokenState.revoked == False,
				)
			)

		return [
			TokenStateDbOut.model_validate(t_model) for t_model in res.scalars().all()
		]

	@staticmethod
	def create_root_model_from_dto(dto: TokenStateDbIn) -> TokenState:
		return TokenState(**dto.model_dump())

	@staticmethod
	def _normalize_uuid(id_):
		if isinstance(id_, str):
			return UUID(hex=id_)
		return id_


RepoType = RepositoryABC
RepoClsType = type[RepoType]

_repository_singletones = {}


def _get_repo(repo_type: type[RepoType]) -> RepoType:
	repo = _repository_singletones.get(repo_type)
	if repo is None:
		repo = repo_type(async_session_factory)
		_repository_singletones[repo_type] = repo
	return repo


def get_users_repo() -> UsersRepository:
	return _get_repo(UsersRepository)


def get_token_state_repo() -> TokenStateRepository:
	return _get_repo(TokenStateRepository)
