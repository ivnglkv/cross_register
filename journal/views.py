from json import loads

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.generic import ListView
from math import ceil

from .models import PBXPort, PBX
from .utils import get_crosspath, CrosspathPointDecoder


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

    crosspath = [
        loads(point.json_path, cls=CrosspathPointDecoder) for point in pbxports_list
    ]

    context['crosspath'] = crosspath

    return render(request, template, context)


def subscriber_card_view(request, card):
    context = {}
    template = 'journal/subscriber_card.html'

    pbxport = PBXPort.objects.get(subscriber_number=card)

    context['pbxport'] = pbxport
    points_ids = (pbxport.crosspoint_ptr_id,)
    context['point'] = get_crosspath(points_ids)[0]

    last_pbxport_state = pbxport.history.values()[0]

    last_edit_person = None
    try:
        last_edit_person = User.objects.get(pk=last_pbxport_state['history_user_id'])
    except ObjectDoesNotExist:
        pass

    context['last_edit_person'] = last_edit_person

    return render(request, template, context)


class PBXPortsView(ListView):
    model = PBXPort
    template_name = 'journal/pbx_ports.html'

    def get_queryset(self, *args, **kwargs):
        return PBXPort.objects.filter(pbx=int(kwargs['pbx']))
