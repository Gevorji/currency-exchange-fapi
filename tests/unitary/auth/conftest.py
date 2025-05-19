import datetime
from datetime import timedelta

from fastapi import FastAPI
import pytest
from joserfc import jwk
from sqlalchemy.ext.asyncio import AsyncSession

from currency_exchange.auth import get_users_repo
from currency_exchange.auth import get_token_state_repo
from currency_exchange.auth.providers import jwt_validator_provider, JWTIssuerProvider
from currency_exchange.auth.routes import clients_router, token_router
from currency_exchange.auth.admin import admin_router
from currency_exchange.auth.services.jwtservice import JWTValidator
from currency_exchange.auth.dbmodels import User, UserCategory, TokenState
from currency_exchange.auth.utils import get_subject_claim_for_user
from currency_exchange.config import auth_settings
from ..auth.utils import EncodedToken, add_token_state_to_db


@pytest.fixture(scope="package")
async def token_validator_dependency_override(encryption_key):
	validator = JWTValidator(key=encryption_key.as_pem(private=False))

	def token_validator_provider():
		return validator

	return token_validator_provider


@pytest.fixture(scope="package")
async def app(token_validator_dependency_override) -> FastAPI:
	app = FastAPI()
	app.include_router(clients_router, prefix="/clients")
	app.include_router(token_router, prefix="/token")
	app.include_router(admin_router)
	app.dependency_overrides = {
		jwt_validator_provider: token_validator_dependency_override
	}
	return app


@pytest.fixture(scope="package")
async def users_raw_passwords(get_random_password):
	return {
		name: get_random_password(length=auth_settings.MIN_PASSWORD_LENGTH)
		for name in ["Gevorji", "Mithrandir", "Bilbo_baggins", "The_Goblin_King"]
	}


@pytest.fixture(scope="package", autouse=True)
async def users_models(db_connection, users_raw_passwords):
	users_models = [
		User(
			username="Gevorji",
			password=users_raw_passwords["Gevorji"],
			category=UserCategory.ADMIN,
		),
		User(
			username="Mithrandir",
			password=users_raw_passwords["Mithrandir"],
			category=UserCategory.MANAGER,
		),
		User(
			username="Bilbo_baggins",
			password=users_raw_passwords["Bilbo_baggins"],
			category=UserCategory.API_CLIENT,
		),
		User(
			username="The_Goblin_King",
			password=users_raw_passwords["The_Goblin_King"],
			category=UserCategory.API_CLIENT,
			is_active=False,
		),
	]

	db_session = AsyncSession(db_connection, expire_on_commit=False)
	async with db_session:
		db_session.add_all(users_models)
		await db_session.commit()

	return {user.username: user for user in users_models}


@pytest.fixture(scope="package")
async def encryption_key():
	return jwk.RSAKey.generate_key()


@pytest.fixture(scope="package")
async def get_jwt_issuer_config(encryption_key):
	def _get_jwt_issuer_config():
		return {
			"key": encryption_key.as_pem(),
			"issuer": "test",
			"access_tkn_duration": timedelta(minutes=1),
			"refresh_tkn_duration": timedelta(minutes=2),
			"assign_jtis": True,
		}

	return _get_jwt_issuer_config


@pytest.fixture(scope="package")
async def token_state_repo():
	return get_token_state_repo()


@pytest.fixture(scope="package")
async def users_repo():
	return get_users_repo()


@pytest.fixture
async def existing_tokens(user, token_issuer, db_session) -> dict[str, EncodedToken]:
	token_iss_args = {
		"subject": get_subject_claim_for_user("testing", user.username, user.id),
		"scope": ["test1", "test2"],
		"private_claims": {"device_id": "none"},
	}
	access_token = EncodedToken(*token_issuer.get_access_token(**token_iss_args))
	refresh_token = EncodedToken(*token_issuer.get_refresh_token(**token_iss_args))
	deviced_token_args = {
		"subject": user.username,
		"scope": ["test1", "test2"],
		"private_claims": {"device_id": "tel"},
	}
	deviced_access_token = EncodedToken(
		*token_issuer.get_access_token(**deviced_token_args)
	)
	deviced_refresh_token = EncodedToken(
		*token_issuer.get_refresh_token(**deviced_token_args)
	)
	for token in [
		access_token,
		refresh_token,
		deviced_access_token,
		deviced_refresh_token,
	]:
		type_ = "access" if token.payload["scope"][0] != "refresh" else "refresh"
		await add_token_state_to_db(
			TokenState(
				id=token.payload["jti"],
				user_id=user.id,
				type=type_,
				device_id=token.payload["device_id"],
				expiry_date=datetime.datetime.fromtimestamp(token.payload["exp"]),
			),
			db_session,
		)

	tokens = {
		token_iss_args["private_claims"]["device_id"]: {
			"access": access_token,
			"refresh": refresh_token,
		},
		deviced_token_args["private_claims"]["device_id"]: {
			"access": deviced_access_token,
			"refresh": deviced_refresh_token,
		},
	}

	return tokens


@pytest.fixture
async def existing_revoked_refresh_token(user, token_issuer, db_session):
	token = EncodedToken(
		*token_issuer.get_refresh_token(
			**{
				"subject": get_subject_claim_for_user(
					"testing", user.username, user.id
				),
				"scope": ["test1", "test2"],
				"private_claims": {"device_id": "none"},
			}
		)
	)
	await add_token_state_to_db(
		TokenState(
			id=token.payload["jti"],
			user_id=user.id,
			type="refresh",
			revoked=True,
			device_id="none",
			expiry_date=datetime.datetime.fromtimestamp(token.payload["exp"]),
		),
		db_session,
	)

	return token


@pytest.fixture
def mock_token_issuers_encryption_keys(monkeypatch, encryption_key):
	for issuer in JWTIssuerProvider._user_category_issuer_map.values():
		monkeypatch.setattr(issuer, "_key", encryption_key)
