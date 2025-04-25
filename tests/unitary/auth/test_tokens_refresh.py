import datetime

import pytest
from joserfc import jwt

from currency_exchange.auth.services.jwtservice import JWTIssuer
from .utils import add_token_state_to_db, get_token_state_from_db, EncodedToken, b64_encode_credentials

pytestmark = pytest.mark.anyio


@pytest.fixture(scope='module')
async def request_url():
    return '/token/refresh'


@pytest.fixture(scope='module')
async def user(users_models):
    return users_models['Mithrandir']


@pytest.fixture(scope="module")
async def token_issuer(get_jwt_issuer_config) -> JWTIssuer:
    return JWTIssuer(**get_jwt_issuer_config())


@pytest.mark.usefixtures('mock_token_issuers_encryption_keys')
async def test_tokens_refresh_successful(
        user, request_client, request_url, existing_tokens, db_session, encryption_key, users_raw_passwords
):
    response = await request_client.post(
        request_url,
        headers={'Authorization': f'Basic {b64_encode_credentials(user.username, users_raw_passwords[user.username])}'},
        data={'grant_type': 'refresh_token', 'refresh_token': existing_tokens['none']['refresh'].str},
    )
    assert response.status_code == 200

    response_date = response.json()

    _existing_tokens = existing_tokens
    existing_tokens = _existing_tokens['none']
    existing_deviced_tokens = _existing_tokens['tel']

    access_token = jwt.decode(response_date['access_token'], encryption_key)
    refresh_token = jwt.decode(response_date['refresh_token'], encryption_key)

    access_token_state = await get_token_state_from_db(access_token.claims['jti'], db_session)
    refresh_token_state = await get_token_state_from_db(refresh_token.claims['jti'], db_session)

    db_session.expire_all()
    revoked_refresh_token_state = await get_token_state_from_db(existing_tokens['refresh'].payload['jti'], db_session)
    revoked_access_token_state = await get_token_state_from_db(existing_tokens['access'].payload['jti'], db_session)

    deviced_refresh_token_state = await get_token_state_from_db(
        existing_deviced_tokens['refresh'].payload['jti'], db_session
    )
    deviced_access_token_state = await get_token_state_from_db(
        existing_deviced_tokens['access'].payload['jti'], db_session
    )

    assert access_token_state is not None
    assert refresh_token_state is not None

    assert revoked_refresh_token_state.revoked is True
    assert revoked_access_token_state.revoked is True

    assert  deviced_access_token_state.revoked is False
    assert deviced_refresh_token_state.revoked is False


async def test_tokens_refresh_invalid_password_error(
        user, request_client, request_url, existing_tokens, users_raw_passwords
):
    response = await request_client.post(
        request_url,
        headers={'Authorization': f'Basic {b64_encode_credentials(user.username, users_raw_passwords[user.username][::-1])}'},
        data={'grant_type': 'refresh_token', 'refresh_token': existing_tokens['none']['refresh'].str},
    )

    assert response.status_code == 401


async def test_tokens_refresh_nonexistent_user_error(
        user, request_client, request_url, existing_tokens, users_raw_passwords
):
    response = await request_client.post(
        request_url,
        headers={
            'Authorization': f'Basic {b64_encode_credentials(user.username[::-1], users_raw_passwords[user.username])}'
        },
        data={'grant_type': 'refresh_token', 'refresh_token': existing_tokens['none']['refresh'].str},
    )

    assert response.status_code == 401


async def test_tokens_refresh_users_doesnt_match_error(
        users_models, request_client, request_url, existing_tokens, users_raw_passwords
):
    user = users_models['Bilbo_baggins']
    response = await request_client.post(
        request_url,
        headers={'Authorization': f'Basic {b64_encode_credentials(user.username, users_raw_passwords[user.username])}'},
        data={'grant_type': 'refresh_token', 'refresh_token': existing_tokens['none']['refresh'].str},
    )

    assert response.status_code == 403


async def test_tokens_refresh_inactive_user_error(
        users_models, request_client, request_url, existing_tokens, users_raw_passwords
):
    user = users_models['The_Goblin_King']
    response = await request_client.post(
        request_url,
        headers={'Authorization': f'Basic {b64_encode_credentials(user.username, users_raw_passwords[user.username])}'},
        data={'grant_type': 'refresh_token', 'refresh_token': existing_tokens['none']['refresh'].str},
    )

    assert response.status_code == 403


async def test_tokens_refresh_revoked_token_error(
        user, request_client, request_url, existing_tokens, existing_revoked_refresh_token,
        db_session, users_raw_passwords
):
    response = await request_client.post(
        request_url,
        headers={'Authorization': f'Basic {b64_encode_credentials(user.username, users_raw_passwords[user.username])}'},
        data={'grant_type': 'refresh_token', 'refresh_token': existing_revoked_refresh_token.str},
    )

    revoked_tokens_states = [
        await get_token_state_from_db(t.payload['jti'], db_session) for t in existing_tokens['none'].values()
    ]

    assert response.status_code == 403

    assert all(ts.revoked for ts in revoked_tokens_states)
