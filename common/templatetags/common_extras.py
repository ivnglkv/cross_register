"""
Release: 0.2.1
Author: Golikov Ivan
Date: 10.07.2017
"""

from django import template

register = template.Library()


@register.filter(name='range')
def times(number):
    return range(1, number+1)
