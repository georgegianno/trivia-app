from .production_settings import *  # NOQA

DEBUG = True

ALLOWED_HOSTS += ['*']

INTERNAL_IPS = ALLOWED_HOSTS


MIDDLEWARE += [
    # Comment this line to view traceback of errors in debug mode
    'project.application.middleware.CustomErrorPagesMiddleware'
]

DATABASES['default'].update({
    'TEST': {
        'NAME': 'trivia_db_test'
    }
})