from __future__ import print_function

from django.conf import settings
from django.core import mail
from django.utils.safestring import mark_safe

from email_extras.models import Key

from email_extras.utils import get_gpg, EncryptionFailedError

# Generated with:
#
# key_data = {
#     'key_type': "RSA",
#     'key_length': 4096,
#     'name_real': 'django-email-extras test project',
#     # 'name_comment': "Test address and key for django-email-extras",
#     'name_email': 'django-email-extras@example.com',
#     'expire_date': 0,
# }

# key = gpg.gen_key(gpg.gen_key_input(**key_data))
# public_fp = key.fingerprint
# private_key = gpg.export_keys(key.fingerprint, True, armor=True)
# public_key = gpg.export_keys(key.fingerprint, armor=True)
# gpg.delete_keys([private_fp], True)
# gpg.delete_keys([public_fp])
# print('TEST_KEY_FINGERPRINT = "{}"'.format(public_fp))
# print('TEST_PRIVATE_KEY = """\n{}"""'.format(private_key))
# print('TEST_PUBLIC_KEY = """\n{}"""'.format(public_key))
#
TEST_KEY_FINGERPRINT = "5C5C560DA52021E167B5D713C9EA85FD5D576B8D"
TEST_PRIVATE_KEY = """
-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: GnuPG/MacGPG2 v2

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
ayBef79l2Ir9GA==
=B5JT
-----END PGP PRIVATE KEY BLOCK-----
"""
TEST_PUBLIC_KEY = """
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG/MacGPG2 v2

mQINBFjrQhQBEADknfZRSqDxWY7o/yiiiXX1peUhKmMxdgHmIPdT4VL7P//DRRmK
OBuUan22dVduA9h1tdOpEviejJmw63rJLPmFaR3knhHcPkhhlx2AoHaSNzZNZk9M
r0c23BRILckeKGenrzhxzdWi1Yp+XWzsEzUuf0X3X8zLJ6Kf3P79d3uEA7hxupqs
Q18NzfZx3cyewL3dL00Z54LFMf+QLyj/Rn2YKjj2XgBJ6e4cOgv3CJJCDueLDjSO
XL4Q/yoXGahEeQlnWL0n0dya2G3zOgYfIQDDSkhSCDF5n9yiJldEVMrdckIoWtkp
JeTJBC2lgty0vl2XuWPo8gyGJ0KDYCx/hwjoR44BsQbAx//3EmU4DWp2TqvuuFWB
WVnFghXFRMp/SMBflQPXcLb5Qy1ea9xo64MGBsw+ajOFjf58aViUAd1YZm4ejIic
MRYOpkSYUWR3kuZL2VZvVKC1bC3M0fkTV9lciwir4n7CivfCqxRr19tx+2Pfep13
1gf6jtrNTRlJyvpaOPGXqJGJJS2BLuWZK+G6tHB3OnOQBGlXCraJQoTjK8V7I9ng
LQLAOdssefV40ijznD2w7YOTI7CwSsqGamwX5diJ5bePU2Fh/paXkVSYQAScje1/
JAbuHGp8Cewnk81VdXqav3XzHbGWuqx073881P2WYYoio2bJwMYpk2mjxQARAQAB
tEJkamFuZ28tZW1haWwtZXh0cmFzIHRlc3QgcHJvamVjdCA8ZGphbmdvLWVtYWls
LWV4dHJhc0BleGFtcGxlLmNvbT6JAjkEEwEIACMFAljrQhQCGy8HCwkIBwMCAQYV
CAIJCgsEFgIDAQIeAQIXgAAKCRDJ6oX9XVdrjTtPD/90ygOHzgqOEYowq9XpUcye
3VqL/jk0zichZt98qtc7x0FejPTnnzDcdEpNFH881L0lg1QxcCqjiyLqxQRfQaUF
SBlwn73DrTxz5Ky6hyrhbpBUMt5Fd0T3M+nbBJkop0XXFTVVXwhrfd8rKKhER9vH
xy2mIRYyCegRCGcyieazveqS7vw4SHy+fEOzbrp8PCLOJoT1HJc5qH4SdXraYdyJ
n7QfWs2siaVMWpwNebxqtkgofdSsxWNqpfrfj1FTs506kAgI+q9x9s/jT5mXdiZF
d24deiiFDMG2JUGVPTJdiIXQ+sbYNDwyf+EU8XNelHIcXEq84YYPDZ4D/yjwnpi5
7cTcmdXhZrMUEKKjdvuogLZ37U7AX6yyD5K8i4MJ+VHWGNKdg+cNzJaSmfFXjuDc
/gSCTy/DR97s5p1BrVr4ypDra3ZstbjTh8QPDD5EfecJ0GJchRrCIVyGP8UTX7Iq
U+3ycDLFI7X9+JHpkPN+AEyknaQ4TMmzFzF97VbVUC69j34sj08Sff6dov6xtnLC
DiQC+u2fjOPjp4I4hQqip2+/3pUCFKNCJbO4jZnSmUln2xAQTqsdDhHjZqA8AdRJ
1e64hjzkVKDzIsVh0eDF64dGJDAK+J2hpC2xZ5f9PBEqjaxGNnV3TesB3PwunjPS
H0DZwqtpayBef79l2Ir9GA==
=X9C8
-----END PGP PUBLIC KEY BLOCK-----
"""


