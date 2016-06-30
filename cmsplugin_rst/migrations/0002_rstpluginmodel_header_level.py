# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_rst', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rstpluginmodel',
            name='header_level',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
