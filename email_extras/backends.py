
from tempfile import NamedTemporaryFile
import webbrowser

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend


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
        temp = NamedTemporaryFile(delete=False)
        temp.write(body)
        temp.close()
        webbrowser.open("file://" + temp.name)
