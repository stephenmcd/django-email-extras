import os

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.utils.safestring import mark_safe

from email_extras.utils import EncryptionFailedError

from tests.utils import (SendMailFunctionMixin, SendMailMixin)


@override_settings(
    EMAIL_BACKEND='email_extras.backends.BrowsableEmailBackend',
    DEBUG=True)
class BrowsableEmailBackendTestCase(SendMailFunctionMixin, TestCase):
    mail_file = 'tests/mail.txt'
    send_mail_function = 'tests.utils.send_mail_with_backend'

    def _remove_mail_file(self):
        if os.path.exists(self.mail_file):
            os.remove(self.mail_file)

    def setUp(self):
        self._remove_mail_file()

    def tearDown(self):
        self._remove_mail_file()

    @override_settings(DEBUG=False)
    def test_with_debug_false(self):
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        # Make sure the file doesn't exist yet
        self.assertFalse(os.path.exists(self.mail_file))

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            html_message=mark_safe(msg_html))

        # The backend should bail when DEBUG = False
        self.assertFalse(os.path.exists(self.mail_file))

    def test_with_txt_mail(self):
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"

        # Make sure the file doesn't exist yet
        self.assertFalse(os.path.exists(self.mail_file))

        self.send_mail(
            msg_subject, msg_text, from_email, to)

        # Since there isn't an HTML alternative, the backend shouldn't fire
        self.assertFalse(os.path.exists(self.mail_file))

    def test_with_non_html_alternative(self):
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        # Make sure the file doesn't exist yet
        self.assertFalse(os.path.exists(self.mail_file))

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            alternatives=[(mark_safe(msg_html), 'application/gpg-encrypted')])

        # The backend should skip any non-HTML alternative
        self.assertFalse(os.path.exists(self.mail_file))

    def test_with_html_mail(self):
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        # Make sure the file doesn't exist yet
        self.assertFalse(os.path.exists(self.mail_file))

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            html_message=mark_safe(msg_html))

        # Make sure the file exists
        self.assertTrue(os.path.exists(self.mail_file))

        # Make sure the contents are expected
        with open(self.mail_file, 'r') as f:
            self.assertEquals(f.read().strip(), msg_html)

        # Try to remove it
        self._remove_mail_file()

        # Make sure the file doesn't exist
        self.assertFalse(os.path.exists(self.mail_file))


@override_settings(
    EMAIL_BACKEND='email_extras.backends.EncryptingLocmemEmailBackend')
class SendEncryptedMailBackendNoASCTestCase(SendMailMixin, TestCase):
    use_asc = False
    maxDiff = 10000
    send_mail_function = 'tests.utils.send_mail_with_backend'

    def test_send_mail_function_html_message_encrypted_alternative(self):
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        with open('tests/templates/email_extras/dr_suess.txt', 'r') as f:
            alt = f.read()

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            alternatives=[(alt, 'application/gpg-encrypted')])

        message = mail.outbox[0]

        # Decrypt and test the alternatives later, just ensure we have
        # any alternatives at all so we fail quickly
        self.assertNotEquals(message.alternatives, [])
        self.assertEquals(message.attachments, [])

        # We should only have one alternative - the txt message
        self.assertEquals(len(message.alternatives), 1)

        # Check the alternative to make sure it wasn't encrypted
        content, mimetype = message.alternatives[0]
        self.assertEquals(mimetype, "application/gpg-encrypted")
        self.assertEquals(content, alt)

    def test_handle_failed_alternative_encryption(self):
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        # Make sending the mail fail
        from email_extras import utils
        previous_value = utils.encrypt_kwargs['always_trust']
        utils.encrypt_kwargs['always_trust'] = False
        # Tweak the failed content handler to simply pass
        from email_extras import backends
        previous_content_handler = backends.handle_failed_message_encryption
        backends.handle_failed_message_encryption = lambda e: None
        with self.assertRaises(EncryptionFailedError):
            self.send_mail(
                msg_subject, msg_text, from_email, to,
                html_message=mark_safe(msg_html))
        backends.handle_failed_message_encryption = previous_content_handler
        utils.encrypt_kwargs['always_trust'] = previous_value

    def test_handle_failed_attachment_encryption(self):
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        # Make sending the mail fail
        from email_extras import utils
        previous_value = utils.encrypt_kwargs['always_trust']
        utils.encrypt_kwargs['always_trust'] = False
        # Tweak the failed content handler to simply pass
        from email_extras import backends
        previous_content_handler = backends.handle_failed_message_encryption
        alt_handler = backends.handle_failed_alternative_encryption
        previous_alt_handler = alt_handler
        backends.handle_failed_message_encryption = lambda e: None
        backends.handle_failed_alternative_encryption = lambda e: None
        with self.assertRaises(EncryptionFailedError):
            self.send_mail(
                msg_subject, msg_text, from_email, to,
                attachments=[('file.txt', msg_html, 'text/html')])
        backends.handle_failed_alternative_encryption = previous_alt_handler
        backends.handle_failed_message_encryption = previous_content_handler
        utils.encrypt_kwargs['always_trust'] = previous_value


@override_settings(
    EMAIL_BACKEND='email_extras.backends.EncryptingLocmemEmailBackend')
class SendEncryptedMailBackendWithASCTestCase(SendMailMixin, TestCase):
    use_asc = True
    send_mail_function = 'tests.utils.send_mail_with_backend'


@override_settings(
    EMAIL_BACKEND='email_extras.backends.EncryptingLocmemEmailBackend')
class SendDoNotEncryptMailBackendTestCase(SendMailMixin, TestCase):
    use_asc = True
    send_mail_function = 'tests.utils.send_mail_with_backend'

    def test_send_mail_function_txt_message(self):
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"

        self.send_mail(msg_subject, msg_text, from_email, to,
                       do_not_encrypt_this_message=True)

        message = mail.outbox[0]

        self.assertEquals(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext
        self.assertEquals(message.body, msg_text)
        self.assertEquals(message.to, to)
        self.assertEquals(message.cc, [])
        self.assertEquals(message.bcc, [])
        self.assertEquals(message.reply_to, [])
        self.assertEquals(message.from_email, from_email)
        self.assertEquals(message.extra_headers, {})
        self.assertEquals(message.alternatives, [])
        self.assertEquals(message.attachments, [])
