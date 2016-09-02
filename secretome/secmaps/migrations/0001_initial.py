# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dbids',
            fields=[
                ('dbid', models.CharField(max_length=32, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hguids',
            fields=[
                ('hguid', models.CharField(max_length=32, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='HguidsFrequencies',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_sources', models.IntegerField()),
                ('times_mapped', models.IntegerField()),
                ('mapped_hguid', models.ForeignKey(to='secmaps.Hguids', db_column='mapped_hguid')),
            ],
        ),
        migrations.CreateModel(
            name='MappedHguids',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hgnc_symbol', models.CharField(max_length=32)),
                ('mapped_db', models.ForeignKey(to='secmaps.Dbids', db_column='mapped_db')),
                ('mapped_hguid', models.ForeignKey(to='secmaps.Hguids', db_column='mapped_hguid')),
            ],
        ),
        migrations.CreateModel(
            name='MappedIds',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('before_mapping', models.CharField(max_length=32)),
                ('mapped_db', models.ForeignKey(to='secmaps.Dbids', db_column='mapped_db')),
                ('mapped_hguid', models.ForeignKey(to='secmaps.Hguids', db_column='mapped_hguid')),
            ],
        ),
    ]
