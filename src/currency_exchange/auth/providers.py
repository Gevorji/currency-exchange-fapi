from collections.abc import Awaitable
from typing import Annotated, Callable
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    SecurityScopes, OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials, OAuth2PasswordRequestForm
)
from starlette.requests import Request

from .routes import TOKEN_URL
from .schemas import UserDbOut
from .services.permissions import scopes_registry, UserCategory
from .services.jwtservice import JWTValidator, JWTModel, JWTIssuer
from .services.passwordhashing import match_password
from . import errors
from currency_exchange.config import auth_settings
from .utils import check_jwt_revocation, get_user, get_active_user, get_user_from_sub_jwt_claim

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


jwt_validator_provider = JWTValidatorProvider(JWTValidator.from_config(auth_settings))
jwt_revocation_checker_provider = JWTRevocationCheckerProvider(check_jwt_revocation)


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
    except errors.CorruptedTokenDataError as e:
        raise HTTPException(detail='Corrupted token', **exc_args) from e
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
    if token.claims.scope[0] == 'refresh':
        logger.debug('Access denied.')
        raise HTTPException(detail='Access denied. Attempted to access with refresh token.', **forbidden_exc_args)


async def get_user_ouath(ouath_form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> UserDbOut:
    return await get_user(ouath_form_data.username)


async def get_active_user_oauth(ouath_form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> UserDbOut:
    return await get_active_user(ouath_form_data.username)


async def get_user_http_basic_auth(
        user_credentials: Annotated[HTTPBasicCredentials, Depends(http_basic_auth_scheme)]
) -> UserDbOut:
    return await get_active_user(user_credentials.username)


async def get_active_user_http_basic_auth(
        user_credentials: Annotated[HTTPBasicCredentials, Depends(http_basic_auth_scheme)]
) -> UserDbOut:
    return await get_active_user(user_credentials.username)


async def get_user_from_bearer_token(bearer_token: Annotated[JWTModel, Depends(validate_jwt)]) -> UserDbOut:
    return await get_user_from_sub_jwt_claim(bearer_token.claims.sub)


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