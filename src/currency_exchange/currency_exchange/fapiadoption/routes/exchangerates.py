from typing import Annotated
import logging

from fastapi import APIRouter, HTTPException, status, Form, Path, Security
from sqlalchemy.sql.functions import user

from currency_exchange.auth import verify_access
from ...application import errors as appexc
from ..schemas import ExchangeRateOutSchema, AddExchangeRateSchema, UpdateExchangeRateSchema
from ..appadapter import currency_exchange_app
from ..dependencies import user_dependency

logger = logging.getLogger('currency_exchange')
exchange_rates_router = APIRouter()

CodePairPathField = Path(pattern='[a-zA-Z]{6}', examples=['USDRUB', 'RUBEUR'])

@exchange_rates_router.get('/exchangerates',
                           response_model=list[ExchangeRateOutSchema],
                           dependencies=[Security(verify_access, scopes=['exch_rate:request'])])
async def get_all_exchange_rates():
    return await currency_exchange_app.get_all_exchange_rates()


er_codes_not_present_exc = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Request path to this '
                                                                                              'resource should be of a '
                                                                                              'form /currency/{code}')


@exchange_rates_router.get('/exchangerate', include_in_schema=False)
async def get_currency_stub():
    raise er_codes_not_present_exc


@exchange_rates_router.patch('/exchangerate', include_in_schema=False)
async def patch_currency_stub():
    raise er_codes_not_present_exc


@exchange_rates_router.delete('/exchangerate', include_in_schema=False)
async def delete_currency_stub():
    raise er_codes_not_present_exc


@exchange_rates_router.get('/exchangerate/{code_pair}', response_model=ExchangeRateOutSchema,
                           responses={400: {'description': 'Bad data in request'},
                                      404: {'description': 'Rate not found'}},
                           dependencies=[Security(verify_access, scopes=['exch_rate:request'])])
async def get_exchange_rate(
        code_pair: Annotated[str, CodePairPathField], user: user_dependency
):
    base_code, target_code = code_pair[:3], code_pair[3:]
    try:
        return await currency_exchange_app.get_exchange_rate(base_code, target_code)
    except appexc.ExchangeRateDoesntExistError:
        logger.debug('Error on trying to get currency by user %s', user.username, exc_info=True)
        raise HTTPException(status_code=404, detail='Rate not found')


@exchange_rates_router.post('/exchangerates', status_code=status.HTTP_201_CREATED,
                            response_model=ExchangeRateOutSchema,
                            responses={409: {'description': 'Exchange rate already exists'},
                                       404: {'description': 'Currency(ies) not found'},
                                       400: {'description': 'Bad data in request'}},
                            dependencies=[Security(verify_access, scopes=['exch_rate:create'])])
async def add_exchange_rate(new_exchange_rate: Annotated[AddExchangeRateSchema, Form()], user: user_dependency):
    try:
        try:
            logger.debug('User %s adding exchange_rate %s', user.username, new_exchange_rate)
            added_er = await currency_exchange_app.add_exchange_rate(new_exchange_rate)
            logger.info('User %s added exchange rate %s', user.username, new_exchange_rate)
            return added_er
        except Exception:
            logger.debug('Error on trying to add exchange_rate %s by user %s', new_exchange_rate,
                         user.username, exc_info=True)
            raise
    except appexc.CurrencyDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=e.args[0])
    except appexc.ExchangeRateAlreadyExistsError:
        raise HTTPException(status_code=409, detail='Exchange rate already exists')
    except appexc.CurrencyToSameCurrencyExchangeRateError:
        raise HTTPException(status_code=409, detail='Can\'t add exchange rate to same currency')


@exchange_rates_router.patch('/exchangerate/{code_pair}', response_model=ExchangeRateOutSchema,
                             responses={404: {'description': 'Currency(ies) not found'},
                                        400: {'description': 'Bad data in request'}},
                             dependencies=[Security(verify_access, scopes=['exch_rate:update'])])
async def update_exchange_rate(
        code_pair: Annotated[str, CodePairPathField], er_data: Annotated[UpdateExchangeRateSchema, Form()],
        user: user_dependency
):
    base_code, target_code = code_pair[:3], code_pair[3:]
    try:
        try:
            upd_er = await currency_exchange_app.update_exchange_rate(base_code, target_code, er_data.rate)
            logger.debug('User %s updating exchange_rate %s-%s with %s',
                         user.username, base_code, target_code, er_data.model_dump(exclude_unset=True))
            logger.info('User %s updated exchange rate %s-%s with %s', user.username,
                        base_code, target_code, er_data.model_dump(exclude_unset=True))
            return upd_er
        except Exception:
            logger.debug('Error on trying to update exchange_rate %s by user %s',
                        f'{base_code}-{target_code}', user.username, exc_info=True)
            raise
    except appexc.CurrencyDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=e.args[0])


@exchange_rates_router.delete('/exchangerate/{code_pair}',
                              responses={404: {'description': 'Currency(ies) not found'},
                                         400: {'description': 'Bad request data'}},
                              dependencies=[Security(verify_access, scopes=['all'])])
async def delete_exchange_rate(code_pair: Annotated[str, CodePairPathField], user: user_dependency):
    base_code, target_code = code_pair[:3], code_pair[3:]
    try:
        deleted_er = await currency_exchange_app.delete_exchange_rate(base_code, target_code)
        logger.info('User %s deleted exchange rate %s-%s', user.username, base_code, target_code)
        return deleted_er
    except appexc.CurrencyDoesNotExistError as e:
        logger.debug('Error on trying to delete exchange_rate %s-%s by user %s', base_code, target_code,
                     user.username, exc_info=True)
        raise HTTPException(status_code=404, detail=e.args[0])


