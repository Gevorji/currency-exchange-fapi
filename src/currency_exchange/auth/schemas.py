from datetime import datetime, timedelta
from typing import Optional, Literal

from pydantic import BaseModel, UUID4, ConfigDict, field_validator, model_validator

from .services.permissions import UserCategory


class _UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    category: UserCategory = UserCategory.API_CLIENT
    is_active: bool = True


class UserDbIn(_UserBase):
    password: str


class UserDbOut(_UserBase):
    id: int
    password: str


class UserOut(_UserBase):
    id: int


class UserDbUpdate(_UserBase):
    id: Optional[int] = None
    old_username: Optional[str] = None

    @model_validator(mode='after')
    def ensure_either_id_or_username_is_set(self):
        if self.id is None and self.old_username is None:
            raise ValueError('Either id or old_username must be set')


class _TokenStateBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    revoked: Optional[bool] = False


class TokenStateDbIn(_TokenStateBase):
    id: UUID4
    type: Literal['access', 'refresh']
    device_id: Optional[str] = None
    expiry_date: datetime
    user_id: int


class TokenStateDbOut(TokenStateDbIn): ...


class TokenStateDbUpdate(_TokenStateBase):
    id: UUID4


class UserCreatedResponse(_UserBase):
    id: int


class UserCreationErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'errors': {
                        'username': ['Minimum username length must be 5', 'Username should consist of ...'],
                        'password': ['Minimum password length must be 8', 'Password should consist of ...'],
                    }
                }
            ]
        }
    )

    errors: dict[str, list[str]]


class TokenCreatedResponse(BaseModel):

    access_token: str
    token_type: str
    expires_in: timedelta | int
    refresh_token: Optional[str] = None
    scope: Optional[list[str]] = None

    @field_validator('expires_in', mode='after')
    @classmethod
    def ensure_seconds(cls, value):
        if isinstance(value, timedelta):
            return value.seconds


class TokensRevokedResponse(BaseModel):
    revoked: list[UUID4]
