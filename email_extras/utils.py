from __future__ import with_statement
from os.path import basename

from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives

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
    if not hasattr(addr_to, "__iter__"):
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
    def encrypt_if_key(body, addr):
        if addr in key_addresses:
            return unicode(gpg.encrypt(body, addr, always_trust=ALWAYS_TRUST))
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

    # Send emails.
    for addr in addr_to:
        msg = EmailMultiAlternatives(subject, encrypt_if_key(body_text, addr),
                                     addr_from, [addr], connection=connection,
                                     headers=headers)
        if body_html is not None:
            body_html = encrypt_if_key(body_html, addr)
            msg.attach_alternative(body_html, "text/html")
        for parts in attachments_parts:
            name = parts[0]
            if key_addresses.get(addr):
                name += ".asc"
            msg.attach(name, encrypt_if_key(parts[1], addr))
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
