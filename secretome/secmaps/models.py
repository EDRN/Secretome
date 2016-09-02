# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Dbids(models.Model):
    def __unicode__(self):
        return self.dbid

    dbid = models.CharField(primary_key=True, max_length=32)

class Hguids(models.Model):
    def __unicode__(self):
        return self.hguid

    hguid = models.CharField(primary_key=True, max_length=32)

class HguidsFrequencies(models.Model):

    id = models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)
    mapped_hguid = models.ForeignKey(Hguids, db_column='mapped_hguid')
    num_sources = models.IntegerField()
    times_mapped = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'secmaps_hguidsfrequencies'

class MappedHguids(models.Model):

    id = models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)
    mapped_hguid = models.ForeignKey(Hguids, db_column='mapped_hguid')
    hgnc_symbol = models.CharField(max_length=32)
    mapped_db = models.ForeignKey(Dbids, db_column='mapped_db')

    class Meta:
        managed = False
        db_table = 'secmaps_mappedhguids'


class MappedIds(models.Model):

    id = models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)
    mapped_db = models.ForeignKey(Dbids, db_column='mapped_db')
    before_mapping = models.CharField(max_length=32)
    mapped_hguid = models.ForeignKey(Hguids, db_column='mapped_hguid')

    class Meta:
        managed = False
        db_table = 'secmaps_mappedids'

