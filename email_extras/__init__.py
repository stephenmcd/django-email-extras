
from email_extras.settings import USE_GNUPG


__version__ = "0.1.0"

if USE_GNUPG:
    try:
        import gnupg
    except ImportError:
        try:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured, "Could not import gnupg"        except ImportError:
            pass


