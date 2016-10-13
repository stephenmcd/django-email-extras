
from email_extras.settings import USE_GNUPG


if USE_GNUPG:
    from django.contrib import admin
    from email_extras.models import Key, Address
    from email_extras.forms import KeyForm

    class KeyAdmin(admin.ModelAdmin):
        form = KeyForm

    class AddressAdmin(admin.ModelAdmin):
        def has_add_permission(self, request):
                return False

    admin.site.register(Key, KeyAdmin)
    admin.site.register(Address, AddressAdmin)
