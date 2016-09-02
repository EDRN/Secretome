from django.contrib import admin

# Register your models here.

from secmaps.models import Dbids, Hguids, HguidsFrequencies, MappedHguids, MappedIds

admin.site.register(Dbids)
admin.site.register(Hguids)
admin.site.register(HguidsFrequencies)
admin.site.register(MappedHguids)
admin.site.register(MappedIds)
