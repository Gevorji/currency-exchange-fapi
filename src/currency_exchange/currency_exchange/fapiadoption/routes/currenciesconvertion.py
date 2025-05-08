import logging
from typing import Annotated

from fastapi import APIRouter, Query, status, HTTPException, Security

from currency_exchange.auth import verify_access
from ...application import errors as appexc
from ..appadapter import currency_exchange_app
from ..schemas import ConvertedCurrencySchema, CurrencyConvertionDataSchema
from ..dependencies import user_dependency

logger = logging.getLogger('currency_exchange')
currencies_convertion_router = APIRouter()


@currencies_convertion_router.get('/exchange', response_model=ConvertedCurrencySchema,
                                  responses={404: {'description': 'Exchange rate not found'},
                                             400: {'description': 'Bad request data'}},
                                  dependencies=[Security(verify_access, scopes=['exch_rate:request'])])
async def convert_currencies(convertion_data: Annotated[CurrencyConvertionDataSchema, Query()], user: user_dependency):
    try:
        try:
            return await currency_exchange_app.convert_currency(convertion_data.from_, convertion_data.to,
                                                          convertion_data.amount)
        except Exception:
            logger.debug('Error on trying to convert currency by user %s (%s %s to %s)', user.username,
                         convertion_data.amount, convertion_data.from_, convertion_data.to, exc_info=True)
            raise
    except appexc.CurrenciesConvertionError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Exchange rate not found')
