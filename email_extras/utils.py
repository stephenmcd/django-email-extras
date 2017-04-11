from __future__ import with_statement

from os.path import basename
from warnings import warn

from django import VERSION
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils import six
from django.utils.encoding import smart_text

from email_extras.settings import (ALWAYS_TRUST, GNUPG_ENCODING, GNUPG_HOME,
                                   USE_GNUPG, SIGNING_KEY_FINGERPRINT)

# Contexts are just vanilla Python dictionaries in Django 1.9+
if VERSION >= (1, 9):
    Context = dict  # noqa: F811


if USE_GNUPG:
    from gnupg import GPG

    def get_gpg():
        gpg = GPG(gnupghome=GNUPG_HOME)
        if GNUPG_ENCODING is not None:
            gpg.encoding = GNUPG_ENCODING
        return gpg

# Used internally
encrypt_kwargs = {
    'always_trust': ALWAYS_TRUST,
    'sign': SIGNING_KEY_FINGERPRINT,
}


class EncryptionFailedError(Exception):
    pass


class BadSigningKeyError(KeyError):
    pass


def check_signing_key():
    if USE_GNUPG and SIGNING_KEY_FINGERPRINT is not None:
        gpg = get_gpg()
        try:
            gpg.list_keys(True).key_map[SIGNING_KEY_FINGERPRINT]
        except KeyError:
            raise BadSigningKeyError(
                "The key specified by the "
                "EMAIL_EXTRAS_SIGNING_KEY_FINGERPRINT setting "
                "({fp}) does not exist in the GPG keyring. Adjust the "
                "EMAIL_EXTRAS_GNUPG_HOME setting (currently set to "
                "{gnupg_home}, correct the key fingerprint, or generate a new "
                "key by running python manage.py email_signing_key --generate "
                "to fix.".format(
                    fp=SIGNING_KEY_FINGERPRINT,
                    gnupg_home=GNUPG_HOME))


def addresses_for_key(gpg, key):
    """
    Takes a key and extracts the email addresses for it.
    """
    return [address.split("<")[-1].strip(">")
            for address in gpg.list_keys().key_map[key['fingerprint']]["uids"]
            if address]


def send_mail(subject, body_text, addr_from, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              attachments=None, body_html=None, html_message=None,
              connection=None, headers=None):
    """
    Sends a multipart email containing text and html versions which
    are encrypted for each recipient that has a valid gpg key
    installed.
    """

    # Make sure only one HTML option is specified
    if body_html is not None and html_message is not None:  # pragma: no cover
        raise ValueError("You cannot specify body_html and html_message at "
                         "the same time. Please only use html_message.")

    # Push users to update their code
    if body_html is not None:  # pragma: no cover
        warn("Using body_html is deprecated; use the html_message argument "
             "instead. Please update your code.", DeprecationWarning)
        html_message = body_html

    # Allow for a single address to be passed in.
    if isinstance(recipient_list, six.string_types):
        recipient_list = [recipient_list]

    connection = connection or get_connection(
        username=auth_user, password=auth_password,
        fail_silently=fail_silently)

    # Obtain a list of the recipients that have gpg keys installed.
    key_addresses = {}
    if USE_GNUPG:
        from email_extras.models import Address
        key_addresses = dict(Address.objects.filter(address__in=recipient_list)
                                            .values_list('address', 'use_asc'))
        # Create the gpg object.
        if key_addresses:
            gpg = get_gpg()

    # Check if recipient has a gpg key installed
    def has_pgp_key(addr):
        return addr in key_addresses

    # Encrypts body if recipient has a gpg key installed.
    def encrypt_if_key(body, addr_list):
        if has_pgp_key(addr_list[0]):
            encrypted = gpg.encrypt(body, addr_list[0], **encrypt_kwargs)
            if not encrypted.ok or str(encrypted) == "" and body != "":
                # encryption failed
                raise EncryptionFailedError("Encrypting mail to %s failed: %s",
                                            addr_list[0], encrypted.stderr)
            return smart_text(encrypted)
        return body

    # Load attachments and create name/data tuples.
    attachments_parts = []
    if attachments is not None:
        for attachment in attachments:
            # Attachments can be pairs of name/data, or filesystem paths.
            if isinstance(attachment, six.string_types):
                with open(attachment, "rb") as f:
                    attachments_parts.append((basename(attachment), f.read()))
            else:
                attachments_parts.append(attachment)

    # Send emails - encrypted emails needs to be sent individually, while
    # non-encrypted emails can be sent in one send. So the final list of
    # lists of addresses to send to looks like:
    # [[unencrypted1, unencrypted2, unencrypted3], [encrypted1], [encrypted2]]
    unencrypted = [addr for addr in recipient_list
                   if addr not in key_addresses]
    unencrypted = [unencrypted] if unencrypted else unencrypted
    encrypted = [[addr] for addr in key_addresses]
    for addr_list in unencrypted + encrypted:
        msg = EmailMultiAlternatives(subject,
                                     encrypt_if_key(body_text, addr_list),
                                     addr_from, addr_list,
                                     connection=connection, headers=headers)
        if html_message is not None:
            if has_pgp_key(addr_list[0]):
                mimetype = "application/gpg-encrypted"
            else:
                mimetype = "text/html"
            msg.attach_alternative(encrypt_if_key(html_message, addr_list),
                                   mimetype)

        for parts in attachments_parts:
            name = parts[0]

            # Don't encrypt attachments twice
            if len(parts) > 2 and parts[2] == "application/gpg-encrypted":
                msg.attach(name, parts[1], parts[2])
                continue

            if has_pgp_key(addr_list[0]):
                # Name might be none if content was simply directly attached
                if key_addresses.get(addr_list[0]) and name is not None:
                    name += ".asc"
                mimetype = "application/gpg-encrypted"
            else:
                # If we aren't encrypting the message, then leave the mimetype
                # alone
                mimetype = parts[2] if len(parts) > 2 else None

            msg.attach(name, encrypt_if_key(parts[1], addr_list), mimetype)

        msg.send(fail_silently=fail_silently)


def send_mail_template(subject, template, addr_from, recipient_list,
                       fail_silently=False, attachments=None, context=None,
                       connection=None, headers=None):
    """
    Send email rendering text and html versions for the specified
    template name using the context dictionary passed in.
    """

    if context is None:
        context = {}

    # Loads a template passing in vars as context.
    def render(ext):
        name = "email_extras/%s.%s" % (template, ext)
        return loader.get_template(name).render(Context(context))

    send_mail(subject, render("txt"), addr_from, recipient_list,
              fail_silently=fail_silently, attachments=attachments,
              html_message=render("html"), connection=connection,
              headers=headers)
