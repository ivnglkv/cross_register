from django.conf.urls import url

from .views import pbx_ports_view

urlpatterns = [
    url(r'^pbx/(?P<pbx>\d+)/page-(?P<page>\d+)$', pbx_ports_view, name='pbx_ports'),
]
