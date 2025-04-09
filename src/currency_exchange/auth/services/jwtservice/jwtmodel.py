from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, field_validator, model_validator, BeforeValidator
from pydantic_core import PydanticCustomError
from typing_extensions import Optional

from . import JWTAlgorithms
from ... import errors

def ensure_list(value):
    if not isinstance(value, list):
        return [value]
    else:
        return value

class JWTHeaderModel(BaseModel):
    typ: str
    alg: JWTAlgorithms


class JWTClaimsModel(BaseModel):
    iss: str
    sub: str
    exp: datetime
    iat: datetime
    nbf: Optional[datetime] = None
    aud: Optional[str | list[str]] = None
    scope: Annotated[Optional[list[str]], BeforeValidator(ensure_list)] = None
    jti: Optional[str] = None
    device_id: Optional[str] = None

    @field_validator('exp', mode='after')
    @classmethod
    def token_expiry_check(cls, value: datetime) -> datetime:
        if value < datetime.now(tz=timezone.utc):
            raise errors.ExpiredTokenError('Token has expired')
        return value

    @model_validator(mode='after')
    def time_fields_consistency_check(self):
        if self.nbf and self.exp > self.nbf > self.iat:
            return self
        elif self.exp > self.iat:
            return self
        else:
            raise errors.InvalidTokenClaimError(
                'exp > nbf > iat should be true'
            )


class JWTModel(BaseModel):
    header: JWTHeaderModel
    claims: JWTClaimsModel
