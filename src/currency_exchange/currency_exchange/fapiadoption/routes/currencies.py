from typing import Annotated
import logging

from fastapi import APIRouter, Security, status, HTTPException, Form, Path

from currency_exchange.auth import verify_access
from ...application import errors as appexc
from ..schemas import CurrencyOutSchema, AddCurrencySchema, UpdateCurrencySchema, CurrencyCodeField
from ..appadapter import currency_exchange_app
from ..dependencies import user_dependency

currencies_router = APIRouter()


logger = logging.getLogger('currency_exchange')

currency_code_path_field = Annotated[CurrencyCodeField, Path()]

@currencies_router.get('/currencies',
                       response_model=list[CurrencyOutSchema],
                       dependencies=[Security(verify_access, scopes=['currency:request'])])
async def get_all_currencies():
    return await currency_exchange_app.get_all_currencies()


currency_code_not_present_exc = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Request path to this '
                                                                                              'resource should be of a '
                                                                                              'form /currency/{code}')


@currencies_router.get('/currency', include_in_schema=False)
async def get_currency_stub():
    raise currency_code_not_present_exc


@currencies_router.patch('/currency', include_in_schema=False)
async def patch_currency_stub():
    raise currency_code_not_present_exc


@currencies_router.delete('/currency', include_in_schema=False)
async def delete_currency_stub():
    raise currency_code_not_present_exc

@currencies_router.get('/currency/{currency_code}', response_model=CurrencyOutSchema,
                       responses={404: {'description': 'Currency not found'},
                                  400: {'description': 'Currency code not provided'}},
                       dependencies=[Security(verify_access, scopes=['currency:request'])])
async def get_currency(currency_code: CurrencyCodeField, user: user_dependency):
    try:
        return await currency_exchange_app.get_currency(currency_code)
    except appexc.CurrencyDoesNotExistError:
        logger.debug('Error requesting currency %s by user %s', currency_code, user.username, exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Currency not found')


@currencies_router.post('/currencies', status_code=status.HTTP_201_CREATED, response_model=CurrencyOutSchema,
                        responses={400: {'description': 'Not enough fields provided'},
                                   409: {'description': 'Currency with such code already exists'}},
                        dependencies=[Security(verify_access, scopes=['currency:create'])])
async def add_currency(new_currency: Annotated[AddCurrencySchema, Form()], user: user_dependency):
    try:
        added_currency = await currency_exchange_app.add_currency(new_currency)
        logger.info('User %s added currency %s, %s, %s',
                    user.username, added_currency.code, added_currency.name, added_currency.sign)
        return added_currency
    except appexc.CurrencyAlreadyExistsError:
        logger.debug('Error on trying to add currency by user %s', user.username, exc_info=True)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,  detail=f'Currency with code {new_currency.code} '
                                                                          f'already exists')


@currencies_router.patch('/currency/{currency_code}', response_model=CurrencyOutSchema,
                         responses={400: {'description': 'Bad request data'},
                                    404: {'description': 'Currency not found'}},
                         dependencies=[Security(verify_access, scopes=['currency:update'])])
async def update_currency(currency_code: currency_code_path_field, currency_data: Annotated[UpdateCurrencySchema, Form()],
                          user: user_dependency):
    try:
       upd_currency = await currency_exchange_app.update_currency(currency_code, currency_data)
       logger.info('User %s updated currency %s, with %s', user.username,
                   currency_data.model_dump(exclude_unset=True))
       return upd_currency
    except appexc.CurrencyDoesNotExistError:
        logger.debug('Error on trying to update currency by user %s', user.username, exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Currency not found')


@currencies_router.delete('/currency/{currency_code}',
                          responses={400: {'description': 'Bad request data'},
                                     404: {'description': 'Currency not found'}},
                          dependencies=[Security(verify_access, scopes=['all'])])
async def delete_currency(currency_code: currency_code_path_field, user: user_dependency):
    try:
        deleted_currency = await currency_exchange_app.delete_currency(currency_code)
        logger.info('User %s deleted currency %s, %s', deleted_currency.code, deleted_currency.name)
    except appexc.CurrencyDoesNotExistError:
        logger.debug('Error on trying to delete currency by user %s', user.username, exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Currency not found')
