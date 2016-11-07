# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from gnupg import GPG

from email_extras.settings import GNUPG_HOME


def forward_change(apps, schema_editor):
    Key = apps.get_model('email_extras', 'Key')
    Address = apps.get_model('email_extras', 'Address')

    for key in Key.objects.all():
        addresses = Address.objects.filter(address__in=key.addresses.split(','))
        addresses.update(key=key)

        gpg = GPG(gnupghome=GNUPG_HOME)
        result = gpg.import_keys(key.key)
        key.fingerprint = result.fingerprints[0]
        key.save()


def reverse_change(apps, schema_editor):
    Key = apps.get_model('email_extras', 'Key')
    for key in Key.objects.all():
        key.addresses = ",".join(address.address for address in key.address_set.all())
        key.save()


class Migration(migrations.Migration):

    dependencies = [
        ('email_extras', '0002_auto_20161103_0752'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='key',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='email_extras.Key'),
        ),
        migrations.AddField(
            model_name='key',
            name='fingerprint',
            field=models.CharField(blank=True, editable=False, max_length=200),
        ),
        migrations.RunPython(forward_change, reverse_change),
        migrations.RemoveField(
            model_name='key',
            name='addresses',
        ),
    ]
