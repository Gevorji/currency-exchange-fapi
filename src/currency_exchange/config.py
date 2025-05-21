from datetime import timedelta
from pathlib import Path
from typing import Annotated, Literal, Optional
from enum import Enum

from pydantic import StrictStr, IPvAnyAddress, field_validator, PositiveInt, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# DeclarativeBase common for all project models
SQLAModelBase = "currency_exchange.db.base.Base"


class GeneralSettings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", extra="ignore")

	DEBUG: Literal["True", "False", "1", "0"] = "False"
	APP_LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

	@field_validator("DEBUG", mode="after")
	@classmethod
	def validate_debug(cls, value: str):
		return {
			"True": True,
			"False": False,
			"1": True,
			"0": False,
		}[value.capitalize()]


class DbConnectionSettings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_prefix="DB_", extra="ignore")

	# following options is used to build a URL for sqlalchemy engine
	DBMS: Annotated[str, Field(frozen=True)] = "postgresql"
	DRIVER: str = "asyncpg"
	HOST: StrictStr | IPvAnyAddress = "localhost"
	PORT: Annotated[PositiveInt, Field(gt=0, lt=65535, coerce_numbers_to_str=True)] = (
		"5432"
	)

	# following options must be set in .env
	USERNAME: str
	PASSWORD: str
	DB_NAME: str

	@field_validator("HOST", mode="after")
	@classmethod
	def validate_host(cls, value):
		return value.lower()


class AuthConfig(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=".env", env_prefix="AUTH_", extra="ignore"
	)

	# algorithms that is available to use for jwt hash computation and checking, do not change this.
	class JWTAlgorithms(Enum):
		HS256 = "HS256"
		RS256 = "RS256"
		ES256 = "ES256"

	# string that defines the content in key 'iss' in jwt, issued by the app
	JWT_ISSUER: str = "gevorji.currency-exchange.auth"

	# algorithm used for signing jwts
	JWT_SIGN_ALGORITHM: JWTAlgorithms = JWTAlgorithms.RS256

	# keys must be given in a files, an application then reads this files and operates with keys
	JWT_PUB_KEY_PATH: Path
	JWT_PRIV_KEY_PATH: Path

	# duration of issued jwts
	JWT_ACCESS_DURATION: timedelta = timedelta(seconds=1800)
	JWT_REFRESH_DURATION: timedelta = timedelta(seconds=1209600)

	# value that specifies a duration after jwt issuance upon which a token can't be processed (nbf field in jwt)
	JWT_NBF_DURATION: Optional[timedelta] = None

	# defines whether issued jwts is given a unique id (usually uuid), not recommended to change this, because a
	# mechanism of tokens blacklist heavily relies on token ids
	JWT_JTIS: bool = True

	# absolute import paths of validator functions used to validate users password
	PASSWORD_VALIDATORS: list[str] = [
		"currency_exchange.auth.services.passwordvalidation.min_length_validator",
		"currency_exchange.auth.services.passwordvalidation.no_whitespace_chars_validator",
	]

	# absolute import paths of hashers used to obtain a hash of users password
	PASSWORD_HASHERS: list[str] = [
		"currency_exchange.auth.services.passwordhashing.BCryptHasher"
	]
	MIN_PASSWORD_LENGTH: int = 8
	USERNAME_MIN_LENGTH: int = 5


# Your applications access scopes.
# The scopes are used to authorize requests to application endpoints. You restrict access to endpoints
# by using FastAPI's Security dependency tool, called with verify_access dependency from auth package.
# scopes_usr_category_bindings init parameter here is used to specify the default scopes for each user category.
class PermissionsConfig(BaseSettings):
	scopes: dict[str, str] = {
		"all": "All permissions granted",
		"currency:create": "Create currency",
		"currency:delete": "Delete currency",
		"currency:update": "Update currency",
		"currency:request": "Request currencies",
		"exch_rate:create": "Create exchange rate",
		"exch_rate:delete": "Delete exchange rate",
		"exch_rate:update": "Update exchange rate",
		"exch_rate:request": "Request exchange rates",
	}

	scopes_usr_category_bindings: dict[str, list[str]] = {
		"API_CLIENT": [
			"currency:create",
			"currency:update",
			"currency:request",
			"exch_rate:create",
			"exch_rate:update",
			"exch_rate:request",
		],
		"MANAGER": [
			"currency:create",
			"currency:update",
			"currency:request",
			"exch_rate:create",
			"exch_rate:update",
			"exch_rate:request",
		],
		"ADMIN": ["all"],
	}


db_conn_settings = DbConnectionSettings()
general_settings = GeneralSettings()
auth_settings = AuthConfig()
permissions_settings = PermissionsConfig()
