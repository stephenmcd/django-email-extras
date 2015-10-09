from __future__ import with_statement
from os.path import basename

from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from django.utils import six
from django.utils.encoding import smart_text

from email_extras.settings import USE_GNUPG, GNUPG_HOME, ALWAYS_TRUST


if USE_GNUPG:
    from gnupg import GPG


def addresses_for_key(gpg, key):
    """
    Takes a key and extracts the email addresses for it.
    """
    fingerprint = key["fingerprint"]
    addresses = []
    for key in gpg.list_keys():
        if key["fingerprint"] == fingerprint:
            addresses.extend([address.split("<")[-1].strip(">")
                              for address in key["uids"] if address])
    return addresses


def send_mail(subject, body_text, addr_from, addr_to, fail_silently=False,
              attachments=None, body_html=None, connection=None,
              headers=None):
    """
    Sends a multipart email containing text and html versions which
    are encrypted for each recipient that has a valid gpg key
    installed.
    """

    # Allow for a single address to be passed in.
    if isinstance(addr_to, six.string_types):
        addr_to = [addr_to]

    # Obtain a list of the recipients that have gpg keys installed.
    key_addresses = {}
    if USE_GNUPG:
        from email_extras.models import Address
        for address in Address.objects.filter(address__in=addr_to):
            key_addresses[address.address] = address.use_asc
        # Create the gpg object.
        if key_addresses:
            gpg = GPG(gnupghome=GNUPG_HOME)

    # Encrypts body if recipient has a gpg key installed.
    def encrypt_if_key(body, addr_list):
        if addr_list[0] in key_addresses:
            encrypted = gpg.encrypt(body, addr_list[0],
                                    always_trust=ALWAYS_TRUST)
            return smart_text(encrypted)
        return body

    # Load attachments and create name/data tuples.
    attachments_parts = []
    if attachments is not None:
        for attachment in attachments:
            # Attachments can be pairs of name/data, or filesystem paths.
            if not hasattr(attachment, "__iter__"):
                with open(attachment, "rb") as f:
                    attachments_parts.append((basename(attachment), f.read()))
            else:
                attachments_parts.append(attachment)

    # Send emails - encrypted emails needs to be sent individually, while
    # non-encrypted emails can be sent in one send. So the final list of
    # lists of addresses to send to looks like:
    # [[unencrypted1, unencrypted2, unencrypted3], [encrypted1], [encrypted2]]
    unencrypted = [[addr for addr in addr_to if addr not in key_addresses]]
    encrypted = [[addr] for addr in key_addresses]
    for addr_list in unencrypted + encrypted:
        msg = EmailMultiAlternatives(subject,
                                     encrypt_if_key(body_text, addr_list),
                                     addr_from, addr_list,
                                     connection=connection, headers=headers)
        if body_html is not None:
            msg.attach_alternative(encrypt_if_key(body_html, addr_list),
                                   "text/html")
        for parts in attachments_parts:
            name = parts[0]
            if key_addresses.get(addr_list[0]):
                name += ".asc"
            msg.attach(name, encrypt_if_key(parts[1], addr_list))
        msg.send(fail_silently=fail_silently)


def send_mail_template(subject, template, addr_from, addr_to,
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

    send_mail(subject, render("txt"), addr_from, addr_to,
              fail_silently=fail_silently, attachments=attachments,
              body_html=render("html"), connection=connection,
              headers=headers)
