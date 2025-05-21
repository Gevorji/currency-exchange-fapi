import datetime

import pytest
from sqlalchemy import func, select

from currency_exchange.auth.dbmodels import User, TokenState
from currency_exchange.auth.services.permissions import UserCategory
from currency_exchange.auth.services.jwtservice import JWTIssuer
from currency_exchange.auth.providers import JWTIssuerProvider
from currency_exchange.auth.schemas import UserDbOut
from .utils import (
	EncodedToken,
	get_user_from_db,
	add_token_state_to_db,
	get_token_state_from_db,
)

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
async def admin_user(users_models) -> User:
	return users_models["Gevorji"]


@pytest.fixture(scope="module")
async def user(users_models) -> User:
	return users_models["Bilbo_baggins"]


@pytest.fixture(scope="module")
async def admin_token_issuer(get_jwt_issuer_config, admin_user):
	return JWTIssuerProvider(UserDbOut.model_validate(admin_user), device_id="none")


@pytest.fixture(scope="module")
async def token_issuer(get_jwt_issuer_config):
	return JWTIssuer(**get_jwt_issuer_config())


@pytest.fixture
async def admin_access_token(
	admin_token_issuer, admin_user, db_session, mock_token_issuers_encryption_keys
):
	token = EncodedToken(*admin_token_issuer.get_access_token(scope=["all"]))
	await add_token_state_to_db(
		TokenState(
			id=token.payload["jti"],
			user_id=admin_user.id,
			type="access",
			device_id="none",
			expiry_date=datetime.datetime.fromtimestamp(token.payload["exp"]),
		),
		db_session,
	)
	return token


@pytest.fixture
async def usual_access_token(admin_token_issuer, users_models, db_session):
	user = users_models["Bilbo_baggins"]
	token = EncodedToken(*admin_token_issuer.get_access_token(scope=["test"]))
	await add_token_state_to_db(
		TokenState(
			id=token.payload["jti"],
			user_id=user.id,
			type="access",
			device_id="none",
			expiry_date=datetime.datetime.fromtimestamp(token.payload["exp"]),
		),
		db_session,
	)
	return token


@pytest.mark.parametrize(
	"request_url,method,expected_status_code", [("/admin/users/all", "get", 200)]
)
async def test_admin_resource_access_success(
	request_url, request_client, method, admin_access_token, expected_status_code
):
	method_func = getattr(request_client, method)
	response = await method_func(
		request_url, headers={"Authorization": f"Bearer {admin_access_token.str}"}
	)

	assert response.status_code == expected_status_code


@pytest.mark.usefixtures("mock_token_issuers_encryption_keys")
@pytest.mark.parametrize("request_url,method", [("/admin/users/all", "get")])
async def test_admin_resource_access_error(
	request_url, request_client, method, usual_access_token
):
	method_func = getattr(request_client, method)
	response = await method_func(
		request_url, headers={"Authorization": f"Bearer {usual_access_token.str}"}
	)

	assert response.status_code == 403


async def test_admin_get_all_users_success(
	admin_access_token, request_client, db_session
):
	response = await request_client.get(
		"/admin/users/all",
		headers={"Authorization": f"Bearer {admin_access_token.str}"},
	)

	assert response.status_code == 200

	response_data = response.json()

	number_of_users_in_db = await db_session.execute(
		select(func.count()).select_from(User)
	)
	number_of_users_in_db = number_of_users_in_db.scalar_one()
	assert len(response_data) == number_of_users_in_db


async def test_get_one_user_success(admin_access_token, request_client, users_models):
	user = users_models["Bilbo_baggins"]
	response = await request_client.get(
		"/admin/users/search",
		headers={"Authorization": f"Bearer {admin_access_token.str}"},
		params={"username": user.username},
	)

	assert response.status_code == 200

	response_data = response.json()

	assert response_data["username"] == user.username
	assert response_data["id"] == user.id


async def test_get_one_user_user_not_found_error(
	admin_access_token, request_client, users_models
):
	user = users_models["Bilbo_baggins"]
	response = await request_client.get(
		"/admin/users/search",
		headers={"Authorization": f"Bearer {admin_access_token.str}"},
		params={"username": user.username[::-1]},
	)

	assert response.status_code == 404


class TestPromoteUsersCategory:
	@pytest.fixture
	def get_request_url(self):
		def _get_request_url(user_id: str):
			return f"/admin/users/{user_id}/category/promote"

		return _get_request_url

	async def test_promote_users_category_success(
		self,
		admin_access_token,
		request_client,
		users_models,
		get_request_url,
		db_session,
	):
		user = users_models["Bilbo_baggins"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
			params={"to": "0"},
		)
		assert response.status_code == 200

		user_from_db = await get_user_from_db(user.id, db_session)

		assert user_from_db.category == UserCategory.MANAGER

	async def test_promote_users_category_user_is_admin_error(
		self,
		admin_access_token,
		request_client,
		users_models,
		get_request_url,
		db_session,
	):
		user = users_models["Gevorji"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
			params={"to": "0"},
		)
		assert response.status_code == 409

		user_from_db = await get_user_from_db(user.id, db_session)

		assert user_from_db.category == user.category

	async def test_promote_users_category_from_higher_to_lower_category_error(
		self,
		admin_access_token,
		request_client,
		users_models,
		get_request_url,
		db_session,
	):
		user = users_models["Mithrandir"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
			params={"to": "-1"},
		)
		assert response.status_code == 409

		user_from_db = await get_user_from_db(user.id, db_session)

		assert user_from_db.category == user.category

	async def test_promote_users_category_same_category_specified_error(
		self,
		admin_access_token,
		request_client,
		users_models,
		get_request_url,
		db_session,
	):
		user = users_models["Mithrandir"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
			params={"to": "0"},
		)
		assert response.status_code == 409

		user_from_db = await get_user_from_db(user.id, db_session)

		assert user_from_db.category == user.category

	async def test_promote_users_category_user_not_found_error(
		self, admin_access_token, request_client, users_models, get_request_url
	):
		user = users_models["Bilbo_baggins"]
		response = await request_client.patch(
			get_request_url(user.id * 1000),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
			params={"to": "0"},
		)
		assert response.status_code == 404


