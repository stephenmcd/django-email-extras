from __future__ import with_statement

from os.path import basename
from tempfile import NamedTemporaryFile
import webbrowser

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleBackend
from django.core.mail.backends.locmem import EmailBackend as LocmemBackend
from django.core.mail.backends.filebased import EmailBackend as FileBackend
from django.core.mail.backends.smtp import EmailBackend as SmtpBackend
from django.core.mail.message import EmailMultiAlternatives
from django.utils.encoding import smart_text

from .handlers import (handle_failed_message_encryption,
                       handle_failed_alternative_encryption,
                       handle_failed_attachment_encryption)
from .settings import (GNUPG_HOME, GNUPG_ENCODING, USE_GNUPG)
from .utils import (EncryptionFailedError, encrypt_kwargs)


class BrowsableEmailBackend(BaseEmailBackend):
    """
    An email backend that opens HTML parts of emails sent
    in a local web browser, for testing during development.
    """

    def send_messages(self, email_messages):
        if not settings.DEBUG:
            # Should never be used in production.
            return
        for message in email_messages:
            for body, content_type in getattr(message, "alternatives", []):
                if content_type == "text/html":
                    self.open(body)

    def open(self, body):
        with NamedTemporaryFile(delete=False) as temp:
            temp.write(body.encode('utf-8'))

        webbrowser.open("file://" + temp.name)


if USE_GNUPG:
    from gnupg import GPG

    from .models import Address

    # Create the GPG object
    gpg = GPG(gnupghome=GNUPG_HOME)
    if GNUPG_ENCODING is not None:
        gpg.encoding = GNUPG_ENCODING

    def copy_message(msg):
        return EmailMultiAlternatives(
            to=msg.to,
            cc=msg.cc,
            bcc=msg.bcc,
            reply_to=msg.reply_to,
            from_email=msg.from_email,
            subject=msg.subject,
            body=msg.body,
            attachments=msg.attachments,
            headers=msg.extra_headers,
            connection=msg.connection)

    def encrypt(text, addr):
        encryption_result = gpg.encrypt(text, addr, **encrypt_kwargs)
        if not encryption_result.ok:
            raise EncryptionFailedError("Encrypting mail to %s failed: '%s'",
                                        addr, encryption_result.status)
        if smart_text(encryption_result) == "" and text != "":
            raise EncryptionFailedError("Encrypting mail to %s failed.",
                                        addr)
        return smart_text(encryption_result)

    def encrypt_attachment(address, attachment, use_asc):
        # Attachments can either just be filenames or a
        # (filename, content, mimetype) triple
        if not hasattr(attachment, "__iter__"):
            filename = basename(attachment)
            mimetype = None

            # If the attachment is just a filename, open the file,
            # encrypt it, and attach it
            with open(attachment, "rb") as f:
                content = f.read()
        else:
            # Unpack attachment tuple
            filename, content, mimetype = attachment

        # Ignore attachments if they're already encrypted
        if mimetype == "application/gpg-encrypted":
            return attachment

        try:
            encrypted_content = encrypt(content, address)
        except EncryptionFailedError as e:
            # This function will need to decide what to do. Possibilities include
            # one or more of:
            #
            # * Mail admins (possibly without encrypting the message to them)
            # * Remove the offending key automatically
            # * Set the body to a blank string
            # * Set the body to the cleartext
            # * Set the body to the cleartext, with a warning message prepended
            # * Set the body to a custom error string
            # * Reraise the exception
            #
            # However, the behavior will be very site-specific, because each site
            # will have different attackers, different threat profiles, different
            # compliance requirements, and different policies.
            #
            handle_failed_attachment_encryption(e)
        else:
            if use_asc and filename is not None:
                filename += ".asc"

        return (filename, encrypted_content, "application/gpg-encrypted")

    def encrypt_messages(email_messages):
        unencrypted_messages = []
        encrypted_messages = []
        for msg in email_messages:
            # Copied out of utils.py
            # Obtain a list of the recipients that have GPG keys installed
            key_addrs = dict(Address.objects.filter(address__in=msg.to)
                                            .values_list('address', 'use_asc'))

            # Encrypt emails - encrypted emails need to be sent individually,
            # while non-encrypted emails can be sent in one send. So we split
            # up each message into 1 or more parts: the unencrypted message
            # that is addressed to everybody who doesn't have a key, and a
            # separate message for people who do have keys.
            unencrypted_msg = copy_message(msg)
            unencrypted_msg.to = [addr for addr in msg.to
                                  if addr not in key_addrs]
            if unencrypted_msg.to:
                unencrypted_messages.append(unencrypted_msg)

            # Make a new message object for each recipient with a key
            new_msg = copy_message(msg)

            # Encrypt the message body and all attachments for all addresses
            # we have keys for
            for address, use_asc in key_addrs.items():
                if getattr(msg, 'do_not_encrypt_this_message', False):
                    unencrypted_messages.append(new_msg)
                    continue

                # Replace the message body with the encrypted message body
                try:
                    new_msg.body = encrypt(new_msg.body, address)
                except EncryptionFailedError as e:
                    handle_failed_message_encryption(e)

                # If the message has alternatives, encrypt them all
                alternatives = []
                for alt, mimetype in getattr(new_msg, 'alternatives', []):
                    # Ignore alternatives if they're already encrypted
                    if mimetype == "application/gpg-encrypted":
                        alternatives.append((alt, mimetype))
                        continue

                    try:
                        encrypted_alternative = encrypt(alt, address)
                    except EncryptionFailedError as e:
                        handle_failed_alternative_encryption(e)
                    else:
                        alternatives.append((encrypted_alternative,
                                             "application/gpg-encrypted"))
                # Replace all of the alternatives
                new_msg.alternatives = alternatives

                # Replace all unencrypted attachments with their encrypted
                # versions
                attachments = []
                for attachment in new_msg.attachments:
                    attachments.append(
                        encrypt_attachment(address, attachment, use_asc))
                new_msg.attachments = attachments

                encrypted_messages.append(new_msg)

        return unencrypted_messages + encrypted_messages

    class EncryptingEmailBackendMixin(object):
        def send_messages(self, email_messages):
            if USE_GNUPG:
                email_messages = encrypt_messages(email_messages)
            super(EncryptingEmailBackendMixin, self)\
                .send_messages(email_messages)

    class EncryptingConsoleEmailBackend(EncryptingEmailBackendMixin,
                                        ConsoleBackend):
        pass

    class EncryptingLocmemEmailBackend(EncryptingEmailBackendMixin,
                                       LocmemBackend):
        pass

    class EncryptingFilebasedEmailBackend(EncryptingEmailBackendMixin,
                                          FileBackend):
        pass

    class EncryptingSmtpEmailBackend(EncryptingEmailBackendMixin,
                                     SmtpBackend):
        pass
