
from email_extras.settings import USE_GNUPG


if USE_GNUPG:
    from django.contrib import admin
    from email_extras.models import Key, Address
    from email_extras.forms import KeyForm

    class KeyAdmin(admin.ModelAdmin):
        form = KeyForm

    admin.site.register(Key, KeyAdmin)
    admin.site.register(Address)
