# This file is part of Cregister - cross register management software
# Copyright (C) 2017  Golikov Ivan <ivnglkv@eml.cc>
#
# Cregister is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cregister is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cregister.  If not, see <http://www.gnu.org/licenses/>.

from math import ceil
import re

from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.views.generic import ListView

from .models import PBXPort, PBX, Subscriber, Phone
from .utils import pbxport_to_crosspath


def pbx_ports_view(request, pbx, page):
    context = {}
    template = 'journal/pbx_ports.html'

    ports_per_page = 100

    current_page = int(page)

    first_element_index = (current_page - 1) * ports_per_page
    last_element_index = first_element_index + ports_per_page

    pbxports_list = PBXPort.objects.filter(pbx=pbx)[first_element_index:last_element_index]
    pbxports_count = PBXPort.objects.filter(pbx=pbx).count()
    pages_count = ceil(pbxports_count / ports_per_page)

    last_element_index = first_element_index + pbxports_list.count()

    context['pbx'] = pbx
    context['pbx_object'] = PBX.objects.get(pk=pbx)
    context['pbxports_count'] = pbxports_count
    context['current_page'] = current_page
    context['pages_count'] = pages_count
    context['first_element_index'] = first_element_index + 1
    context['last_element_index'] = last_element_index
    context['can_add_pbxport'] = request.user.has_perm('journal.add_pbxport')

    context['crosspath'] = pbxport_to_crosspath(pbxports_list)

    return render(request, template, context)


def subscriber_card_view(request, card):
    context = {}
    template = 'journal/subscriber_card.html'

    pbxport = PBXPort.objects.get(subscriber_number=card)

    context['pbxport'] = pbxport
    context['point'] = pbxport_to_crosspath(pbxport)

    last_pbxport_state = pbxport.history.values()[0]

    last_edit_person = None
    try:
        last_edit_person = User.objects.get(pk=last_pbxport_state['history_user_id'])
    except ObjectDoesNotExist:
        pass

    context['last_edit_person'] = last_edit_person

    return render(request, template, context)


def search_view(request):
    context = {}
    template = 'journal/search.html'
    search_input = request.GET.get('search_input', '').strip()

    if re.match(r'\d+', search_input):
        pbxport_set = PBXPort.objects.filter(subscriber_number=search_input)
        context['number_crosspath'] = pbxport_to_crosspath(pbxport_set)

        room_number_pattern = r'(^|\D+){}(\D+|$)'.format(search_input)
        phone_set = Phone.objects.filter(location__room__room__iregex=room_number_pattern)
        pbxport_set = PBXPort.objects.filter(pk__in=phone_set.values('main_source'))

        context['room_crosspath'] = pbxport_to_crosspath(pbxport_set)

    elif search_input != '':
        subscriber_set = Subscriber.objects.order_by(
            'last_name').filter(
            last_name__icontains=search_input)

        subscriber_crosspath = {}

        for subscriber in subscriber_set:
            phone_set = subscriber.phones.all().values('main_source')
            pbxport_set = PBXPort.objects.filter(pk__in=phone_set)

            if pbxport_set:
                subscriber_crosspath[subscriber] = pbxport_to_crosspath(pbxport_set)

        context['subscriber_crosspath'] = subscriber_crosspath

    return render(request, template, context)


class PBXPortsView(ListView):
    model = PBXPort
    template_name = 'journal/pbx_ports.html'

    def get_queryset(self, *args, **kwargs):
        return PBXPort.objects.filter(pbx=int(kwargs['pbx']))


def help_view(request, page_name=None):
    help_file_name = 'user_manual.pdf'

    return redirect(settings.MEDIA_URL + help_file_name)
