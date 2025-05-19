import uuid

import pytest

from currency_exchange.auth.services.jwtservice import JWTIssuer
from .utils import get_token_state_from_db, b64_encode_credentials


pytestmark = pytest.mark.anyio


@pytest.fixture(scope='module')
async def request_url():
    return '/token/revoke'


@pytest.fixture(scope='module')
async def user(users_models):
    return users_models['Mithrandir']


@pytest.fixture(scope="module")
async def token_issuer(get_jwt_issuer_config) -> JWTIssuer:
    return JWTIssuer(**get_jwt_issuer_config())


async def test_revoke_all_users_tokens_success(
        user, request_client, request_url, existing_tokens, db_session, users_raw_passwords
):
    response = await request_client.patch(
        request_url, headers={
            'Authorization': f'Basic {b64_encode_credentials(user.username, users_raw_passwords[user.username])}'
        }
    )

    tokens_states = [await get_token_state_from_db(t.payload['jti'], db_session) for t in existing_tokens['none'].values()] + \
    [await get_token_state_from_db(t.payload['jti'], db_session) for t in existing_tokens['tel'].values()]

    assert response.status_code == 200
    assert all(t.revoked for t in tokens_states)


async def test_revoke_specified_users_tokens_success(
        user, request_client, request_url, existing_tokens, db_session, users_raw_passwords
):
    revoked_tokens_ids = [t.payload['jti'] for t in [existing_tokens['tel']['access'], existing_tokens['none']['access']]]
    untouched_tokens_ids = [t.payload['jti'] for t in [existing_tokens['tel']['refresh'], existing_tokens['none']['refresh']]]
    response = await request_client.patch(
        request_url,
        headers={
            'Authorization': f'Basic {b64_encode_credentials(user.username, users_raw_passwords[user.username])}'
        },
        data={'tokens': revoked_tokens_ids},
    )

    revoked_tokens_states = [await get_token_state_from_db(t_id, db_session) for t_id in revoked_tokens_ids]
    untouched_tokens_states = [await get_token_state_from_db(t_id, db_session) for t_id in untouched_tokens_ids]

    assert response.status_code == 200
    assert all(t.revoked for t in revoked_tokens_states)
    assert all(not t.revoked for t in untouched_tokens_states)


async def test_revoke_tokens_when_user_have_no_active_tokens_success(
        user, request_client, request_url, existing_revoked_refresh_token, db_session, users_raw_passwords
):
    response = await request_client.patch(
        request_url, headers={
            'Authorization': f'Basic {b64_encode_credentials(user.username, users_raw_passwords[user.username])}'
        }
    )

    assert response.status_code == 200


async def test_revoke_tokens_when_user_have_no_specified_tokens_success(
        user, request_client, request_url, db_session, users_raw_passwords
):
    response = await request_client.patch(
        request_url, headers={
            'Authorization': f'Basic {b64_encode_credentials(user.username, users_raw_passwords[user.username])}'
        },
        data={'tokens': [uuid.uuid4(), uuid.uuid4()]},
    )

    assert response.status_code == 200


@pytest.mark.parametrize('username,password', [('Mithrandir', '12345678'), ('Mithrandir'[::-1], '12345678')])
async def test_revoke_tokens_user_password_or_username_is_invalid_error(
        username, password, request_client, request_url, db_session
):
    response = await request_client.patch(
        request_url, headers={'Authorization': f'Basic {b64_encode_credentials(username, password)}'},
        data={'tokens': [uuid.uuid4(), uuid.uuid4()]},
    )

    assert response.status_code == 401


async def test_revoke_tokens_user_is_inactive_error(
        users_models, request_client, request_url, db_session, users_raw_passwords
):
    user = users_models['The_Goblin_King']
    response = await request_client.patch(
        request_url, headers={
            'Authorization': f'Basic {b64_encode_credentials(user.username, users_raw_passwords[user.username])}'
        },
        data={'tokens': [uuid.uuid4(), uuid.uuid4()]},
    )

    assert response.status_code == 403