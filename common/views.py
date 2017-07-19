"""
Release: 0.2
Author: Golikov Ivan
Date: 10.07.2017
"""

from django.views.generic.list import ListView

from journal.models import PBX


class IndexView(ListView):
    template_name = 'common/index.html'
    context_object_name = 'pbx_list'

    model = PBX
