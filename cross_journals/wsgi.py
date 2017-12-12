"""
WSGI config for cross_journals project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

# This file is part of Cregister - cross register management software
# Copyright (C) 2017  Golikov Ivan <ivnglkv@eml.cc>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cross_journals.settings")

application = get_wsgi_application()
