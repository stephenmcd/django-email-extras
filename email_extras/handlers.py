from importlib import import_module
from inspect import trace

from django.conf import settings
from django.core.mail import mail_admins

from .models import Address
from .settings import FAILURE_HANDLERS


ADMIN_ADDRESSES = [admin[1] for admin in settings.ADMINS]


def get_variable_from_exception(exception, variable_name):
    """
    Grab the variable from closest frame in the stack
    """
    for frame in reversed(trace()):
        try:
            # From http://stackoverflow.com/a/9059407/6461688
            frame_variable = frame[0].f_locals[variable_name]
        except KeyError:
            pass
        else:
            return frame_variable
    else:
        raise KeyError("Variable '%s' not in any stack frames", variable_name)


def default_handle_failed_encryption(exception):
    """
    Handle failures when trying to encrypt alternative content for messages
    """
    raise exception


def default_handle_failed_alternative_encryption(exception):
    """
    Handle failures when trying to encrypt alternative content for messages
    """
    raise exception


def default_handle_failed_attachment_encryption(exception):
    """
    Handle failures when trying to encrypt alternative content for messages
    """
    raise exception


def force_mail_admins(unencrypted_message, address):
    """
    Mail admins when encryption fails, and send the message unencrypted if
    the recipient is an admin
    """

    if address in ADMIN_ADDRESSES:
        # We assume that it is more important to mail the admin *without*
        # encrypting the message
        force_send_message(unencrypted_message)
    else:
        mail_admins(
            "Failed encryption attempt",
            """
            There was a problem encrypting an email message.

            Subject: "{subject}"
            Address: "{address}"
            """)


def force_delete_key(address):
    """
    Delete the key from the keyring and the Key and Address objects from the
    database
    """
    address_object = Address.objects.get(address=address)
    address_object.key.delete()
    address_object.delete()


def force_send_message(unencrypted_message):
    """
    Send the message unencrypted
    """
    unencrypted_message.do_not_encrypt_this_message = True
    unencrypted_message.send()


def import_function(key):
    mod, _, function = FAILURE_HANDLERS[key].rpartition('.')
    mod = import_module(mod)
    return getattr(mod, function)

exception_handlers = {
    'message': 'handle_failed_message_encryption',
    'alternative': 'handle_failed_alternative_encryption',
    'attachment': 'handle_failed_attachment_encryption',
}

for key, value in exception_handlers.items():
    locals()[value] = import_function(key)
