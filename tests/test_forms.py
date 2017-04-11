from django.forms import forms
from django.test import TestCase

from email_extras.forms import KeyForm

from tests.utils import (
    TEST_PUBLIC_KEY, TEST_KEY_FINGERPRINT, GPGMixin
)


class KeyFormTestCase(GPGMixin, TestCase):
    maxDiff = 10000

    def setUp(self):
        if TEST_KEY_FINGERPRINT in self.gpg.list_keys().key_map:
            self.gpg.delete_keys([TEST_KEY_FINGERPRINT])

    def tearDown(self):
        if TEST_KEY_FINGERPRINT in self.gpg.list_keys().key_map:
            self.gpg.delete_keys([TEST_KEY_FINGERPRINT])

    def test_valid_key_data(self):
        form = KeyForm(data={
            'key': TEST_PUBLIC_KEY,
            'use_asc': False,
        })
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['key'].strip(),
                          TEST_PUBLIC_KEY.strip())
        self.assertEquals(form.cleaned_data['use_asc'], False)

    def test_invalid_key_data(self):
        form = KeyForm(data={
            'key': "The cat in the hat didn't come back after that",
            'use_asc': False,
        })
        self.assertFalse(form.is_valid())

        form.cleaned_data = form.data
        with self.assertRaises(forms.ValidationError):
            form.clean_key()
