
from django.db import models

from email_extras.settings import USE_GNUPG, GNUPG_HOME


if USE_GNUPG:
    from gnupg import GPG

    class Key(models.Model):
        """
        Accepts a key and imports it via admin's save_model which
        omits saving.
        """

        key = models.TextField()
        addresses = models.TextField(editable=False)

        def __unicode__(self):
            return self.addresses


    class Address(models.Model):
        """
        Stores the address for a successfully imported key and allows
        deletion.
        """

        class Meta:
            verbose_name_plural = "Addresses"

        address = models.CharField(max_length=200)

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
