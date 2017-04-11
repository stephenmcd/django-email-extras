from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.test import TestCase

from email_extras.handlers import (
    force_delete_key, force_mail_admins, force_send_message,
    get_variable_from_exception,
)

from tests.utils import KeyMixin


class GetVariableFromExceptionTestCase(TestCase):
    def test_get_variable_from_parent(self):
        def child():
            child_var = 2  # noqa: F841
            raise Exception()

        def parent():
            parent_var = 1  # noqa: F841

            child()

        try:
            parent()
        except Exception as e:
            self.assertEquals(get_variable_from_exception(e, 'parent_var'), 1)
        else:
            self.assertTrue(False, "handler() didn't raise an exception")

    def test_get_variable_from_child(self):
        def child():
            child_var = 2  # noqa: F841
            raise Exception()

        def parent():
            parent_var = 1  # noqa: F841

            child()

        try:
            parent()
        except Exception as e:
            self.assertEquals(get_variable_from_exception(e, 'child_var'), 2)
        else:
            self.assertTrue(False, "handler() didn't raise an exception")

    def test_raise_key_error(self):
        def child():
            child_var = 2  # noqa: F841
            raise Exception()

        def parent():
            parent_var = 1  # noqa: F841

            child()

        with self.assertRaises(KeyError):
            try:
                parent()
            except Exception as e:
                get_variable_from_exception(e, 'grandchild_var')
            else:
                self.assertTrue(False, "handler() didn't raise an exception")


class ForceDeleteKeyTestCase(KeyMixin, TestCase):
    use_asc = False

    def test_key_deletion(self):
        self.assertGreater(len(self.gpg.list_keys()), 0)

        force_delete_key(self.address)

        self.assertEquals(len(self.gpg.list_keys()), 0)


class ForceMailAdminsTestCase(TestCase):
    def test_force_mail_admins_from_trying_to_mail_admin(self):
        sent = {'sent': False}

        message = EmailMultiAlternatives(
            "Subject", "Body", "sender@example.com",
            [admin[1] for admin in settings.ADMINS])

        def fake_send():
            # It's eaiser to use nonlocal here, but we support Python 2.7
            # nonlocal sent
            sent['sent'] = True

        setattr(message, 'send', fake_send)

        self.assertFalse(sent['sent'])

        force_mail_admins(message, settings.ADMINS[0][1])

        self.assertTrue(sent['sent'])

    def test_force_mail_admins_from_trying_to_mail_nonadmins(self):
        sent = {'sent': False}

        message = EmailMultiAlternatives(
            "Subject", "Body", "sender@example.com", ["recipient@example.com"])

        def fake_mail_admins(subject, body):
            # It's eaiser to use nonlocal here, but we support Python 2.7
            # nonlocal sent
            sent['sent'] = True

        from email_extras import handlers
        previous_mail_admins = handlers.mail_admins
        handlers.mail_admins = fake_mail_admins

        self.assertFalse(sent['sent'])

        force_mail_admins(message, "recipient@example.com")

        self.assertTrue(sent['sent'])

        handlers.mail_admins = previous_mail_admins


class ForceSendMessageTestCase(TestCase):
    def test_sent_message(self):
        sent = {'sent': False}

        message = EmailMultiAlternatives(
            "Subject", "Body", "sender@example.com", ["recipient@example.com"])

        def fake_send():
            # It's eaiser to use nonlocal here, but we support Python 2.7
            # nonlocal sent
            sent['sent'] = True

        setattr(message, 'send', fake_send)

        self.assertFalse(sent['sent'])

        force_send_message(message)

        self.assertTrue(sent['sent'])
