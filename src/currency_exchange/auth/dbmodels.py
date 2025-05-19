import re
from typing import Optional, Literal

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import UUID

from .services.passwordvalidation import get_all_password_validators
from .services.passwordhashing import (
	match_password,
	get_password_hash_str,
	get_password_components,
)
from .services.permissions import UserCategory
from currency_exchange.config import auth_settings, SQLAModelBase
from currency_exchange.utils.importobject import import_object


SQLAModelBase = import_object(SQLAModelBase)


class User(SQLAModelBase):
	_PSWD_VALIDATORS = get_all_password_validators()
	_USERNAME_MIN_LENGTH = auth_settings.USERNAME_MIN_LENGTH
	_USERNAME_PATTERN = re.compile("\\w+")

	__tablename__ = "user"

	id: Mapped[int] = mapped_column(primary_key=True)
	username: Mapped[str] = mapped_column(unique=True)
	password: Mapped[Optional[str]] = mapped_column(nullable=False)
	category: Mapped[UserCategory]
	is_active: Mapped[bool] = mapped_column(default=True)

	def __init__(self, **kwargs):
		username, password = kwargs.get("username"), kwargs.get("password")
		self.validate_field_values({"username": username, "password": password})
		self.id = kwargs.get("id")
		self.username = username
		self.category = kwargs.get("category")
		self.is_active = kwargs.get("is_active")
		if password is not None:
			self.set_password(password)

	def set_password(self, password: str) -> None:
		self.validate_password(password)
		self.password = get_password_hash_str(password)

	@classmethod
	def validate_password(cls, password: str) -> None:
		complains = []
		for validator in cls._PSWD_VALIDATORS:
			try:
				validator(password)
			except ValueError as e:
				complains.append(e.args[0])
		if complains:
			raise ValueError(complains)

	def match_password(self, password: str) -> bool:
		if self.password is None:
			raise AttributeError("Password is not set.")
		return match_password(password, self.password)

	def validate_field_values(self, fields: dict):
		errors = {}
		for field_name in fields:
			validator = getattr(self, f"validate_{field_name}", None)
			field_value = fields[field_name]
			if field_value is None:
				continue
			if validator:
				try:
					validator(field_value)
				except ValueError as e:
					errors[field_name] = e.args[0]
		if errors:
			raise ValueError(errors)

	def validate_username(self, username: str) -> None:
		complains = []
		if not re.fullmatch(self._USERNAME_PATTERN, username):
			complains.append("Invalid characters in username")

		if not len(username) >= self._USERNAME_MIN_LENGTH:
			complains.append(f"Minimum username length is {self._USERNAME_MIN_LENGTH}")

		if complains:
			raise ValueError(complains)

	def has_hashed_password(self) -> bool:
		return bool(get_password_components(self.password))


class TokenState(SQLAModelBase):
	__tablename__ = "token_state"

	id = mapped_column(UUID(as_uuid=True), primary_key=True)
	type: Mapped[Literal["refresh", "access"]]
	revoked: Mapped[bool] = mapped_column(default=False)
	device_id: Mapped[str] = mapped_column(default=None)
	expiry_date = mapped_column(TIMESTAMP(timezone=True))
	user_id: Mapped[str] = mapped_column(ForeignKey("user.id"))
