
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


GNUPG_HOME = getattr(settings, "EMAIL_EXTRAS_GNUPG_HOME", None)
USE_GNUPG = getattr(settings, "EMAIL_EXTRAS_USE_GNUPG", GNUPG_HOME is not None)
ALWAYS_TRUST = getattr(settings, "EMAIL_EXTRAS_ALWAYS_TRUST_KEYS", False)


if USE_GNUPG:
    try:
        import gnupg
    except ImportError:
        raise ImproperlyConfigured("Could not import gnupg")
