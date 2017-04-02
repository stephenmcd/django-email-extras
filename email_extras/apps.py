from django.apps import AppConfig

from email_extras.settings import USE_GNUPG, SIGNING_KEY_FINGERPRINT
from email_extras.utils import get_gpg


class EmailExtrasConfig(AppConfig):
    name = 'email_extras'
    verbose_name = 'Email Extras'

    def ready(self):
        # Fail early and loudly if the signing key fingerprint is misconfigured
        if USE_GNUPG and SIGNING_KEY_FINGERPRINT is not None:
            gpg = get_gpg()
            try:
                gpg.list_keys().key_map[SIGNING_KEY_FINGERPRINT]
            except KeyError:
                raise Exception(
                    "The key specified by the "
                    "EMAIL_EXTRAS_SIGNING_KEY_FINGERPRINT setting"
                    "({fp}) does not exist in the GPG keyring. Adjust the"
                    "EMAIL_EXTRAS_GNUPG_HOME setting, correct the key "
                    "fingerprint, or generate a new key by running "
                    "python manage.py email_signing_key --generate to fix.")
