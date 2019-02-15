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

from django.urls import reverse
from json import JSONEncoder, JSONDecoder, dumps, loads

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
        if isinstance(crosspoint, CrossPoint):
            self.init_from_crosspoint(crosspoint)
        elif crosspoint is not None:
            self.crosspoint_id = crosspoint['id']
            self.location_id = crosspoint['location_id']
            self.parent_id = crosspoint['parent']
            self.main_src_id = crosspoint['main_src_id']
            self.level = crosspoint['level']

            cp = CrossPoint.objects.get(pk=self.crosspoint_id)

            self.admin_url = reverse(
                'admin:journal_{}_change'.format(cp._meta.model_name),
                args=(self.crosspoint_id,))

            self.journal_str = cp.journal_str()
        else:
            pass

        self.destination = []

    def init_from_crosspoint(self, crosspoint):
        self.crosspoint_id = crosspoint.pk
        self.location_id = crosspoint.location_id
        self.parent_id = crosspoint.source_id
        self.main_src_id = crosspoint.main_source_id
        self.level = crosspoint.level

        self.admin_url = reverse(
            'admin:journal_{}_change'.format(crosspoint._meta.model_name),
            args=(self.crosspoint_id,))

        self.journal_str = crosspoint.journal_str()

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


def get_crosspath(source):
    """
    source -- int или tuple

    Функция получает id портов АТС, для которых нужно получить маршрут
    и возвращает его либо в виде одиночного объекта CrosspathPoint (если source -- int),
    либо в виде списка CrosspathPoint (если source -- tuple)
    """
    if hasattr(source, '__iter__'):
        source_is_iterable = True
        crosspoints_filter = {'main_source_id__in': source}
    else:
        source_is_iterable = False
        crosspoints_filter = {'main_source_id': source}

    crosspoints = CrossPoint.objects.filter(**crosspoints_filter)

    crosspath = []
    current_crosspath_index = -1

    while len(crosspoints) > 0:
        exclude_points_list = []

        for point in crosspoints:
            cur_point = CrosspathPoint(point)

            if cur_point.level == 1:
                if current_crosspath_index >= 0:
                    crosspath[current_crosspath_index].destination.append(cur_point)
                    exclude_points_list.append(point.pk)
            elif cur_point.level >= 2:
                try:
                    source_point = crosspath[current_crosspath_index]
                    parent = source_point.find_parent(cur_point.parent_id)
                    parent.destination.append(cur_point)
                    exclude_points_list.append(point.pk)
                except:
                    pass
            else:
                crosspath.append(cur_point)
                current_crosspath_index += 1

                exclude_points_list.append(point.pk)

        crosspoints = crosspoints.exclude(pk__in=exclude_points_list)

    return crosspath if source_is_iterable else crosspath[0]


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


def pbxport_to_crosspath(source):
    if hasattr(source, '__iter__'):
        result = [
           loads(pbxport.json_path, cls=CrosspathPointDecoder) for pbxport in source
        ]
    else:
        result = loads(source.json_path, cls=CrosspathPointDecoder)

    return result
