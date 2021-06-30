from datetime import datetime

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "basic": {"format": "%(name)s - %(levelname)s - %(message)s"},
        "extended": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "basic",
            "stream": "ext://sys.stdout",
        },
        "console_test": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "extended",
            "stream": "ext://sys.stdout",
        },
        "file_handler": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "extended",
            "filename": "./logs/{:%Y-%m-%d_%H-%M-%S}.log".format(datetime.now()),
            "encoding": "UTF-8",
        },
    },
    "loggers": {
        "lyrics": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "preprocessing": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "dataset": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "db": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "main": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    },
}
