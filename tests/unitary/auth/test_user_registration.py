import pytest
from sqlalchemy import select

from currency_exchange.config import auth_settings
from currency_exchange.auth.dbmodels import User
from .utils import count_users_in_db

pytestmark = pytest.mark.anyio


async def user_exists_in_db(username: str, session):
	res = await session.execute(select(User).where(User.username == username))
	user = res.scalar_one_or_none()
	return user is not None


async def test_user_registration_success(
	request_client, get_random_password, db_session
):
	pswd = get_random_password(auth_settings.MIN_PASSWORD_LENGTH)
	username = "malcolm_smith"
	response = await request_client.post(
		"/clients/register",
		data={"username": username, "password1": pswd, "password2": pswd},
	)

	assert response.status_code == 201

	assert await user_exists_in_db(username, db_session)


async def test_user_registration_passwords_unequal_error(
	request_client, get_random_password, db_session
):
	pswd = get_random_password(auth_settings.MIN_PASSWORD_LENGTH)
	username = "malcolm_smith"
	response = await request_client.post(
		"/clients/register",
		data={"username": username, "password1": pswd, "password2": pswd[::-1]},
	)

	assert response.status_code == 400

	assert not await user_exists_in_db(username, db_session)


@pytest.mark.parametrize("username", ["g", "", "?", "@", ";drop database users;", "<"])
async def test_user_registration_username_is_invalid_error(
	username, request_client, get_random_password, db_session
):
	pswd = get_random_password(auth_settings.MIN_PASSWORD_LENGTH)
	response = await request_client.post(
		"/clients/register",
		data={"username": username, "password1": pswd, "password2": pswd},
	)

	assert response.status_code == 400

	assert not await user_exists_in_db(username, db_session)


@pytest.mark.parametrize(
	"password",
	[
		"a" * (auth_settings.MIN_PASSWORD_LENGTH - 1),
		"a" * (auth_settings.MIN_PASSWORD_LENGTH - 1) + " ",
		"a" * (auth_settings.MIN_PASSWORD_LENGTH - 1) + "\t",
		"a" * (auth_settings.MIN_PASSWORD_LENGTH - 1) + "\n",
	],
)
async def test_user_registration_password_is_invalid_error(
	password, request_client, db_session
):
	username = "Banksy"
	response = await request_client.post(
		"/clients/register",
		data={"username": username, "password1": password, "password2": password},
	)

	assert response.status_code == 400

	assert not await user_exists_in_db(username, db_session)


async def test_user_registration_user_exists_error(
	request_client, get_random_password, db_session
):
	pswd = get_random_password(auth_settings.MIN_PASSWORD_LENGTH)
	username = "Mithrandir"
	response = await request_client.post(
		"/clients/register",
		data={"username": username, "password1": pswd, "password2": pswd},
	)

	assert response.status_code == 409

	users_number = await count_users_in_db(username, db_session)
	assert users_number == 1
