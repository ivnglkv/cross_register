# This file is part of Cregister - cross register management software
# Copyright (C) 2017  Golikov Ivan <ivnglkv@eml.cc>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.conf.urls import url

from . import views

app_name = 'journal'
urlpatterns = [
    url(r'^help/?$', views.help_view, name='help'),
    url(r'^pbx/(?P<pbx>\d+)/page-(?P<page>\d+)$', views.pbx_ports_view, name='pbx_ports'),
    url(r'^subscriber_card/(?P<card>\d+)$', views.subscriber_card_view, name='subscriber_card'),
    url(r'^search$', views.search_view, name='search'),
]
