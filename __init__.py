
from django.core.exceptions import ImproperlyConfigured

from email_extras.settings import USE_GNUPG


if USE_GNUPG:
	try:
		import gnupg
	except ImportError:
		raise ImproperlyConfigured, "Could not import gnupg"
