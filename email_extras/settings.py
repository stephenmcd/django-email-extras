from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


GNUPG_HOME = getattr(settings, "EMAIL_EXTRAS_GNUPG_HOME", None)
USE_GNUPG = getattr(settings, "EMAIL_EXTRAS_USE_GNUPG", GNUPG_HOME is not None)

ALWAYS_TRUST = getattr(settings, "EMAIL_EXTRAS_ALWAYS_TRUST_KEYS", False)
FAILURE_HANDLERS = {
    'message': 'email_extras.handlers.default_handle_failed_encryption',
    'alternative': 'email_extras.handlers.default_handle_failed_alternative_encryption',
    'attachment': 'email_extras.handlers.default_handle_failed_attachment_encryption',
}
FAILURE_HANDLERS.update(getattr(settings, "EMAIL_EXTRAS_FAILURE_HANDLERS", {}))
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
SIGNING_KEY_FINGERPRINT = getattr(
    settings, "EMAIL_EXTRAS_SIGNING_KEY_FINGERPRINT", None)

if USE_GNUPG:
    try:
        import gnupg  # noqa: F401
    except ImportError:  # pragma: no cover
        raise ImproperlyConfigured("Could not import gnupg")
