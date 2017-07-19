"""
Release: 0.2.2
Author: Golikov Ivan
Date: 10.07.2017
"""

from datetime import timedelta

from django import template
from django.contrib.auth.models import User
from django.urls import reverse

from journal.models import HistoricalPunchBlock, HistoricalPhone

register = template.Library()


@register.simple_tag(name='get_point_path_table')
def get_point_path_table(point, start_new_line, cells):
    res = '<tr>' if start_new_line else ''

    if point.level > 0 and start_new_line:
        res += '<td colspan={}></td>'.format(cells)
        res += '<td>↘ '
    elif point.level > 0:
        res += ' → '
    else:
        res += '<td>'

    if point.level > 0:
        res += '<a href="{}">{}</a>'.format(point.admin_url,
                                            point.journal_str,
                                            )
    else:
        res += '<a href="{}">{}</a>'.format(
            reverse('journal:subscriber_card', args=[int(point.journal_str)]),
            point.journal_str,
            )

    if len(point.destination) > 1:
        res += '</td><td>'
        cells += 1

    for line_num, child in enumerate(point.destination):
        new_line = True if line_num > 0 else False

        res += get_point_path_table(child, new_line, cells)

    if not point.destination:
        res += '</tr>'

    return res


class RecentChange:
    ACTION_TO_ICON = {
        '+': 'journal/icons/add.svg',
        '~': 'journal/icons/edit.svg',
        '-': 'journal/icons/delete.svg',
    }

    READABLE_ACTION = {
        '+': 'добавил (-а)',
        '~': 'изменил (-а)',
        '-': 'удалил (-а)',
    }

    def __init__(self, historical_item, user_manager):
        self.historical_item = historical_item

        self.icon = self.ACTION_TO_ICON[historical_item.history_type]
        self.action = self.READABLE_ACTION[historical_item.history_type]

        self.user = historical_item.history_user

        try:
            self.new_object_state = historical_item.history_object.changes_str()
        except:
            self.new_object_state = ''

        if historical_item.history_type == '~':
            moment_earlier = historical_item.history_date - timedelta(microseconds=1)
            try:
                self.old_object_state = historical_item.history_object.history.as_of(
                    moment_earlier
                    ).changes_str()
            except:
                self.old_object_state = ''

    def __repr__(self):
        return self.historical_item.__repr__()


@register.inclusion_tag('journal/recent_changes.html')
def recent_changes(items_count, **kwargs):
    user_manager = kwargs.get('user_manager', User.objects)
    changelist = []

    last_historical_objects = [
        HistoricalPunchBlock.objects.all()[:items_count],
        HistoricalPhone.objects.all()[:items_count],
    ]

    for objects_list in last_historical_objects:
        changelist += [RecentChange(object, user_manager) for object in objects_list]

    changelist = sorted(changelist,
                        key=lambda object: object.historical_item.history_date,
                        reverse=True
                        )[:10]

    return {
        'changelist': changelist,
    }
