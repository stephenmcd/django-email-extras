from tempfile import NamedTemporaryFile
import webbrowser

from .settings import ACTUAL_DEBUG_BACKEND, DEBUG

mod, _, backend = ACTUAL_DEBUG_BACKEND.rpartition('.')
try:
    # Python 3.4+
    from importlib import import_module
except ImportError:
    # Python < 3.4
    # From http://stackoverflow.com/a/8255024/6461688
    mod = __import__(mod, globals(), locals(), [backend])
else:
    mod = import_module(mod)
ActualBackend = getattr(mod, backend)


class BrowsableEmailBackend(ActualBackend):
    """
    An email backend that opens HTML parts of emails sent
    in a local web browser, for testing during development.
    """

    def send_messages(self, email_messages):
        if not DEBUG:
            # Should never be used in production.
            return
        for message in email_messages:
            for body, content_type in getattr(message, "alternatives", []):
                if content_type == "text/html":
                    self.open(body)

        super(BrowsableEmailBackend, self).send_messages(email_messages)

    def open(self, body=None):
        if body is None:
            return super(BrowsableEmailBackend, self).open()

        with NamedTemporaryFile(delete=False) as temp:
            temp.write(body.encode('utf-8'))

        webbrowser.open("file://" + temp.name)
