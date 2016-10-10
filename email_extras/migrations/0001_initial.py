from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200)),
                ('use_asc', models.BooleanField(default=False, editable=False)),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.TextField()),
                ('addresses', models.TextField(editable=False)),
                ('use_asc', models.BooleanField(default=False, help_text="If True, an '.asc' extension will be added to email attachments sent to the address for this key.")),
            ],
            options={
                'verbose_name': 'Key',
                'verbose_name_plural': 'Keys',
            },
        ),
    ]
