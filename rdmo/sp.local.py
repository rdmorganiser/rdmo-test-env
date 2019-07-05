import os

from rdmo.core.settings import INSTALLED_APPS, AUTHENTICATION_BACKENDS, MIDDLEWARE

from . import BASE_DIR

SITE_ID = 2

MULTISITE = True

DEBUG = True

SECRET_KEY = 'this is not a very secret key'

ALLOWED_HOSTS = ['localhost', 'ip6-localhost', '127.0.0.1', '[::1]', 'sp.test.rdmo.org']

LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/srv/rdmo/rdmo.sqlite3',
    }
}

SHIBBOLETH = True
PROFILE_UPDATE = False

INSTALLED_APPS += ['shibboleth']

SHIBBOLETH_ATTRIBUTE_MAP = {
    'eppn': (True, 'username'),
    'givenName': (True, 'first_name'),
    'sn': (True, 'last_name'),
    'mail': (True, 'email'),
}

SHIBBOLETH_GROUP_ATTRIBUTES = ['eduPersonScopedAffiliation']

AUTHENTICATION_BACKENDS.append('shibboleth.backends.ShibbolethRemoteUserBackend')

MIDDLEWARE.insert(
    MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware') + 1,
    'shibboleth.middleware.ShibbolethRemoteUserMiddleware'
)

LOGIN_URL = '/Shibboleth.sso/Login?target=/projects'
LOGOUT_URL = '/Shibboleth.sso/Logout'

LOGGING_DIR = os.path.join(BASE_DIR, 'log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s'
        },
        'name': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s'
        },
        'console': {
            'format': '[%(asctime)s] %(message)s'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'error_log': {
            'level': 'ERROR',
            'class':'logging.FileHandler',
            'filename': os.path.join(LOGGING_DIR, 'error.log'),
            'formatter': 'default'
        },
        'rdmo_log': {
            'level': 'DEBUG',
            'class':'logging.FileHandler',
            'filename': os.path.join(LOGGING_DIR, 'rdmo.log'),
            'formatter': 'name'
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins', 'error_log'],
            'level': 'ERROR',
            'propagate': True
        },
        'rdmo': {
            'handlers': ['rdmo_log'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
