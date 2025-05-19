import pytest
from fastapi import FastAPI, APIRouter
from fastapi import Security
import httpx
from httpx import AsyncClient

from currency_exchange.auth.schemas import TokenStateDbIn
from currency_exchange.auth.services.jwtservice import JWTIssuer
from currency_exchange.auth.providers import (
	verify_access,
	jwt_validator_provider,
	jwt_revocation_checker_provider,
)

pytestmark = pytest.mark.anyio


test_router = APIRouter()


REQUIRED_ACCESS_SCOPES = ["elf", "human", "middle_earth"]


@test_router.get(
	"/guarded_endpoint",
	dependencies=[Security(verify_access, scopes=REQUIRED_ACCESS_SCOPES)],
)
def get_guarded_endpoint():
	return {"message": "You have got a guarded resource!"}


@pytest.fixture(scope="module")
async def token_issuer(get_jwt_issuer_config) -> JWTIssuer:
	return JWTIssuer(**get_jwt_issuer_config())


@pytest.fixture(scope="module")
async def revocation_checker_dependency_override():
	def revocation_checker_provider():
		async def _check_revocation(*args, **kwargs):
			return False

		return _check_revocation

	return revocation_checker_provider


@pytest.fixture
async def app(
	token_validator_dependency_override, revocation_checker_dependency_override
):
	_app = FastAPI()
	_app.include_router(test_router)
	_app.dependency_overrides = {
		jwt_validator_provider: token_validator_dependency_override,
		jwt_revocation_checker_provider: revocation_checker_dependency_override,
	}
	return _app


@pytest.mark.parametrize(
	"scopes",
	[
		["elf", "human", "middle_earth", "fish_recipie_defender"],
		["elf", "human", "middle_earth"],
		["all"],
	],
)
async def test_verify_access_success(token_issuer, request_client: AsyncClient, scopes):
	access_token = token_issuer.get_access_token(subject="Smeagol", scope=scopes)[0]

	response = await request_client.get(
		"/guarded_endpoint", headers={"Authorization": f"Bearer {access_token}"}
	)
	assert response.status_code == 200


@pytest.mark.parametrize("scopes", [["elf", "human"], ["elf"]])
async def test_verify_access_error_when_token_does_not_have_required_scopes(
	token_issuer, request_client: AsyncClient, scopes
):
	access_token = token_issuer.get_access_token(subject="Smeagol", scope=scopes)[0]

	response = await request_client.get(
		"/guarded_endpoint", headers={"Authorization": f"Bearer {access_token}"}
	)
	with pytest.raises(httpx.HTTPStatusError):
		response.raise_for_status()


async def test_verify_access_error_when_token_is_refresh(
	token_issuer, request_client: AsyncClient
):
	token = token_issuer.get_refresh_token(
		subject="Smeagol", scope=["elf", "human", "middle_earth"]
	)[0]

	response = await request_client.get(
		"/guarded_endpoint", headers={"Authorization": f"Bearer {token}"}
	)
	with pytest.raises(httpx.HTTPStatusError):
		response.raise_for_status()


async def test_verify_access_error_when_token_revoked(
	token_issuer, request_client: AsyncClient, app, token_state_repo, users_models
):
	access_token, _, payload = token_issuer.get_access_token(
		subject="Smeagol", scope=REQUIRED_ACCESS_SCOPES
	)
	del app.dependency_overrides[jwt_revocation_checker_provider]

	await token_state_repo.save(
		TokenStateDbIn(
			id=payload["jti"],
			type="access",
			device_id="none",
			expiry_date=payload["exp"],
			revoked=True,
			user_id=users_models["Bilbo_baggins"].id,
		)
	)

	response = await request_client.get(
		"/guarded_endpoint", headers={"Authorization": f"Bearer {access_token}"}
	)

	with pytest.raises(httpx.HTTPStatusError):
		response.raise_for_status()
	assert "revoked" in response.text.lower()


async def test_verify_access_error_when_token_has_no_token_state_in_db(
	token_issuer, request_client: AsyncClient, app
):
	access_token, _, payload = token_issuer.get_access_token(
		subject="Smeagol", scope=REQUIRED_ACCESS_SCOPES
	)
	del app.dependency_overrides[jwt_revocation_checker_provider]

	response = await request_client.get(
		"/guarded_endpoint", headers={"Authorization": f"Bearer {access_token}"}
	)

	with pytest.raises(httpx.HTTPStatusError):
		response.raise_for_status()
	assert "unrecognized" in response.text.lower()
