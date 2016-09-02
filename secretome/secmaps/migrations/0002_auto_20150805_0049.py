# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secmaps', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='hguidsfrequencies',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mappedhguids',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='mappedids',
            options={'managed': False},
        ),
    ]
