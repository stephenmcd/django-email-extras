
from django import forms

from email_extras.settings import USE_GNUPG, GNUPG_HOME

if USE_GNUPG:
    from gnupg import GPG


class KeyForm(forms.ModelForm):

    def clean_key(self):
        """
        Validate the key contains an email address.
        """
        key = self.cleaned_data["key"]
        gpg = GPG(gnupghome=GNUPG_HOME)
        result = gpg.import_keys(key)
        if result.count == 0:
            raise forms.ValidationError("Invalid Key")
        return key

