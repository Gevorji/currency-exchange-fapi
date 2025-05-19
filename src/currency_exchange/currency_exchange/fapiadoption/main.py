from fastapi import FastAPI, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from .routes.currencies import currencies_router
from .routes.exchangerates import exchange_rates_router
from .routes.currenciesconvertion import currencies_convertion_router


def custom_generate_unique_id(route: APIRoute):
	return f"{route.tags[0]}-{route.name}"


app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
app.include_router(currencies_router, tags=["Currency exchange"])
app.include_router(exchange_rates_router, tags=["Currency exchange"])
app.include_router(currencies_convertion_router, tags=["Currency exchange"])


@app.exception_handler(HTTPException)
async def app_http_exception_handler(
	request: Request, exc: HTTPException
) -> JSONResponse:
	return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


@app.exception_handler(RequestValidationError)
async def app_request_validation_error_handler(
	request: Request, exc: RequestValidationError
) -> JSONResponse:
	return JSONResponse(
		status_code=status.HTTP_400_BAD_REQUEST,
		content=jsonable_encoder({"message": exc.errors()}),
	)
