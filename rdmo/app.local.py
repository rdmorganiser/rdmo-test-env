import os
import ldap

from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

from . import BASE_DIR

DEBUG = True

SECRET_KEY = 'this is not a very secret key'

ALLOWED_HOSTS = ['localhost', 'ip6-localhost', '127.0.0.1', '[::1]', 'app.test.rdmo.org']

LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'rdmo.sqlite3',
    }
}

PROFILE_UPDATE = False

AUTH_LDAP_SERVER_URI = "ldap://ldap.test.rdmo.org"
AUTH_LDAP_BIND_DN = "uid=rdmo,dc=ldap,dc=test,dc=rdmo,dc=org"
AUTH_LDAP_BIND_PASSWORD = "rdmo"
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "dc=ldap,dc=test,dc=rdmo,dc=org", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
)
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    'email': 'mail'
}
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "dc=ldap,dc=test,dc=rdmo,dc=org", ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")
AUTH_LDAP_MIRROR_GROUPS = ['special']

AUTHENTICATION_BACKENDS = (
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
)

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
        'ldap_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_DIR, 'ldap.log'),
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
        'django_auth_ldap': {
            "level": "DEBUG",
            "handlers": ["ldap_log"]
        },
        'rdmo': {
            'handlers': ['rdmo_log'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
