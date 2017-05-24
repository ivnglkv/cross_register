from django import template

from journal.models import CrossPoint

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
        res += '<a href="{}">'.format(point.admin_url) + \
            CrossPoint.objects.get(pk=point.crosspoint_id).journal_str() + \
            '</a>'
    else:
        res += CrossPoint.objects.get(pk=point.crosspoint_id).journal_str()

    if len(point.destination) > 1:
        res += '</td><td>'
        cells += 1

    for line_num, child in enumerate(point.destination):
        new_line = True if line_num > 0 else False

        res += get_point_path_table(child, new_line, cells)

    if not point.destination:
        res += '</tr>'

    return res
