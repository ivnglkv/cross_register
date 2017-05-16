from django.db import connection
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from math import ceil

from .models import PBXPort, PBX, CrossPoint


class CrosspathPoint:
    crosspoint = None
    admin_url = ''
    destination = None

    def __str__(self):
        return('boot')


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


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
    context['pbxports_list'] = pbxports_list
    context['pbxports_count'] = pbxports_count
    context['current_page'] = current_page
    context['pages_count'] = pages_count
    context['first_element_index'] = first_element_index + 1
    context['last_element_index'] = last_element_index

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

        cursor.execute(sql.format(points_ids))

        crosspoints = dictfetchall(cursor)

    crosspath = []
    current_crosspath_index = -1

    current_source_point_id = -1
    last_point = None
    for point in crosspoints:
        if point['main_src_id'] != current_source_point_id:
            current_source_point_id = point['id']

        cur_point = CrosspathPoint()

        cur_point.crosspoint = point
        cp_tmp = CrossPoint.objects.get(pk=point['id'])
        cur_point.admin_url = reverse(
            'admin:journal_{}_change'.format(cp_tmp.get_subclass()._meta.model_name),
            args=(point['id'],))

        level = point['level']

        if level > 0:
            last_point.destination = cur_point
            pass
        else:
            crosspath.append(cur_point)
            current_crosspath_index += 1

        last_point = cur_point

    context['crosspath'] = crosspath

    return render(request, template, context)


class PBXPortsView(ListView):
    model = PBXPort
    template_name = 'journal/pbx_ports.html'

    def get_queryset(self, *args, **kwargs):
        return PBXPort.objects.filter(pbx=int(kwargs['pbx']))
