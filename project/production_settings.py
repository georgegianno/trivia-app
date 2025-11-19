import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '19mkp062m#fei(cekf*^deo4esg6u$piminbxvst!%@^pj=(#k'

DEBUG = False

ALLOWED_HOSTS = ['https://production-domain.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'project.application',
    'project.game',
]

MIDDLEWARE = [
    'project.application.middleware.SelfDestructionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'project.application.middleware.SessionRefreshMiddleware',
    'project.application.middleware.CustomErrorPagesMiddleware'
]

SESSION_SAVE_EVERY_REQUEST = True

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(ROOT_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # This populates context for the games
                'project.game.context_proccessors.game_secret'
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Settings are defined like this to have the option to use docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'trivia_db'),
        'USER': os.environ.get('DB_USER', 'trivia_db_owner'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'NA0;z3-b3£0@'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', 5432),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(ROOT_DIR, 'static')
STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Trivia API
TRIVIA_SESSION_TOKEN_URL = 'https://opentdb.com/api_token.php?command=request'
TRIVIA_SEARCH_URL = 'https://opentdb.com/api.php'
TRIVIA_TOKEN_INACTIVE_LIMIT = 60*60*6
NUMBER_OF_QUESTIONS_FETCHED = 50

# Game
GAME_SECRET = 'Squiz-game'
GAME_UPDATE_ACTION = 'update_game_timestamp'
GAME_START_ACTION = 'game_start_action'
PLAYER_LOSES_ACTION = 'player_loses_action'