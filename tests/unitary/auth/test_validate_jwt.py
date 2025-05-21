import datetime
import string
import uuid
from functools import partial
from math import ceil
import random

import pytest
from joserfc import jwt

from currency_exchange.auth.providers import validate_jwt
from currency_exchange.auth.services.jwtservice import JWTValidator
from currency_exchange.auth import errors
from .utils import EncodedToken

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
async def jwt_validator_revocation_stub(encryption_key):
	return partial(
		validate_jwt,
		token_validator=JWTValidator(key=encryption_key.as_pem(private=False)),
		revocation_checker=lambda: False,
	)


@pytest.fixture(scope="module")
async def jwt_validator(encryption_key) -> JWTValidator:
	return JWTValidator(key=encryption_key.as_pem(private=False))


@pytest.fixture
async def get_mock_token(encryption_key):
	def _get_mock_token(**kwargs) -> EncodedToken:
		header = {"typ": "JWT", "alg": "RS256"}
		payload = {"sub": "Smeagol", "iss": "tester", "jti": uuid.uuid4().hex}
		payload.update(kwargs)
		for key in ["iat", "exp", "nbf"]:
			value = payload.get(key)
			if value is not None and isinstance(value, datetime.datetime):
				payload[key] = ceil(value.timestamp())
		return EncodedToken(
			str=jwt.encode(header, payload, encryption_key),
			payload=payload,
			header=header,
		)

	return _get_mock_token


@pytest.fixture
async def mock_token_base() -> tuple[dict, dict]:
	header = {"typ": "JWT", "alg": "HS256"}
	payload = {"sub": "Smeagol", "iss": "tester", "jti": uuid.uuid4().hex}

	return header, payload


def randomize_char(_string: str) -> str:
	idx = random.randint(0, len(_string) - 1)
	_string = (
		_string[:idx]
		+ random.choice(string.ascii_letters + string.digits)
		+ _string[idx + 1 :]
	)
	return _string


@pytest.mark.parametrize(
	"iat,nbf,exp",
	[
		(
			now := datetime.datetime.now(),
			now + datetime.timedelta(minutes=1),
			now + datetime.timedelta(minutes=5),
		),
		(now, None, now + datetime.timedelta(minutes=5)),
	],
)
async def test_validate_jwt_success(iat, nbf, exp, get_mock_token, jwt_validator):
	token = get_mock_token(iat=iat, nbf=nbf, exp=exp)

	validated_token = jwt_validator.token_validate(token.str)

	token_claims = validated_token.claims
	if nbf:
		assert token_claims.nbf.timestamp() == token.payload["nbf"]
	assert token_claims.iat.timestamp() == token.payload["iat"]
	assert token_claims.exp.timestamp() == token.payload["exp"]
	assert token_claims.jti == token.payload["jti"]


@pytest.mark.parametrize(
	"iat,nbf,exp",
	[
		(
			base := datetime.datetime.now(tz=datetime.timezone.utc)
			- datetime.timedelta(minutes=5),
			base - datetime.timedelta(minutes=4),
			datetime.datetime.now() - datetime.timedelta(seconds=10),
		),
		(
			base,
			base + datetime.timedelta(minutes=1),
			datetime.datetime.now() - datetime.timedelta(seconds=10),
		),
		(base, None, datetime.datetime.now() - datetime.timedelta(seconds=10)),
	],
)
async def test_validate_jwt_expired_token_failure(
	iat, nbf, exp, get_mock_token, jwt_validator
):
	token = get_mock_token(iat=iat, nbf=nbf, exp=exp)

	with pytest.raises(errors.ExpiredTokenError):
		jwt_validator.token_validate(token.str)


@pytest.mark.parametrize(
	"iat,nbf,exp",
	[
		(
			base := datetime.datetime.now(tz=datetime.timezone.utc),
			base + datetime.timedelta(minutes=1),
			base + datetime.timedelta(minutes=1),
		),
		(
			base,
			base + datetime.timedelta(minutes=6),
			base + datetime.timedelta(minutes=2),
		),
		(base + datetime.timedelta(minutes=1), None, base),
	],
)
async def test_validate_jwt_inconsistent_iat_exp_failure(
	iat, nbf, exp, get_mock_token, jwt_validator
):
	token = get_mock_token(iat=iat, nbf=nbf, exp=exp)

	with pytest.raises(errors.InvalidTokenClaimError):
		jwt_validator.token_validate(token.str)


async def test_validate_jwt_invalid_signature_failure(get_mock_token, jwt_validator):
	now = datetime.datetime.now()
	token = get_mock_token(
		iat=now,
		nbf=now + datetime.timedelta(minutes=1),
		exp=now + datetime.timedelta(minutes=5),
	)
	token_header_str, token_payload_str, token_signature_str = token.str.split(".")
	corrupted_tokens = [
		token_header_str
		+ "."
		+ randomize_char(token_payload_str)
		+ "."
		+ token_signature_str,
		token_header_str
		+ "."
		+ token_payload_str
		+ "."
		+ randomize_char(token_signature_str),
	]

	for corrupted_token in corrupted_tokens:
		with pytest.raises(errors.BadSignatureError):
			jwt_validator.token_validate(corrupted_token)


@pytest.mark.parametrize(
	"token",
	[
		"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
		"eyJzdWIiOiIxMjM0NTY3ODkwIiwi[]FtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
		"SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
		"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
		"SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
	],
)
async def test_validate_jwt_invalid_token_format_failure(token, jwt_validator):
	with pytest.raises(errors.CorruptedTokenDataError):
		jwt_validator.token_validate(token)