def send_mail_with_backend(
        subject, body, from_email, recipient_list, html_message=None,
        fail_silently=False, auth_user=None, auth_password=None,
        attachments=None, alternatives=None, connection=None, headers=None,
        do_not_encrypt_this_message=False):
    connection = connection or mail.get_connection(
        username=auth_user, password=auth_password,
        fail_silently=fail_silently,
    )
    message = mail.EmailMultiAlternatives(
        subject, body, from_email, recipient_list, attachments=attachments,
        connection=connection, headers=headers)

    if html_message:
        message.attach_alternative(html_message, 'text/html')

    for alternative, mimetype in alternatives or []:
        message.attach_alternative(alternative, mimetype)

    if do_not_encrypt_this_message:
        message.do_not_encrypt_this_message = True

    return message.send()


class GPGMixin(object):
    @classmethod
    def setUpClass(cls):
        cls.gpg = get_gpg()
        super(GPGMixin, cls).setUpClass()


class KeyMixin(GPGMixin):
    @classmethod
    def setUpClass(cls):
        super(KeyMixin, cls).setUpClass()
        # Import the public key through the Key model
        cls.key = Key.objects.create(key=TEST_PUBLIC_KEY,
                                     use_asc=cls.use_asc)
        cls.address = cls.key.address_set.first()

    @classmethod
    def tearDownClass(cls):
        for address in cls.key.address_set.all():
            address.delete()
        cls.key.delete()
        super(KeyMixin, cls).tearDownClass()


class DeleteAllKeysMixin(GPGMixin):
    def delete_all_keys(self):
        self.gpg.delete_keys([k['fingerprint'] for k in self.gpg.list_keys()],
                             True)
        self.gpg.delete_keys([k['fingerprint'] for k in self.gpg.list_keys()])


class SendMailFunctionMixin(GPGMixin):
    send_mail_function = None

    def send_mail(self, *args, **kwargs):
        if hasattr(self.send_mail_function, '__call__'):
            # Allow functions assigned directly
            send_mail_actual_function = self.send_mail_function
        else:
            # Import a function from its dotted path
            mod, _, function = self.send_mail_function.rpartition('.')
            try:
                # Python 3.4+
                from importlib import import_module
            except ImportError:
                # Python < 3.4
                # From http://stackoverflow.com/a/8255024/6461688
                mod = __import__(mod, globals(), locals(), [function])
            else:
                mod = import_module(mod)
            send_mail_actual_function = getattr(mod, function)

        return send_mail_actual_function(*args, **kwargs)


