from django.test import TestCase

from email_extras.models import Address, Key

from tests.utils import (
    TEST_KEY_FINGERPRINT, TEST_PUBLIC_KEY, GPGMixin,
)


class ModelFunctionTestCase(GPGMixin, TestCase):
    # This isn't too complex yet, but there are a few things left to do:
    #
    # * Implement queryset functions (create, update, delete)
    # * Implement tests for queryset functions
    # * Refactor functionality in the models' .save() function into signal
    #   handlers and connect them up in email_extras/apps.py
    #
    # Once we implement that this will get "filled in" a bit more
    #
    def test_key_model_functions(self):
        key = Key(key=TEST_PUBLIC_KEY, use_asc=False)
        key.save()

        # Test Key.__str__()
        self.assertEquals(str(key), TEST_KEY_FINGERPRINT)

        # Test Key.email_addresses property
        self.assertEquals(key.email_addresses,
                          'django-email-extras@example.com')

        address = Address.objects.get(key=key)

        # Test Address.__str__()
        self.assertEquals(str(address), 'django-email-extras@example.com')

        self.assertEquals(address.address, 'django-email-extras@example.com')

        fp = key.fingerprint
        self.assertEquals(fp, TEST_KEY_FINGERPRINT)

        address.delete()
        key.delete()

        self.assertEquals(Address.objects.count(), 0)
        self.assertEquals(Key.objects.count(), 0)
