import logging.config

from currency_exchange.loggingconf import LOGGING_CONF
from currency_exchange.auth.main import auth_router, admin_router
from currency_exchange.currency_exchange.fapiadoption.main import app

logging.config.dictConfig(LOGGING_CONF)


app.include_router(auth_router)
app.include_router(admin_router)
