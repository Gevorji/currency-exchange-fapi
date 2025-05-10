from typing import Annotated, Literal, Optional
import logging

from fastapi import APIRouter, Form, status, HTTPException
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder

from . import get_users_repo, get_token_state_repo, errors
from .schemas import (
    UserDbIn, UserDbOut, TokenStateDbIn, UserCreationErrorResponse,
    UserCreatedResponse, TokenCreatedResponse, TokensRevokedResponse
)
from .providers import (
    JWTIssuerProvider, get_active_user_oauth, jwt_validator_provider, RevocationCheckerType,
    jwt_revocation_checker_provider, get_active_user_http_basic_auth, http_basic_auth_scheme
)
from .services.jwtservice import JWTValidator
from .services.permissions import UserCategory
from .utils import (
    revoke_all_users_tokens_per_device, get_user_id_from_sub_jwt_claim, revoke_users_tokens,
    check_password, save_token_state_in_db
)

logger = logging.getLogger('auth')

token_router = APIRouter()

clients_router = APIRouter()


@clients_router.post(
    '/register', status_code=status.HTTP_201_CREATED, response_model=UserCreatedResponse,
    responses={
        400: {'model': UserCreationErrorResponse, 'description': 'Submitted values invalid'},
        409: {'model': UserCreationErrorResponse, 'description': 'User already exists'},
    }
)
async def create_user(
        username: Annotated[str, Form()], password1: Annotated[str, Form()], password2: Annotated[str, Form()]
):
    if password1 != password2:
        logger.info('Unsuccessful attempt to register user %s', username)
        return JSONResponse(
            jsonable_encoder(
                UserCreationErrorResponse.model_validate({'errors': {'password': ['Passwords do not match']}})
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user_repo = get_users_repo()
    try:
        try:
            user = await user_repo.save(
                UserDbIn(username=username, password=password1, category=UserCategory.API_CLIENT, is_active=True)
            )
            logger.info('Successfully registered user %s', user.username)
            return UserCreatedResponse.model_validate(user)
        except Exception as e:
            logger.info('Unsuccessful attempt to register user %s', username)
            logger.debug('Exception info of unsuccessful registration', username, exc_info=e)
            raise
    except ValueError as e:
        return JSONResponse(
            jsonable_encoder(UserCreationErrorResponse.model_validate({'errors': e.args[0]})),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except errors.UserAlreadyExistsError:
        return JSONResponse(
            jsonable_encoder(
                UserCreationErrorResponse.model_validate({'errors': {'username': ['Username already in use']}})
            ),
            status_code=status.HTTP_409_CONFLICT
        )


@token_router.post(
    '/gain', response_model=TokenCreatedResponse,
    responses={401: {'description': 'Invalid credentials'}, 403: {'description': 'User disabled'}}
)
async def create_token(
        user: Annotated[UserDbOut, Depends(get_active_user_oauth)],
        ouath_form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        device_id: Annotated[str, Form()] = 'none',
):
    check_password(user, ouath_form_data.password)
    token_issuer = JWTIssuerProvider(user, device_id)
    access_token_str, _, access_token_payload = token_issuer.get_access_token()
    refresh_token_str, _, refresh_token_payload = token_issuer.get_refresh_token()

    await revoke_all_users_tokens_per_device(user, device_id)

    await save_token_state_in_db(access_token_payload, 'access', user.id)
    await save_token_state_in_db(refresh_token_payload, 'refresh', user.id)

    logger.info('Issued token for user %s', user.username)
    logger.debug(
        'Generated %s\'s tokens:\n%s\n%s\n(end of tokens)',
        user.username, access_token_payload, refresh_token_payload
    )

    return TokenCreatedResponse(
        access_token=access_token_str,
        token_type='bearer',
        refresh_token=refresh_token_str,
        expires_in=access_token_payload['exp'] - access_token_payload['iat'],
        scope=access_token_payload['scope']
    )


@token_router.post(
    '/refresh', response_model=TokenCreatedResponse,
    responses={
        400: {'description': 'Token is invalid'},
        401: {'description': 'Invalid credentials'},
        403: {'description': 'User disabled or token owner is not a user, or token is revoked'}
    }
)
async def refresh_access_token(
        user: Annotated[UserDbOut, Depends(get_active_user_http_basic_auth)],
        user_credentials: Annotated[HTTPBasicCredentials, Depends(http_basic_auth_scheme)],
        grant_type: Annotated[Literal['refresh_token'], Form(description='Required to be an exact "refresh_token" value')],
        refresh_token: Annotated[str, Form()],
        token_validator: Annotated[JWTValidator, Depends(jwt_validator_provider)],
        revocation_checker: Annotated[RevocationCheckerType, Depends(jwt_revocation_checker_provider)],
):
    exc_args = {'status_code': status.HTTP_400_BAD_REQUEST}

    check_password(user, user_credentials.password)

    try:
        try:
            token = token_validator.token_validate(refresh_token)

            token_owner_id = get_user_id_from_sub_jwt_claim(token.claims.sub)

            if token_owner_id != user.id:
                raise HTTPException(detail='Token owner does not match with client from request',
                                    status_code=status.HTTP_403_FORBIDDEN)
        except errors.JWTValidationError as e:
            logger.debug(
                'Token validation problem. Token header: %s. Token payload: %s',
                e.header, e.payload, exc_info=True
            )
            raise
    except errors.BadSignatureError as e:
        raise HTTPException(detail=str('Bad token signature'), **exc_args) from e
    except errors.InvalidTokenClaimError as e:
        raise HTTPException(detail='Invalid token', **exc_args) from e
    except errors.ExpiredTokenError as e:
        raise HTTPException(detail='Expired token', **exc_args) from e
    try:
        revoked = await revocation_checker(token)
        if revoked:
            await revoke_all_users_tokens_per_device(user, token.claims.device_id)
            raise HTTPException(
                detail='Revoked token. Authentication process should be repeated.',
                status_code=status.HTTP_403_FORBIDDEN
            )
    except errors.TokenDoesNotExistError as e:
        raise HTTPException(detail='Unrecognized token', **exc_args) from e

    previous_access_scopes = token.claims.scope[1:] # first scope will always be 'refresh'

    token_issuer = JWTIssuerProvider(user, token.claims.device_id)
    access_token_str, _, access_token_payload = token_issuer.get_access_token(scope=previous_access_scopes)
    refresh_token_str, _, refresh_token_payload = token_issuer.get_refresh_token(scope=token.claims.scope)

    await revoke_all_users_tokens_per_device(user, token.claims.device_id)

    await save_token_state_in_db(access_token_payload, 'access', user.id)
    await save_token_state_in_db(refresh_token_payload, 'refresh', user.id)

    logger.info('Refreshed token for user %s', user.username)
    logger.debug(
        'Generated %s\'s tokens:\n%s\n%s\n(end of tokens)',
        user.username, access_token_payload, refresh_token_payload
    )

    return TokenCreatedResponse(
        access_token=access_token_str,
        token_type='bearer',
        refresh_token=refresh_token_str,
        expires_in=access_token_payload['exp'] - access_token_payload['iat'],
        scope=access_token_payload['scope']
    )


@token_router.patch(
    '/revoke', status_code=status.HTTP_200_OK, response_model=TokensRevokedResponse,
    responses={401: {'description': 'Invalid credentials'}, 403: {'description': 'User disabled'}}
)
async def revoke_users_token(
        user: Annotated[UserDbOut, Depends(get_active_user_http_basic_auth)],
        user_credentials: Annotated[HTTPBasicCredentials, Depends(http_basic_auth_scheme)],
        tokens: Annotated[Optional[list[str]], Form()] = None
):
    check_password(user, user_credentials.password)
    revoked = await revoke_users_tokens(user, tokens)
    return TokensRevokedResponse(revoked=revoked)