class SendMailMixin(KeyMixin, SendMailFunctionMixin):
    def test_send_mail_key_validation_fail_raises_exception(self):
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        from email_extras import utils
        previous_value = utils.encrypt_kwargs['always_trust']
        utils.encrypt_kwargs['always_trust'] = False
        with self.assertRaises(EncryptionFailedError):
            self.send_mail(
                msg_subject, msg_text, from_email, to,
                html_message=mark_safe(msg_html))
        utils.encrypt_kwargs['always_trust'] = previous_value

    def test_send_mail_function_txt_message(self):
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"

        self.send_mail(msg_subject, msg_text, from_email, to)

        message = mail.outbox[0]

        self.assertEquals(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext
        self.assertNotEquals(message.body, "")
        self.assertNotEquals(message.body, msg_text)
        self.assertEquals(message.to, to)
        self.assertEquals(message.from_email, from_email)
        self.assertEquals(message.alternatives, [])
        self.assertEquals(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEquals(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test it against the cleartext
        self.assertEquals(str(self.gpg.decrypt(message.body)),
                          msg_text)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, True)

        self.assertEquals(str(delete_result), 'ok')

    def test_send_mail_function_txt_message_with_unencrypted_recipients(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com', 'unencrypted@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"

        self.send_mail(msg_subject, msg_text, from_email, to)

        # Grab the unencrypted message
        message = next((msg for msg in mail.outbox if to[1] in msg.to), None)

        self.assertEquals(message.subject, msg_subject)
        self.assertEquals(message.body, msg_text)
        self.assertEquals(message.to, [to[1]])
        self.assertEquals(message.from_email, from_email)
        self.assertEquals(message.alternatives, [])
        self.assertEquals(message.attachments, [])

        # Grab the encrypted message
        message = next((msg for msg in mail.outbox if to[0] in msg.to), None)

        self.assertEquals(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext
        self.assertNotEquals(message.body, "")
        self.assertNotEquals(message.body, msg_text)
        self.assertEquals(message.to, [to[0]])
        self.assertEquals(message.from_email, from_email)
        self.assertEquals(message.alternatives, [])
        self.assertEquals(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEquals(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test it against the cleartext
        self.assertEquals(str(self.gpg.decrypt(message.body)),
                          msg_text)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, True)

        self.assertEquals(str(delete_result), 'ok')

    def test_send_mail_function_txt_message_with_unencrypted_recipients_with_attachment_from_filename(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com', 'unencrypted@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            attachments=[('file.txt', msg_html, 'text/html')])

        # Grab the unencrypted message
        message = next((msg for msg in mail.outbox if to[1] in msg.to), None)

        self.assertEquals(message.subject, msg_subject)
        self.assertEquals(message.body, msg_text)
        self.assertEquals(message.to, [to[1]])
        self.assertEquals(message.from_email, from_email)
        self.assertEquals(message.alternatives, [])
        self.assertNotEquals(message.attachments, [])

        # We should only have one attachment - the HTML message
        self.assertEquals(len(message.attachments), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        filename, content, mimetype = message.attachments[0]
        self.assertEquals(filename, 'file.txt')
        self.assertEquals(mimetype, "text/html")
        self.assertEquals(content, msg_html)

        # Grab the encrypted message
        message = next((msg for msg in mail.outbox if to[0] in msg.to), None)

        self.assertEquals(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext
        self.assertNotEquals(message.body, "")
        self.assertNotEquals(message.body, msg_text)
        self.assertEquals(message.to, [to[0]])
        self.assertEquals(message.from_email, from_email)
        self.assertEquals(message.alternatives, [])
        self.assertNotEquals(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEquals(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test it against the cleartext
        self.assertEquals(str(self.gpg.decrypt(message.body)),
                          msg_text)

        # We should only have one attachment - the HTML message
        self.assertEquals(len(message.attachments), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        filename, content, mimetype = message.attachments[0]
        self.assertEquals(
            filename, 'file.txt{}'.format('.asc' if self.use_asc else ''))
        self.assertEquals(mimetype, "application/gpg-encrypted")
        self.assertEquals(str(self.gpg.decrypt(content)), msg_html)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, True)

        self.assertEquals(str(delete_result), 'ok')

    def test_send_mail_function_html_message(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            html_message=mark_safe(msg_html))

        message = mail.outbox[0]

        self.assertEquals(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext so we fail quickly
        self.assertNotEquals(message.body, "")
        self.assertNotEquals(message.body, msg_text)
        self.assertEquals(message.to, to)
        self.assertEquals(message.from_email, from_email)
        # Decrypt and test the alternatives later, just ensure we have
        # any alternatives at all so we fail quickly
        self.assertNotEquals(message.alternatives, [])
        self.assertEquals(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEquals(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test the message body against the cleartext
        self.assertEquals(str(self.gpg.decrypt(message.body)), msg_text)

        # We should only have one alternative - the HTML message
        self.assertEquals(len(message.alternatives), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        alt, mimetype = message.alternatives[0]
        self.assertEquals(mimetype, "application/gpg-encrypted")
        self.assertEquals(str(self.gpg.decrypt(alt)), msg_html)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, True)

        self.assertEquals(str(delete_result), 'ok')

    def test_send_mail_function_html_message_attachment(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            attachments=[(None, msg_html, 'text/html')])

        message = mail.outbox[0]

        self.assertEquals(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext so we fail quickly
        self.assertNotEquals(message.body, "")
        self.assertNotEquals(message.body, msg_text)
        self.assertEquals(message.to, to)
        self.assertEquals(message.from_email, from_email)
        # Decrypt and test the alternatives later, just ensure we have
        # any alternatives at all so we fail quickly
        self.assertEquals(message.alternatives, [])
        self.assertNotEquals(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEquals(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test the message body against the cleartext
        self.assertEquals(str(self.gpg.decrypt(message.body)), msg_text)

        # We should only have one attachment - the HTML message
        self.assertEquals(len(message.attachments), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        filename, content, mimetype = message.attachments[0]
        self.assertEquals(filename, None)
        self.assertEquals(mimetype, "application/gpg-encrypted")
        self.assertEquals(str(self.gpg.decrypt(content)), msg_html)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, True)

        self.assertEquals(str(delete_result), 'ok')

    def test_send_mail_function_html_message_attachment_from_filename(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            attachments=[('file.txt', msg_html, 'text/html')])

        message = mail.outbox[0]

        self.assertEquals(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext so we fail quickly
        self.assertNotEquals(message.body, "")
        self.assertNotEquals(message.body, msg_text)
        self.assertEquals(message.to, to)
        self.assertEquals(message.from_email, from_email)
        # Decrypt and test the alternatives later, just ensure we have
        # any alternatives at all so we fail quickly
        self.assertEquals(message.alternatives, [])
        self.assertNotEquals(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEquals(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test the message body against the cleartext
        self.assertEquals(str(self.gpg.decrypt(message.body)), msg_text)

        # We should only have one attachment - the HTML message
        self.assertEquals(len(message.attachments), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        filename, content, mimetype = message.attachments[0]
        self.assertEquals(
            filename, 'file.txt{}'.format('.asc' if self.use_asc else ''))
        self.assertEquals(mimetype, "application/gpg-encrypted")
        self.assertEquals(str(self.gpg.decrypt(content)), msg_html)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, True)

        self.assertEquals(str(delete_result), 'ok')

    def test_send_mail_function_html_message_encrypted_attachment(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            attachments=[(None, msg_html, 'application/gpg-encrypted')])

        message = mail.outbox[0]

        # We should only have one attachment - the HTML message
        self.assertEquals(len(message.attachments), 1)

        # Check the content to make sure it wasn't encrypted
        filename, content, mimetype = message.attachments[0]
        self.assertEquals(filename, None)
        self.assertEquals(mimetype, "application/gpg-encrypted")
        self.assertEquals(content, msg_html)

    def test_send_mail_function_html_message_attachment_from_file(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-email-extras@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            attachments=['tests/templates/email_extras/dr_suess.html'])

        message = mail.outbox[0]

        self.assertEquals(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext so we fail quickly
        self.assertNotEquals(message.body, "")
        self.assertNotEquals(message.body, msg_text)
        self.assertEquals(message.to, to)
        self.assertEquals(message.from_email, from_email)
        # Decrypt and test the alternatives later, just ensure we have
        # any alternatives at all so we fail quickly
        self.assertEquals(message.alternatives, [])
        self.assertNotEquals(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEquals(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test the message body against the cleartext
        self.assertEquals(str(self.gpg.decrypt(message.body)), msg_text)

        # We should only have one attachment - the HTML message
        self.assertEquals(len(message.attachments), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        filename, content, mimetype = message.attachments[0]
        self.assertEquals(
            filename, 'dr_suess.html{}'.format('.asc' if self.use_asc else ''))
        self.assertEquals(mimetype, "application/gpg-encrypted")
        with open("tests/templates/email_extras/dr_suess.html", 'r') as f:
            self.assertEquals(str(self.gpg.decrypt(content)), f.read())

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, True)

        self.assertEquals(str(delete_result), 'ok')
