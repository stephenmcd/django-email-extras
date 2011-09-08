
from django.contrib import admin
from django import forms

from email_extras.settings import USE_GNUPG, GNUPG_HOME


if USE_GNUPG:
    from gnupg import GPG
    from email_extras.models import Key, Address
    from email_extras.utils import addresses_for_key

    class KeyAdmin(admin.ModelAdmin):

        def save_model(self, request, obj, form, change):
            """
            Import the key and parse the addresses from it and save
            them, and omit the super save_model call so as to never
            save the key instance.
            """
            gpg = GPG(gnupghome=GNUPG_HOME)
            result = gpg.import_keys(obj.key)
            if result.count == 0:
                raise forms.ValidationError("Invalid Key")
            else:
                addresses = []
                for key in result.results:
                    addresses.extend(addresses_for_key(gpg, key))
                obj.addresses = ",".join(addresses)
                for address in addresses:
                    Address.objects.get_or_create(address=address)

    admin.site.register(Key, KeyAdmin)
    admin.site.register(Address)
