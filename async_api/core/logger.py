from pydantic import BaseSettings, Field


class LoggingSettings(BaseSettings):
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_default_handlers = [
        'console',
    ]

    log_level_handlers = Field('DEBUG', env='LOG_LEVEL_HANDLERS')
    log_level_loggers = Field('INFO', env='LOG_LEVEL_LOGGERS')
    log_level_root = Field('INFO', env='LOG_LEVEL_ROOT')


log_settings = LoggingSettings()


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': log_settings.log_format},
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s %(message)s',
            'use_colors': None,
        },
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    },
    'handlers': {
        'console': {
            'level': log_settings.log_level_handlers,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'access': {
            'formatter': 'access',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': log_settings.log_default_handlers,
            'level': log_settings.log_level_loggers,
        },
        'uvicorn.error': {
            'level': log_settings.log_level_loggers,
        },
        'uvicorn.access': {
            'handlers': ['access'],
            'level': log_settings.log_level_loggers,
            'propagate': False,
        },
    },
    'root': {
        'level': log_settings.log_level_root,
        'formatter': 'verbose',
        'handlers': log_settings.log_default_handlers,
    },
}
