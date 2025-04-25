import pytest
from fastapi import HTTPException

from currency_exchange.auth.dbmodels import User
from currency_exchange.auth.providers import get_active_user


pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
async def inactive_user(users_models) -> User:
    return users_models['The_Goblin_King']


@pytest.fixture(scope="module")
async def active_user(users_models) -> User:
    return users_models['Bilbo_baggins']


async def test_get_active_user_success(active_user: User):
    user = await get_active_user(active_user.username)
    assert user.id == active_user.id


async def test_get_active_user_error_on_inactive_user(inactive_user: User):
    with pytest.raises(HTTPException):
        await get_active_user(inactive_user.username)


async def test_get_active_user_error_on_nonexistent_user(active_user: User):
    with pytest.raises(HTTPException):
        await get_active_user(active_user.username[::-1])




