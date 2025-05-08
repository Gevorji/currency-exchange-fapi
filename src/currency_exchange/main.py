from logging.config import dictConfig as loggingDictConfig

from currency_exchange.loggingconf import LOGGING_CONF


loggingDictConfig(LOGGING_CONF)
