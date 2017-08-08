from django.apps import AppConfig

from email_extras.utils import check_signing_key


class EmailExtrasConfig(AppConfig):
    name = 'email_extras'
    verbose_name = 'Email Extras'

    # AFAICT, this is impossible to test
    def ready(self):  # pragma: noqa
        # Fail early and loudly if the signing key fingerprint is misconfigured
        check_signing_key()
