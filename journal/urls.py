from django.conf.urls import url

from .views import pbx_ports_view, subscriber_card_view

app_name = 'journal'
urlpatterns = [
    url(r'^pbx/(?P<pbx>\d+)/page-(?P<page>\d+)$', pbx_ports_view, name='pbx_ports'),
    url(r'^subscriber_card/(?P<card>\d+)$', subscriber_card_view, name='subscriber_card'),
]
