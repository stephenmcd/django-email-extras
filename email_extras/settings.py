
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


GNUPG_HOME = getattr(settings, "EMAIL_EXTRAS_GNUPG_HOME", None)
USE_GNUPG = getattr(settings, "EMAIL_EXTRAS_USE_GNUPG", GNUPG_HOME is not None)

ALWAYS_TRUST = getattr(settings, "EMAIL_EXTRAS_ALWAYS_TRUST_KEYS", False)
GNUPG_ENCODING = getattr(settings, "EMAIL_EXTRAS_GNUPG_ENCODING", None)
SIGNING_KEY_DATA = {
    'key_type': "RSA",
    'key_length': 4096,
    'name_real': settings.SITE_NAME,
    'name_comment': "Outgoing email server",
    'name_email': settings.DEFAULT_FROM_EMAIL,
    'expire_date': '2y',
}
SIGNING_KEY_DATA.update(getattr(settings, "EMAIL_EXTRAS_SIGNING_KEY_DATA", {}))

# Used internally
encrypt_kwargs = {
    'always_trust': ALWAYS_TRUST,
}


if USE_GNUPG:
    try:
        import gnupg  # noqa: F401
    except ImportError:
        raise ImproperlyConfigured("Could not import gnupg")
