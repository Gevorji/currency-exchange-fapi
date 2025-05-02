from datetime import timedelta
from pathlib import Path
from typing import Annotated, Literal, Optional
from enum import Enum

from pydantic import StrictStr, IPvAnyAddress, field_validator, PositiveInt, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# DeclarativeBase common for all project models
SQLAModelBase = 'currency_exchange.db.base.Base'

class GeneralSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    DEBUG: Literal['True', 'False', '1', '0'] = 'False'

    @field_validator('DEBUG', mode='after')
    @classmethod
    def validate_debug(cls, value: str):
        return {
            'True': True,
            'False': False,
            '1': True,
            '0': False,
        }[value.capitalize()]

class DbConnectionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_prefix='DB_', extra='ignore')

    DBMS: Annotated[str, Field(frozen=True)] = 'postgresql'
    DRIVER: str = 'asyncpg'
    HOST: StrictStr | IPvAnyAddress = 'localhost'
    PORT: Annotated[PositiveInt, Field(gt=0, lt=65535, coerce_numbers_to_str=True)] = '5432'
    USERNAME: str
    PASSWORD: str
    DB_NAME: str

    @field_validator('HOST', mode='after')
    @classmethod
    def validate_host(cls, value):
        return value.lower()

class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_prefix='AUTH_', extra='ignore')

    class JWTAlgorithms(Enum):
        HS256 = 'HS256'
        RS256 = 'RS256'
        ES256 = 'ES256'

    JWT_ISSUER: str = 'gevorji.currency-exchange.auth'
    JWT_SIGN_ALGORITHM: JWTAlgorithms = JWTAlgorithms.RS256
    JWT_PUB_KEY_PATH: Path
    JWT_PRIV_KEY_PATH: Path
    JWT_ACCESS_DURATION: timedelta = timedelta(seconds=1800)
    JWT_REFRESH_DURATION: timedelta = timedelta(seconds=1209600)
    JWT_NBF_DURATION: Optional[timedelta] = None
    JWT_JTIS: bool = True
    PASSWORD_VALIDATORS: list[str] = [
        'currency_exchange.auth.services.passwordvalidation.min_length_validator',
        'currency_exchange.auth.services.passwordvalidation.no_whitespace_chars_validator'
    ]
    PASSWORD_HASHERS: list[str] = [
        'currency_exchange.auth.services.passwordhashing.BCryptHasher'
    ]
    MIN_PASSWORD_LENGTH: int = 8
    USERNAME_MIN_LENGTH: int = 5


class PermissionsConfig(BaseSettings):
    scopes: dict[str, str] = {
        'all': 'All permissions granted',
        'currency:create': 'Create currency',
        'currency:delete': 'Delete currency',
        'currency:update': 'Update currency',
        'currency:request': 'Request currencies',
        'exch_rate:create': 'Create exchange rate',
        'exch_rate:delete': 'Delete exchange rate',
        'exch_rate:update': 'Update exchange rate',
        'exch_rate:request': 'Request exchange rates',
    }

    scopes_usr_category_bindings: dict[str, list[str]] = {
        'API_CLIENT': [
        'currency:create',
        'currency:update',
        'currency:request',
        'exch_rate:create',
        'exch_rate:update',
        'exch_rate:request',
        ],
        'MANAGER': [
        'currency:create',
        'currency:update',
        'currency:request',
        'exch_rate:create',
        'exch_rate:update',
        'exch_rate:request',
        ],
        'ADMIN': ['all'],
    }

db_conn_settings = DbConnectionSettings()
general_settings = GeneralSettings()
auth_settings = AuthConfig()
permissions_settings = PermissionsConfig()