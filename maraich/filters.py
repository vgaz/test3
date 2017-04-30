# -*- coding: utf-8 -*-

@register.filter(name='d_get_item')
def d_get_item(value, arg):
    """get value of key in dict"""
    return value[arg]

