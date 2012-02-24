
__version__ = "0.1.6"


try:
    from email_extras.settings import USE_GNUPG
except ImportError:
    pass
else:
    if USE_GNUPG:
        try:
            import gnupg
        except ImportError:
            raise ImproperlyConfigured, "Could not import gnupg"


