from django.test import TestCase
from secmaps.models import *

#test creations of models
class ModelTests(TestCase):

    def create_dbids(self, dbid="shh2"):
        return Dbids.objects.create(dbid=dbid)

    def create_hguids(self, hguid="shh2"):
        return Hguids.objects.create(hguid=hguid)

    def create_hguidsfrequencies(self,  mapped_hguid=None, num_sources=1, times_mapped=1):
        return HguidsFrequencies.objects.create(mapped_hguid=mapped_hguid, num_sources=num_sources, times_mapped=times_mapped)


    def test_model_creation(self):
        dbidm = self.create_dbids()
        self.assertTrue(isinstance(dbidm, Dbids))

        hguidm = self.create_hguids()
        self.assertTrue(isinstance(hguidm, Hguids))

        if dbidm:
            hguidfreqm = self.create_hguidsfrequencies(mapped_hguid = hguidm)
            self.assertTrue(isinstance(hguidfreqm, HguidsFrequencies))
