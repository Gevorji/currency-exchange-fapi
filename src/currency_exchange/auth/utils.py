import logging
from typing import Optional, Literal

from fastapi import status, HTTPException

from . import get_token_state_repo, get_users_repo, errors
from .repos import TokenStateRepository, UsersRepository
from .schemas import UserDbOut, TokenStateDbOut, TokenStateDbUpdate, TokenStateDbIn
from .services.jwtservice import JWTModel
from .services.passwordhashing import match_password

logger = logging.getLogger('auth')


async def check_jwt_revocation(jwt: JWTModel) -> bool:
    token_repo: TokenStateRepository = get_token_state_repo()
    token_state = await token_repo.get(jwt.claims.jti)
    logger.debug('Got revoked token. Owner: %s', jwt.claims.sub)
    return token_state.is_revoked


async def get_user_from_sub_jwt_claim(sub: str) -> UserDbOut:
    username = sub.rsplit('.', 1)[-2]
    user_repo = get_users_repo()
    return await user_repo.get(username)


def get_user_id_from_sub_jwt_claim(sub: str) -> int:
    return int(sub.rsplit('.', 1)[-1].lstrip('id'))


async def get_user(username: str) -> UserDbOut:

    user_repo: UsersRepository = get_users_repo()

    try:
        user = await user_repo.get(username)
    except errors.UserDoesNotExistError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return user


async def get_active_user(username: str) -> UserDbOut:
    user = await get_user(username)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is not active')
    return user


def check_password(user: UserDbOut, password: str) -> None:
    if not match_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')


async def revoke_tokens(tokens: list[TokenStateDbOut]):
    token_state_repo = get_token_state_repo()
    for token in tokens:
        update_token = TokenStateDbUpdate.model_validate(token.model_dump())
        update_token.revoked = True
        await token_state_repo.update(update_token)


async def revoke_all_users_tokens_per_device(user: UserDbOut, device_id: str) -> list[TokenStateDbOut]:
    token_state_repo = get_token_state_repo()
    users_tokens = await token_state_repo.get_users_tokens_per_device(user.id, device_id)
    tokens_jtis = [token.claims.jti for token in users_tokens]

    if not users_tokens:
        logger.info('Tokens revocation: user %s has no active tokens for device %s', user.username, device_id)

    await revoke_tokens(users_tokens)
    logger.info('Revoked all user %s tokens for device %s', user.username, device_id)
    return tokens_jtis


async def revoke_users_tokens(user: UserDbOut, jtis: Optional[list[str]] = None) -> list[TokenStateDbOut]:
    token_state_repo = get_token_state_repo()
    if jtis:
        users_tokens = await token_state_repo.get_users_tokens_by_jti(user.id, jtis)
    else:
        users_tokens = await token_state_repo.get_users_tokens(user.id)
    tokens_jtis = [token.claims.jti for token in users_tokens]

    if not users_tokens:
        logger.info('Tokens revocation: user %s has no active tokens', user.username)

    await revoke_tokens(users_tokens)
    if not jtis:
        logger.info('Revoked all user %s tokens', user.username)
    else:
        logger.info('Revoked %s user %s tokens', len(tokens_jtis), user.username)
    return tokens_jtis


async def save_token_state_in_db(token_payload: dict, type_: Literal['access', 'refresh'], user_id: int):
    token_state_repo = get_token_state_repo()
    await token_state_repo.save(
        TokenStateDbIn(
            id=token_payload['jti'], type=type_, user_id=user_id,
            device_id=token_payload['device_id'], expiry_date=token_payload['exp']
        )
    )
