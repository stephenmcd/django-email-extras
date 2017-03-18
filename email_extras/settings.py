
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


DEFAULT_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEBUG = getattr(settings, "DEBUG")
GNUPG_HOME = getattr(settings, "EMAIL_EXTRAS_GNUPG_HOME", None)
USE_GNUPG = getattr(settings, "EMAIL_EXTRAS_USE_GNUPG", GNUPG_HOME is not None)
ALWAYS_TRUST = getattr(settings, "EMAIL_EXTRAS_ALWAYS_TRUST_KEYS", False)
GNUPG_ENCODING = getattr(settings, "EMAIL_EXTRAS_GNUPG_ENCODING", None)
ACTUAL_DEBUG_BACKEND = getattr(settings, "EMAIL_EXTRAS_ACTUAL_DEBUG_BACKEND",
                               DEFAULT_BACKEND)

if USE_GNUPG:
    try:
        import gnupg
    except ImportError:
        raise ImproperlyConfigured("Could not import gnupg")
