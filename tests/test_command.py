import re
import sys
try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO
from unittest import skipIf

from django.core.management import call_command, CommandError
from django.test import TestCase

from email_extras.models import Key

from tests.utils import TEST_KEY_FINGERPRINT


@skipIf(sys.version_info < (3,), "Test uses assertRaisesRegex")
class TestEmailSigningKeyCommandTestCase(TestCase):
    def _generate_signing_key(self):
        out = StringIO()
        err = StringIO()

        self.assertEquals(Key.objects.count(), 0)

        call_command('email_signing_key', '--generate',
                     stdout=out, stderr=err)

        key_data = out.getvalue().strip().split('\n')

        # For Python 3 we can jsut do fp, header, *blocks, footer = key_data
        fp, header = key_data[0:2]
        blocks = key_data[2:-1]
        footer = key_data[-1]

        self.assertRegex(fp, r'^[0-9A-F]{40}$')
        self.assertEquals(header, "-----BEGIN PGP PUBLIC KEY BLOCK-----")
        self.assertEquals(footer, "-----END PGP PUBLIC KEY BLOCK-----")

        self.assertEquals(err.getvalue(), '')

        self.assertEquals(Key.objects.count(), 1)

        key = Key.objects.get()

        # For Python 3.5+ we can just do key_data = [header, *blocks, footer]
        key_data = [header]
        key_data.extend(blocks)
        key_data.append(footer)

        self.assertEquals(key.key.strip(), '\n'.join(key_data))

        self.fp = fp

    def _delete(self, key):
        for address in key.address_set.all():
            address.delete()

        key.delete()

        self.assertEquals(Key.objects.count(), 0)

    def test_generated_signing_key(self):
        self._generate_signing_key()

        self._delete(Key.objects.get())

    def test_print_private_key(self):
        self._generate_signing_key()

        print_out = StringIO()
        print_err = StringIO()

        call_command('email_signing_key', self.fp, '--print-private-key',
                     stdout=print_out, stderr=print_err)

        print_private_key_data = print_out.getvalue().strip().split('\n')
        # In Python 3 we can just do:
        # header, version, *_, footer = print_private_key_data
        header, version = print_private_key_data[0:2]
        footer = print_private_key_data[-1]

        self.assertRegex(version, r'^Version: .*$')
        self.assertEquals(header, "-----BEGIN PGP PRIVATE KEY BLOCK-----")
        self.assertEquals(footer, "-----END PGP PRIVATE KEY BLOCK-----")

        self.assertEquals(print_err.getvalue(), '')

        self.assertEquals(Key.objects.count(), 1)

        self._delete(Key.objects.get())

    def test_upload_to_keyservers(self):
        self._generate_signing_key()

        data = {
            'keyservers': [],
            'fingerprint': '',
        }

        def fake_upload_keys(keyservers, fingerprint):
            data['keyservers'] = keyservers
            data['fingerprint'] = fingerprint

        upload_out = StringIO()
        upload_err = StringIO()

        from email_extras.management.commands import email_signing_key
        previous_value = email_signing_key.upload_keys
        email_signing_key.upload_keys = fake_upload_keys

        call_command('email_signing_key', self.fp, '--keyserver', 'localhost',
                     stdout=upload_out, stderr=upload_err)

        self.assertEquals(data['keyservers'], 'localhost')
        self.assertEquals(data['fingerprint'], self.fp)

        self.assertEquals(upload_out.getvalue(), '')
        self.assertEquals(upload_err.getvalue(), '')

        email_signing_key.upload_keys = previous_value

        self._delete(Key.objects.get())

    def test_fingerprint_and_generate_flag_raises_error(self):
        out = StringIO()
        err = StringIO()

        rgx = re.compile(r'^You cannot specify fingerprints and --generate '
                         r'when running this command$')

        self.assertEquals(Key.objects.count(), 0)

        with self.assertRaisesRegex(CommandError, rgx):
            call_command('email_signing_key', TEST_KEY_FINGERPRINT,
                         generate=True, stdout=out, stderr=err)

        self.assertEquals(out.getvalue(), '')
        self.assertEquals(err.getvalue(), '')

    def test_no_matching_fingerprint_raises_error(self):
        out = StringIO()
        err = StringIO()

        missing_fingerprint = '01234567890ABCDEF01234567890ABCDEF01234567'
        rgx = re.compile(r'''^Key matching fingerprint '{fp}' not '''
                         r'''found.$'''.format(fp=missing_fingerprint))

        self.assertEquals(Key.objects.count(), 0)

        with self.assertRaisesRegex(CommandError, rgx):
            call_command('email_signing_key', missing_fingerprint,
                         stdout=out, stderr=err)

        self.assertEquals(out.getvalue(), '')
        self.assertEquals(err.getvalue(), '')
