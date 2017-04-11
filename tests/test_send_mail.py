from django.conf import settings
from django.core import mail
from django.template import loader
from django.test import TestCase, override_settings

from email_extras.utils import send_mail_template

from tests.utils import SendMailMixin


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SendMailFunctionNoASCTestCase(SendMailMixin, TestCase):
    use_asc = False
    maxDiff = 10000
    send_mail_function = 'email_extras.utils.send_mail'


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SendMailFunctionWithASCTestCase(SendMailMixin, TestCase):
    use_asc = True
    maxDiff = 10000
    send_mail_function = 'email_extras.utils.send_mail'

    def test_send_mail_function_single_recipient(self):
        msg_subject = "Test Subject"
        to = 'django-email-extras@example.com'
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"

        self.send_mail(msg_subject, msg_text, from_email, to)

        message = mail.outbox[0]

        self.assertEquals(message.to, [to])


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SendMailTemplateTestCase(TestCase):
    # We don't need to test our send_mail function here
    send_mail_function = 'django.core.mail.send_mail'

    def test_with_context(self):
        subject = "Dr. Suess Says"
        template = "dr_suess"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = ['unencrypted@example.com']
        context = {
            'last_fish': 'blue fish',
        }

        send_mail_template(subject, template, from_email, to, context=context)

        message = mail.outbox[0]

        self.assertEquals(message.subject, subject)
        self.assertEquals(
            message.body,
            loader.get_template("email_extras/%s.%s" % (template, 'txt'))
            .render(context))

        self.assertEquals(message.alternatives[0][1], 'text/html')
        self.assertEquals(
            message.alternatives[0][0],
            loader.get_template("email_extras/%s.%s" % (template, 'html'))
            .render(context))

    def test_without_context(self):
        subject = "Dr. Suess Says"
        template = "dr_suess"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = ['unencrypted@example.com']

        send_mail_template(subject, template, from_email, to)

        message = mail.outbox[0]

        self.assertEquals(message.subject, subject)
        self.assertEquals(
            message.body,
            loader.get_template("email_extras/%s.%s" % (template, 'txt'))
            .render({}))

        self.assertEquals(message.alternatives[0][1], 'text/html')
        self.assertEquals(
            message.alternatives[0][0],
            loader.get_template("email_extras/%s.%s" % (template, 'html'))
            .render({}))
