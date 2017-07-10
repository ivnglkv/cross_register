"""
Release: 0.1
Author: Golikov Ivan
Date: 10.07.2017
"""

from django.db import connection
from django.urls import reverse
from json import JSONEncoder, JSONDecoder, dumps

from .models import CrossPoint


class CrosspathPoint:
    crosspoint_id = None
    location_id = None
    parent_id = None
    main_src_id = None
    level = 0
    admin_url = ''
    destination = None
    journal_str = ''

    def __init__(self, crosspoint=None):
        if crosspoint is not None:
            self.crosspoint_id = crosspoint['id']
            self.location_id = crosspoint['location_id']
            self.parent_id = crosspoint['parent']
            self.main_src_id = crosspoint['main_src_id']
            self.level = crosspoint['level']

            cp_tmp = CrossPoint.objects.get(pk=self.crosspoint_id)
            cp_subclass = cp_tmp.get_subclass()

            self.admin_url = reverse(
                'admin:journal_{}_change'.format(cp_subclass._meta.model_name),
                args=(self.crosspoint_id,))

            cp = cp_subclass.objects.get(pk=cp_tmp.pk)
            self.journal_str = cp.journal_str()
        else:
            pass

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


def get_crosspath(source):
    """
    source -- int или tuple

    Функция получает id портов АТС, для которых нужно получить маршрут
    и возвращает его либо в виде одиночного объекта CrosspathPoint (если source -- int),
    либо в виде списка CrosspathPoint (если source -- tuple)
    """
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

        if isinstance(source, tuple):
            if len(source) == 1:
                points_ids_str = '({})'.format(source[0])
            elif len(source) > 1:
                points_ids_str = '{}'.format(source)
        elif isinstance(source, int):
            points_ids_str = '({})'.format(source)

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

    return crosspath if isinstance(source, tuple) else crosspath[0]


class CrosspathPointEncoder(JSONEncoder):
    def default(self, obj):
        result = None

        if isinstance(obj, CrosspathPoint):
            result = {}
            for k, v in obj.__dict__.items():
                if k == 'destination':
                    result[k] = [] if v is not None else None
                    for dst in v:
                        if isinstance(dst, CrosspathPoint):
                            result[k].append(self.default(dst))
                        else:
                            continue
                else:
                    result[k] = v
        else:
            result = JSONEncoder.default(self, obj)
        return result


class CrosspathPointDecoder(JSONDecoder):
    def decode(self, json_string):
        result = None

        decoded_json = super().decode(json_string)

        if isinstance(decoded_json, dict):
            result = CrosspathPoint()
            point_dict = {}

            for k, v in decoded_json.items():
                if k == 'destination':
                    point_dict[k] = []

                    if isinstance(v, list) and len(v) > 0:

                        for dst in v:
                            if isinstance(dst, dict):
                                child_json = dumps(dst, cls=CrosspathPointEncoder)
                                point_dict[k].append(self.decode(child_json))
                            else:
                                continue
                else:
                    point_dict[k] = v

            result.__dict__ = point_dict
        else:
            result = decoded_json

        return result