class TestDowngradeUsersCategory:
	@pytest.fixture
	def get_request_url(self):
		def _get_request_url(user_id: str):
			return f"/admin/users/{user_id}/category/downgrade"

		return _get_request_url

	async def test_downgrade_users_category_success(
		self,
		admin_access_token,
		request_client,
		users_models,
		get_request_url,
		db_session,
	):
		user = users_models["Mithrandir"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
			params={"to": "-1"},
		)
		assert response.status_code == 200

		user_from_db = await get_user_from_db(user.id, db_session)

		assert user_from_db.category == UserCategory.API_CLIENT

	async def test_downgrade_users_category_user_is_admin_error(
		self,
		admin_access_token,
		request_client,
		users_models,
		get_request_url,
		db_session,
	):
		user = users_models["Gevorji"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
			params={"to": "0"},
		)
		assert response.status_code == 409

		user_from_db = await get_user_from_db(user.id, db_session)

		assert user_from_db.category == user.category

	async def test_downgrade_users_category_from_higher_to_lower_category_error(
		self,
		admin_access_token,
		request_client,
		users_models,
		get_request_url,
		db_session,
	):
		user = users_models["Bilbo_baggins"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
			params={"to": "0"},
		)
		assert response.status_code == 409

		user_from_db = await get_user_from_db(user.id, db_session)

		assert user_from_db.category == user.category

	async def test_downgrade_users_category_same_category_specified_error(
		self,
		admin_access_token,
		request_client,
		users_models,
		get_request_url,
		db_session,
	):
		user = users_models["Mithrandir"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
			params={"to": "0"},
		)
		assert response.status_code == 409

		user_from_db = await get_user_from_db(user.id, db_session)

		assert user_from_db.category == user.category

	async def test_downgrade_users_category_user_not_found_error(
		self, admin_access_token, request_client, users_models, get_request_url
	):
		user = users_models["Bilbo_baggins"]
		response = await request_client.patch(
			get_request_url(user.id * 1000),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
			params={"to": "0"},
		)
		assert response.status_code == 404


class TestDeactivateUser:
	@pytest.fixture
	def get_request_url(self):
		def _get_request_url(user_id: str):
			return f"/admin/users/{user_id}/deactivate"

		return _get_request_url

	async def test_deactivate_user_success(
		self,
		user,
		request_client,
		admin_access_token,
		existing_tokens,
		db_session,
		get_request_url,
	):
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
		)

		assert response.status_code == 200
		user_from_db = await get_user_from_db(user.id, db_session)
		assert user_from_db.is_active is False

		tokens = [token for token in existing_tokens["none"].values()] + [
			token for token in existing_tokens["tel"].values()
		]
		token_states = [
			await get_token_state_from_db(token.payload["jti"], db_session)
			for token in tokens
		]

		assert all(token_state.revoked is True for token_state in token_states)

	async def test_deactivate_user_user_is_already_deactivated_error(
		self, users_models, request_client, admin_access_token, get_request_url
	):
		user = users_models["The_Goblin_King"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
		)

		assert response.status_code == 409

	async def test_deactivate_user_user_not_found_error(
		self, user, request_client, admin_access_token, get_request_url
	):
		response = await request_client.patch(
			get_request_url(user.id * 1000),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
		)

		assert response.status_code == 404

	async def test_deactivate_user_user_is_admin_error(
		self, admin_user, request_client, admin_access_token, get_request_url
	):
		response = await request_client.patch(
			get_request_url(admin_user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
		)

		assert response.status_code == 409


class TestActivateUser:
	@pytest.fixture
	def get_request_url(self):
		def _get_request_url(user_id: str):
			return f"/admin/users/{user_id}/activate"

		return _get_request_url

	async def test_activate_user_success(
		self,
		users_models,
		request_client,
		admin_access_token,
		db_session,
		get_request_url,
	):
		user = users_models["The_Goblin_King"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
		)

		assert response.status_code == 200
		user_from_db = await get_user_from_db(user.id, db_session)
		assert user_from_db.is_active is True

	async def test_activate_user_user_is_already_active_error(
		self, users_models, request_client, admin_access_token, get_request_url
	):
		user = users_models["Bilbo_baggins"]
		response = await request_client.patch(
			get_request_url(user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
		)

		assert response.status_code == 409

	async def test_activate_user_user_not_found_error(
		self, user, request_client, admin_access_token, get_request_url
	):
		response = await request_client.patch(
			get_request_url(user.id * 1000),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
		)

		assert response.status_code == 404

	async def test_activate_user_user_is_admin_error(
		self, admin_user, request_client, admin_access_token, get_request_url
	):
		response = await request_client.patch(
			get_request_url(admin_user.id),
			headers={"Authorization": f"Bearer {admin_access_token.str}"},
		)

		assert response.status_code == 409
