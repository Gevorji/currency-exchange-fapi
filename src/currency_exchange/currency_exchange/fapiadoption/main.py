from alembic.util import status
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .routes.currencies import currencies_router
from .routes.exchangerates import exchange_rates_router
from .routes.currenciesconvertion import currencies_convertion_router


app = FastAPI()
app.include_router(currencies_router)
app.include_router(exchange_rates_router)
app.include_router(currencies_convertion_router)


@app.exception_handler(HTTPException)
async def app_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={'message': exc.detail})


@app.exception_handler(RequestValidationError)
async def app_request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder({'message': exc.errors()}))