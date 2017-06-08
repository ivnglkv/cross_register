from django.db import connection
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from math import ceil

from .models import PBXPort, PBX, CrossPoint


class CrosspathPoint:
    crosspoint_id = None
    location_id = None
    parent_id = None
    main_src_id = None
    level = 0
    admin_url = ''
    destination = None

    def __init__(self, crosspoint):
        self.crosspoint_id = crosspoint['id']
        self.location_id = crosspoint['location_id']
        self.parent_id = crosspoint['parent']
        self.main_src_id = crosspoint['main_src_id']
        self.level = crosspoint['level']

        cp_tmp = CrossPoint.objects.get(pk=self.crosspoint_id)
        self.admin_url = reverse(
            'admin:journal_{}_change'.format(cp_tmp.get_subclass()._meta.model_name),
            args=(self.crosspoint_id,))

        self.destination = []

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        res = '{0} crosspoint_id: {1}, ' \
              'main_src_id: {2}, parent_id: {3}, level: {4}\n' \
              '{0} destination: {5}'.format('  ' * self.level,
                                            self.crosspoint_id,
                                            self.main_src_id,
                                            self.parent_id,
                                            self.level,
                                            self.destination,
                                            )
        return res

    def find_parent(self, parent_id):
        result = None

        for child in self.destination:
            if child.crosspoint_id == parent_id:
                result = child
            else:
                result = child.find_parent(parent_id)

            if result:
                break

        return result


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_crosspath(points):
    crosspoints = {}

    with connection.cursor() as cursor:
        from os import path
        from django.conf import settings

        sqlfile = open(path.join(settings.BASE_DIR,
                                 'journal',
                                 'sql',
                                 'get_crosspath.sql',
                                 ),
                       'r')
        sql = sqlfile.read()

        if len(points) > 0:
            if len(points) == 1:
                points_ids_str = '({})'.format(points[0])
            else:
                points_ids_str = '{}'.format(points)

            cursor.execute(sql.format(points_ids_str))
            crosspoints = dictfetchall(cursor)

    crosspath = []
    current_crosspath_index = -1

    for point in crosspoints:
        cur_point = CrosspathPoint(point)

        if cur_point.level == 1:
            crosspath[current_crosspath_index].destination.append(cur_point)
        elif cur_point.level >= 2:
            source_point = crosspath[current_crosspath_index]
            parent = source_point.find_parent(cur_point.parent_id)
            parent.destination.append(cur_point)
            pass
        else:
            crosspath.append(cur_point)
            current_crosspath_index += 1

    return crosspath


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

    points_ids = tuple(x.crosspoint_ptr_id for x in pbxports_list)

    last_element_index = first_element_index + pbxports_list.count()

    context['pbx'] = pbx
    context['pbx_object'] = PBX.objects.get(pk=pbx)
    context['pbxports_count'] = pbxports_count
    context['current_page'] = current_page
    context['pages_count'] = pages_count
    context['first_element_index'] = first_element_index + 1
    context['last_element_index'] = last_element_index
    context['can_add_pbxport'] = request.user.has_perm('journal.add_pbxport')

    crosspath = get_crosspath(points_ids)

    context['crosspath'] = crosspath

    return render(request, template, context)


def subscriber_card_view(request, card):
    context = {}
    template = 'journal/subscriber_card.html'

    pbxport = PBXPort.objects.get(subscriber_number=card)

    context['pbxport'] = pbxport
    points_ids = (pbxport.crosspoint_ptr_id,)
    context['point'] = get_crosspath(points_ids)[0]

    return render(request, template, context)


class PBXPortsView(ListView):
    model = PBXPort
    template_name = 'journal/pbx_ports.html'

    def get_queryset(self, *args, **kwargs):
        return PBXPort.objects.filter(pbx=int(kwargs['pbx']))
