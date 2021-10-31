import sys
import logging
import logging.config

LOGGER = logging.getLogger("airsec")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "stream": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s [%(filename)s:%(lineno)d"
        }
    },
    "handlers": {
        "stdout": {
            "level": "INFO",
            "formatter": "stream",
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        },
        "stderr": {
            "level": "INFO",
            "formatter": "stream",
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr'
        }
    },
    "loggers": {
        "airsec": {
            "handlers": ["stdout", "stderr"],
            "levels": "INFO",
            "propagate": False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("airsec")
