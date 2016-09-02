from django.conf.urls import url

from secmaps import views
#from secmaps.views import HFDetailView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^databases/([-:.a-zA-Z0-9_]+)/([0-9]+)/([0-9]+)$', views.database_detail, name='database_detail'),
    url(r'^databases/([-:.a-zA-Z0-9_]+)/([0-9]+)$', views.database_detail, name='database_detail'),
    url(r'^databases$', views.databases, name='databases'),
    url(r'^hguids/([0-9]+)/$', views.hguids, name='hguids'),
    url(r'^search-multihguid2/(.*)/(.*)$', views.search_multihguid2, name='search_multihguid2'),
    url(r'^search-multihguid/$', views.search_multihguid, name='search_multihguid'),
    url(r'^plotd3/([-:.a-zA-Z0-9_]+)$', views.plotd3, name='plotd3'),
    url(r'^usage$', views.usage, name='usage'),
    url(r'^copywtfileres$', views.copywtfileres, name='copywtfileres'),
    url(r'^copywtfile$', views.copywtfile, name='copywtfile'),
    url(r'^displayhguidsfromfile$', views.displayhguidsfromfile, name='displayhguidsfromfile'),
    url(r'^displayfilenamewithwts$', views.displayfilenamewithwts, name='displayfilenamewithwts'),
    url(r'^csv_view/(.*)$', views.csv_view, name='csv_view'),
    url(r'^get_beforemapping_names/(.*)/(.*)$', views.get_beforemapping_names, name='get_beforemapping_names'),
]

#    url(r'^readfromfile/([-:.a-zA-Z0-9_]+)$', views.readfromfile, name='readfromfile'),
#    url(r'^writetofile$', views.writetofile, name='writetofile'),
#    url(r'^testform$', views.testform, name='testform'),
