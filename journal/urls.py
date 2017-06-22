from django.conf.urls import url

from . import views

app_name = 'journal'
urlpatterns = [
    url(r'^pbx/(?P<pbx>\d+)/page-(?P<page>\d+)$', views.pbx_ports_view, name='pbx_ports'),
    url(r'^subscriber_card/(?P<card>\d+)$', views.subscriber_card_view, name='subscriber_card'),
]
