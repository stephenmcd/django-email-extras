Introduction
============

django-email-extras is a Django reusable app providing the
ability to send PGP encrypted and multipart emails using
Django templates. These features can be used together or
separately. When configured to send PGP encrypted email,
the ability for Admin users to manage PGP keys is also
provided.

Dependencies
============

  * `python-gnupg <http://code.google.com/p/python-gnupg/>`_ is
    required for sending PGP encrypted email.

Installation
============

Checkout the source and run ``python setup.py install``. You can
then add ``email_extras`` to your ``INSTALLED_APPS``.

How It Works
============

There are two functions for sending email in the ``email_extras.utils``
module:

  * ``send_mail``
  * ``send_mail_template``

The former mimics the signature of ``django.core.mail.send_mail``
while the latter provides the ability to send multipart emails
using the Django templating system. If configured correctly, both
these functions will PGP encrypt emails as described below.

Sending PGP Encrypted Email
---------------------------

`PGP explanation <http://en.wikipedia.org/wiki/Pretty_Good_Privacy>`_

Using `python-gnupg <http://code.google.com/p/python-gnupg/>`_, two
models are defined in ``email_extras.models`` - ``Key`` and ``Address``
which represent a PGP key and an email address for a successfully
imported key. These models exist purely for the sake of importing
keys and removing keys for a particular address via the Django
Admin.

When adding a key, the key is imported into the key ring on
the server and the instance of the ``Key`` model is not saved. The
email address for the key is also extracted and saved as an
``Address`` instance.

The ``Address`` model is then used when sending email to check for
an existing key to determine whether an email should be encrypted.
When an ``Address`` is deleted via the Django Admin, the key is
removed from the key ring on the server.

Sending Multipart Email with Django Templates
---------------------------------------------

As mentioned above, the following function is provided in
the ``email_extras.utils`` module::

  send_mail_template(subject, template, addr_from, addr_to, fail_silently=False, attachments=None, context=None)

The arguments that differ from ``django.core.mail.send_mail`` are
``template`` and ``context``. The ``template`` argument is simply
the name of the template to be used for rendering the email contents.

A template consists of both a HTML file and a TXT file each responsible
for their respective versions of the email and should be stored in
the ``email_extras`` directory where your templates are stored,
therefore if the name ``contact_form`` was given for the ``template``
argument, the two template files for the email would be:

  * ``templates/email_extras/contact_form.html``
  * ``templates/email_extras/contact_form.txt``

The ``context`` argument is simply a dictionary that is used to
populate the email templates, much like a normal request context
would be used for a regular Django template.

Configuration
=============

There are two settings you can configure in your project's
``settings`` module:

  * ``EMAIL_EXTRAS_USE_GNUPG`` - Boolean that controls whether the PGP
    encryption features are used. Defaults to ``True`` if
    ``EMAIL_EXTRAS_GNUPG_HOME`` is specified, otherwise ``False``.
  * ``EMAIL_EXTRAS_GNUPG_HOME`` - String representing a custom location
    for the GNUPG keyring.
  * ``EMAIL_EXTRAS_ALWAYS_TRUST_KEYS`` - Skip key validation and assume
    that used keys are always fully trusted.
