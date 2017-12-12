# This file is part of Cregister - cross register management software
# Copyright (C) 2017  Golikov Ivan <ivnglkv@eml.cc>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.views.generic.list import ListView

from journal.models import PBX


class IndexView(ListView):
    template_name = 'common/index.html'
    context_object_name = 'pbx_list'

    model = PBX
