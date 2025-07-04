from typing import Optional


class AuthAppError(Exception): ...


class DataError(AuthAppError): ...


class UserDoesNotExistError(DataError): ...


class UserAlreadyExistsError(DataError): ...


class TokenDoesNotExistError(DataError): ...


class JWTValidationError(AuthAppError):
	def __init__(
		self, msg, payload: Optional[dict] = None, header: Optional[dict] = None
	):
		self.msg = msg
		self.payload = payload
		self.header = header


class ExpiredTokenError(JWTValidationError): ...


class InvalidTokenHeaderError(JWTValidationError): ...


class InvalidTokenClaimError(JWTValidationError): ...


class BadSignatureError(JWTValidationError): ...


class CorruptedTokenDataError(JWTValidationError): ...
