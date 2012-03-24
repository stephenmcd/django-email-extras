
from django.db import models

from email_extras.settings import USE_GNUPG, GNUPG_HOME
from email_extras.utils import addresses_for_key


if USE_GNUPG:
    from gnupg import GPG

    class Key(models.Model):
        """
        Accepts a key and imports it via admin's save_model which
        omits saving.
        """

        key = models.TextField()
        addresses = models.TextField(editable=False)
        use_asc = models.BooleanField(default=False, help_text="If True, "
            "an '.asc' extension will be added to email attachments sent "
            "to the address for this key.")

        def __unicode__(self):
            return self.addresses

        def save(self, *args, **kwargs):
            super(Key, self).save(*args, **kwargs)
            gpg = GPG(gnupghome=GNUPG_HOME)
            result = gpg.import_keys(self.key)
            addresses = []
            for key in result.results:
                addresses.extend(addresses_for_key(gpg, key))
            self.addresses = ",".join(addresses)
            for address in addresses:
                address, _ = Address.objects.get_or_create(address=address)
                address.use_asc = self.use_asc
                address.save()


    class Address(models.Model):
        """
        Stores the address for a successfully imported key and allows
        deletion.
        """

        class Meta:
            verbose_name_plural = "Addresses"

        address = models.CharField(max_length=200)
        use_asc = models.BooleanField(default=False, editable=False)

        def __unicode__(self):
            return self.address

        def delete(self):
            """
            Remove any keys for this address.
            """
            from email_extras.utils import addresses_for_key
            gpg = GPG(gnupghome=GNUPG_HOME)
            for key in gpg.list_keys():
                if self.address in addresses_for_key(gpg, key):
                    gpg.delete_keys(key["fingerprint"], True)
                    gpg.delete_keys(key["fingerprint"])
            super(Address, self).delete()
