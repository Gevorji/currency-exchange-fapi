import uuid
import datetime

import pytest
from joserfc import jwt

from currency_exchange.auth.dbmodels import TokenState
from .utils import add_token_state_to_db, get_token_state_from_db

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
async def request_url():
	return "/token/gain"


@pytest.fixture(scope="module")
async def user(users_models):
	return users_models["Bilbo_baggins"]


@pytest.mark.usefixtures("mock_token_issuers_encryption_keys")
async def test_token_granting_successful(
	request_url, user, request_client, users_raw_passwords, encryption_key, db_session
):
	existing_refresh_token = TokenState(
		id=uuid.uuid4(),
		user_id=user.id,
		type="refresh",
		device_id="none",
		expiry_date=datetime.datetime.now() + datetime.timedelta(days=10),
	)
	existing_access_token = TokenState(
		id=uuid.uuid4(),
		user_id=user.id,
		type="access",
		device_id="none",
		expiry_date=datetime.datetime.now() + datetime.timedelta(minutes=15),
	)
	await add_token_state_to_db(existing_refresh_token, db_session)
	await add_token_state_to_db(existing_access_token, db_session)

	response = await request_client.post(
		request_url,
		data={
			"username": user.username,
			"password": users_raw_passwords[user.username],
		},
	)
	assert response.status_code == 200

	response_data = response.json()

	access_token = jwt.decode(response_data["access_token"], key=encryption_key)
	refresh_token = jwt.decode(response_data["refresh_token"], key=encryption_key)

	access_token_state = await get_token_state_from_db(
		access_token.claims["jti"], db_session
	)
	refresh_token_state = await get_token_state_from_db(
		refresh_token.claims["jti"], db_session
	)

	assert access_token_state is not None
	assert refresh_token_state is not None

	await db_session.refresh(existing_access_token)
	await db_session.refresh(existing_refresh_token)
	assert existing_access_token.revoked is True
	assert existing_refresh_token.revoked is True

	assert access_token_state.user_id == user.id
	assert refresh_token_state.user_id == user.id

	assert access_token_state.expiry_date.timestamp() == access_token.claims["exp"]
	assert refresh_token_state.expiry_date.timestamp() == refresh_token.claims["exp"]


async def test_token_granting_invalid_password_failure(
	request_url, user, request_client, users_raw_passwords
):
	response = await request_client.post(
		request_url,
		data={
			"username": user.username,
			"password": users_raw_passwords[user.username][::-1],
		},
	)
	assert response.status_code == 401


async def test_token_granting_nonexistent_user_failure(
	request_url, user, request_client, users_raw_passwords
):
	response = await request_client.post(
		request_url,
		data={
			"username": user.username[::-1],
			"password": users_raw_passwords[user.username],
		},
	)
	assert response.status_code == 401


async def test_token_granting_inactive_user_failure(
	request_url, users_models, request_client, users_raw_passwords
):
	user = users_models["The_Goblin_King"]
	response = await request_client.post(
		request_url,
		data={
			"username": user.username,
			"password": users_raw_passwords[user.username],
		},
	)
	assert response.status_code == 403
