from typing import Literal
from enum import IntEnum

from fastapi import APIRouter, Security, status, HTTPException

from . import get_users_repo, get_token_state_repo, errors
from .providers import verify_access
from .schemas import UserDbOut, UserDbUpdate, UserOut
from .services.permissions import UserCategory
from .utils import revoke_users_tokens

admin_router = APIRouter(prefix='/admin', dependencies=[Security(scopes=[verify_access, 'all'])])

users_ops_router = APIRouter(prefix='/users', tags=['users'])

admin_router.include_router(users_ops_router)

users_repo = get_users_repo()
token_state_repo = get_token_state_repo()


additional_openapi_responses_for_users = {
    404: {'description': 'User not found'}
}

user_not_found_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')


class TransitionUsersCategories(IntEnum):
    MANAGER = 0
    API_CLIENT = -1


async def change_user_is_active(user: UserDbOut, is_active: bool, conflict_msg: str) -> UserDbOut:
    if user.category is UserCategory.ADMIN or user.is_active is is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=conflict_msg)
    try:
        await users_repo.update(UserDbUpdate(id=user.user_id, is_active=is_active))
    except errors.UserDoesNotExistError:
        raise user_not_found_exception

    user.is_active = False
    return user


async def change_users_category(
        user_id: int, to: TransitionUsersCategories, direction: Literal['down', 'up']
) -> UserDbOut:
    try:
        promoted_user = await users_repo.get(user_id)
    except errors.UserDoesNotExistError:
        raise user_not_found_exception
    if direction == 'up':
        not_consistent_with_current_state = to < TransitionUsersCategories[promoted_user.category.name]
        msg_409 = 'lower'
    else:
        not_consistent_with_current_state = to > TransitionUsersCategories[promoted_user.category.name]
        msg_409 = 'higher'
    if promoted_user.category == UserCategory.ADMIN:
        raise HTTPException(status.HTTP_409_CONFLICT, detail='User is admin')
    if to == TransitionUsersCategories[promoted_user.category.name]:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=f'User already has category {to.name}')
    if not_consistent_with_current_state:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f'Users current category ({promoted_user.category.name}) is f{msg_409} than given in the request'
        )

    await users_repo.update(UserDbUpdate(id=user_id, category=UserCategory[to.name]))

    promoted_user.category = UserCategory[to.name]
    return promoted_user


@users_ops_router.get(
    '/search', status_code=status.HTTP_200_OK, response_model=UserOut,
    responses={**additional_openapi_responses_for_users}
)
async def get_user(username: str):
    try:
        return await users_repo.get(username)
    except errors.UserDoesNotExistError:
        raise user_not_found_exception


@users_ops_router.get('/all', status_code=status.HTTP_200_OK, response_model=list[UserOut])
async def get_all_users():
    return await users_repo.get_all()


@users_ops_router.patch(
    '{user_id}/deactivate', status_code=status.HTTP_200_OK, response_model=UserOut,
        responses={
            409: {'description': 'User already deactivated or user is admin'},
            **additional_openapi_responses_for_users
        }
)
async def make_user_inactive(user_id: int):
    user = await users_repo.get(user_id)
    await revoke_users_tokens(user)
    return await change_user_is_active(user, is_active=False, conflict_msg='User is admin or deactivated already')


@users_ops_router.patch(
    '{user_id}/activate}', status_code=status.HTTP_200_OK, response_model=UserOut,
    responses={
        409: {'description': 'User is already active or user is admin'},
        **additional_openapi_responses_for_users
    }
)
async def make_user_active(user_id: int):
    user = await users_repo.get(user_id)
    return await change_user_is_active(user, is_active=True, conflict_msg='User is admin or is active already')


@users_ops_router.patch(
    '/{user_id}/category/promote', status_code=status.HTTP_200_OK, response_model=UserOut,
    responses={
        409: {'description': 'Performed update conflicts with current state of user category'},
        **additional_openapi_responses_for_users
    }
)
async def promote_users_category(user_id: int, to: TransitionUsersCategories):
    return await change_users_category(user_id, to, direction='up')


@users_ops_router.patch(
    '/{user_id}/downgrade', status_code=status.HTTP_200_OK, response_model=UserOut,
    responses={
        409: {'description': 'Performed update conflicts with current state of user category'},
        **additional_openapi_responses_for_users
    }
)
async def downgrade_users_category(user_id: int, to: TransitionUsersCategories):
    return await change_users_category(user_id, to, direction='down')
