from typing import Annotated, Literal
from pydantic import StrictStr, IPvAnyAddress, field_validator, PositiveInt, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class GeneralSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    DEBUG: Literal['True', 'False', '1', '0'] = 'False'

    @field_validator('DEBUG')
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

db_conn_settings = DbConnectionSettings()
general_settings = GeneralSettings()