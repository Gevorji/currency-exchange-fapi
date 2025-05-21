from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, model_validator, BeforeValidator, PrivateAttr
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
	_validation_tstamp: datetime = (
		PrivateAttr()
	)  # time when validation is said to be started
	iss: str
	sub: str
	exp: datetime
	iat: datetime
	nbf: Optional[datetime] = None
	aud: Optional[str | list[str]] = None
	scope: Annotated[Optional[list[str]], BeforeValidator(ensure_list)] = None
	jti: Optional[str] = None
	device_id: Optional[str] = None

	@model_validator(mode="after")
	def issue_time_check(self):
		if self.validation_tstamp.timestamp() - self.iat.timestamp() > -1:
			return self
		raise errors.InvalidTokenClaimError("iat < current_time+1sec  should be true")

	@model_validator(mode="after")
	def token_expiry_check(self):
		if self.exp < self.validation_tstamp:
			raise errors.ExpiredTokenError("Token has expired")
		return self

	@model_validator(mode="after")
	def time_fields_consistency_check(self):
		if self.nbf and self.exp > self.nbf > self.iat:
			return self
		elif not self.nbf and self.exp > self.iat:
			return self
		else:
			raise errors.InvalidTokenClaimError("exp > nbf > iat should be true")

	@property
	def validation_tstamp(self):
		if getattr(self, "_validation_tstamp", None) is None:
			self._validation_tstamp = datetime.now(tz=timezone.utc)
		return self._validation_tstamp


class JWTModel(BaseModel):
	header: JWTHeaderModel
	claims: JWTClaimsModel
