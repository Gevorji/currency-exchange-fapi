import logging
import sys

from currency_exchange.config import general_settings

def info_and_below_logrecord_filter(logrecord: logging.LogRecord):
    if logrecord.levelno > logging.INFO:
        return False
    return True

LOGGING_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(name)s (%(levelname)s): %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'to_stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout,
            'filters': [info_and_below_logrecord_filter]
        },
        'to_stderr': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stderr,
        }
    },
    'root': {
        'handlers': ['to_stdout', 'to_stderr'],
        'level': 'DEBUG' if general_settings.DEBUG else general_settings.APP_LOG_LEVEL,
    }
}
