from collections.abc import Awaitable
from typing import Annotated, Callable, Optional
import logging

from fastapi import Depends, HTTPException, status, Form
from fastapi.security import (
    SecurityScopes, OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials, OAuth2PasswordRequestForm
)
from starlette.requests import Request

from jwt_sandbox import token
from . import get_users_repo, get_token_state_repo
from .repos import TokenStateRepository, UsersRepository
from .routes import TOKEN_URL
from .schemas import UserDbOut, TokenStateDbUpdate, TokenStateDbOut
from .services.permissions import scopes_registry, UserCategory
from .services.jwtservice import JWTValidator, JWTModel, JWTIssuer
from .services.passwordhashing import match_password
from . import errors
from currency_exchange.config import auth_settings

logger = logging.getLogger('auth')

RevocationCheckerType = Callable[[JWTModel], Awaitable[bool]]

ouath2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL, auto_error=False)

http_basic_auth_scheme = HTTPBasic(realm='Api users')


class JWTValidatorProvider:
    _validator: JWTValidator

    def __init__(self, validator: JWTValidator):
        self._validator = validator

    def __call__(self):
        return self._validator

    def set_validator(self, validator: JWTValidator):
        self._validator = validator


class JWTRevocationCheckerProvider:

    _checker: RevocationCheckerType

    def __init__(self, checker: RevocationCheckerType):
        self._checker = checker

    def __call__(self):
        return self._checker

    def set_checker(self, checker: RevocationCheckerType):
        self._checker = checker


async def check_jwt_revocation(jwt: JWTModel) -> bool:
    token_repo: TokenStateRepository = get_token_state_repo()
    token_state = await token_repo.get(jwt.claims.jti)
    logger.debug('Got revoked token. Owner: %s', jwt.claims.sub)
    return token_state.is_revoked


jwt_validator_provider = JWTValidatorProvider(JWTValidator.from_config(auth_settings))
jwt_revocation_checker_provider = JWTRevocationCheckerProvider(check_jwt_revocation)


async def get_user_from_sub_jwt_claim(sub: str) -> UserDbOut:
    username = sub.rsplit('.', 1)[-2]
    user_repo = get_users_repo()
    return await user_repo.get(username)


def get_user_id_from_sub_jwt_claim(sub: str) -> int:
    return int(sub.rsplit('.', 1)[-1].lstrip('id'))


async def validate_jwt(
        token_str: Annotated[str, Depends(ouath2_scheme)],
        token_validator: Annotated[JWTValidator, Depends(jwt_validator_provider)],
        revocation_checker: Annotated[RevocationCheckerType, Depends(jwt_revocation_checker_provider)],
) -> JWTModel:
    exc_args = {
            'status_code': status.HTTP_401_UNAUTHORIZED,
            'headers': {'WWW-Authenticate': 'Bearer'}
    }

    try:
        try:
            token = token_validator.token_validate(token_str)
            logger.debug('Token validated. Owner: %s', token.claims.sub)
        except errors.JWTValidationError as e:
            logger.debug(
                'Token validation problem. Token header: %s. Token payload: %s',
                e.header, e.payload, exc_info=True
            )
            raise
    except errors.BadSignatureError as e:
        raise HTTPException(detail='Bad token signature', **exc_args) from e
    except errors.InvalidTokenClaimError as e:
        raise HTTPException(detail='Invalid token', **exc_args) from e
    except errors.ExpiredTokenError as e:
        raise HTTPException(detail='Expired token', **exc_args) from e
    try:
        revoked = revocation_checker(token)
        if revoked:
            raise HTTPException(detail='Revoked token', **exc_args)
    except errors.TokenDoesNotExistError as e:
        logger.debug('Unrecognized token. Token id: %s', token.claims.jti)
        raise HTTPException(detail='Unrecognized token', **exc_args) from e

    return token


async def verify_access(scopes: SecurityScopes, token: Annotated[JWTModel, Depends(validate_jwt)], request: Request):
    forbidden_exc_args = {
        'status_code': status.HTTP_403_FORBIDDEN,
        'headers': {'WWW-Authenticate': f'scopes={scopes.scope_str}'}
    }

    logger.debug(
        'Access attempt. Resource: %s. Token owner: %s. Token scopes: %s. Required scopes: %s',
        request.url, token.claims.sub, ', '.join(scope for scope in token.claims.scope), scopes.scope_str
    )

    if 'all' in token.claims.scopes:
        return

    if not set(scopes.scopes).issubset(token.claims.scopes):
        logger.debug('Access denied.')
        raise HTTPException(detail='Access denied', **forbidden_exc_args)


async def get_user(username: str, password: str) -> UserDbOut:

    user_repo: UsersRepository = get_users_repo()

    user = await user_repo.get(username)

    if not match_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')
    return user


async def get_active_user(username: str, password: str) -> UserDbOut:
    user = await get_user(username, password)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is not active')
    return user


async def get_user_ouath(ouath_form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> UserDbOut:
    return await get_user(ouath_form_data.username, ouath_form_data.password)


async def get_active_user_oauth(ouath_form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> UserDbOut:
    return await get_active_user(ouath_form_data.username, ouath_form_data.password)


async def get_user_http_basic_auth(
        user_credentials: Annotated[HTTPBasicCredentials, Depends(http_basic_auth_scheme)]
) -> UserDbOut:
    return await get_active_user(user_credentials.username, user_credentials.password)


async def get_active_user_http_basic_auth(
        user_credentials: Annotated[HTTPBasicCredentials, Depends(http_basic_auth_scheme)]
) -> UserDbOut:
    return await get_active_user(user_credentials.username, user_credentials.password)


async def get_user_from_bearer_token(bearer_token: Annotated[JWTModel, Depends(validate_jwt)]) -> UserDbOut:
    return await get_user_from_sub_jwt_claim(bearer_token.claims.sub)


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


class JWTIssuerProvider:
    _audience = ['currency_exchange_api']
    _issuer = 'gevorji.currency_exchange_api'
    _subject_prefix = _issuer
    _user_category_issuer_map = {
        UserCategory.API_CLIENT: JWTIssuer.from_config(
            auth_settings, audience=_audience, scope=scopes_registry.get_standard_scopes_for(UserCategory.API_CLIENT),
        ),
        UserCategory.ADMIN: JWTIssuer.from_config(
            auth_settings, audience=_audience, scope=scopes_registry.get_standard_scopes_for(UserCategory.ADMIN)
        )
    }

    def __init__(
            self, user: UserDbOut,
            device_id: str
    ):
        self._user = user
        self._device_id = device_id

    def get_access_token(self, scope: list[str] = None) -> tuple[str, dict, dict]:
        issuer = self.get_issuer(self._user)
        return issuer.get_access_token(
            subject=self._get_sub_claim(), device_id=self._device_id, scope=scope
        )

    def get_refresh_token(self, scope: list[str] = None) -> tuple[str, dict, dict]:
        issuer = self.get_issuer(self._user)
        return issuer.get_refresh_token(
            subject=self._get_sub_claim(), device_id=self._device_id, scope=scope
        )

    def get_issuer(self, user: UserDbOut) -> tuple[str, dict, dict]:
        return self._user_category_issuer_map[user.category]

    def _get_sub_claim(self) -> str:
        return f'{self._subject_prefix}.{self._user.username}.id{self._user.id}'