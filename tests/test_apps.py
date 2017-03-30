from django.test import TestCase, override_settings

from email_extras.utils import BadSigningKeyError, check_signing_key

from tests.utils import (
    GPGMixin, TEST_PRIVATE_KEY, TEST_KEY_FINGERPRINT,
)


MODIFIED_FINGERPRINT = "{}{}".format(
    TEST_KEY_FINGERPRINT[:-1],
    "0" if TEST_KEY_FINGERPRINT[-1] != "0" else "1")


@override_settings(
    EMAIL_EXTRAS_SIGNING_KEY_FINGERPRINT=TEST_KEY_FINGERPRINT)
class NoBadSigningKeyErrorTestCase(GPGMixin, TestCase):
    use_asc = False
    maxDiff = 10000
    send_mail_function = 'email_extras.utils.send_mail'

    def test_no_exception(self):
        from email_extras import utils
        try:
            self.gpg.import_keys(TEST_PRIVATE_KEY)
            previous_value = utils.SIGNING_KEY_FINGERPRINT
            utils.SIGNING_KEY_FINGERPRINT = TEST_KEY_FINGERPRINT
            check_signing_key()
        except (BadSigningKeyError, KeyError):
            error_raised = True
        else:
            error_raised = False
        finally:
            self.assertFalse(error_raised, "BadSigningKeyError was raised")
            utils.SIGNING_KEY_FINGERPRINT = previous_value
            self.gpg.delete_keys([TEST_KEY_FINGERPRINT], True)


@override_settings(
    EMAIL_EXTRAS_SIGNING_KEY_FINGERPRINT=MODIFIED_FINGERPRINT)
class BadSigningKeyErrorTestCase(GPGMixin, TestCase):
    use_asc = False
    maxDiff = 10000
    send_mail_function = 'email_extras.utils.send_mail'

    @classmethod
    def setUpClass(cls):
        super(BadSigningKeyErrorTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(BadSigningKeyErrorTestCase, cls).tearDownClass()

    def test_exception(self):
        from email_extras import utils
        try:
            previous_value = utils.SIGNING_KEY_FINGERPRINT
            utils.SIGNING_KEY_FINGERPRINT = MODIFIED_FINGERPRINT
            check_signing_key()
        except BadSigningKeyError:
            self.assertTrue(True, "BadSigningKeyError was raised")
        else:
            self.assertFalse(True, "No BadSigningKeyError was raised")
        finally:
            utils.SIGNING_KEY_FINGERPRINT = previous_value
