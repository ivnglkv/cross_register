from django import template

from journal.models import CrossPoint

register = template.Library()


@register.simple_tag(name='get_point_path_table')
def get_point_path_table(point, start_new_line):
    res = '<tr>' if start_new_line else ''

    if point.level > 0 and start_new_line:
        res += '<td></td>' * (point.level * 2 - 1)
        res += '<td>↘</td>'
    elif point.level > 0:
        res += '<td>→</td>'

    res += '<td>'

    if point.level > 0:
        res += '<a href="{}">'.format(point.admin_url) + \
            CrossPoint.objects.get(pk=point.crosspoint_id).journal_str() + \
            '</a>'
    else:
        res += CrossPoint.objects.get(pk=point.crosspoint_id).journal_str()

    res += '</td>'

    for line_num, child in enumerate(point.destination):
        new_line = True if line_num > 0 else False

        res += get_point_path_table(child, new_line)

    res += '</tr>'

    return res
