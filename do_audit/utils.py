# -*- coding: utf-8 -*-
"""
do-audit utils
"""
from __future__ import unicode_literals

import click


def click_echo_kvp(key, value, padding=20, color='green'):
    """
    Helper class for pretty printing key value pairs in click

    :param key: item key
    :type key: str
    :param value: item value
    :type value: any
    :param padding: key padding
    :type padding: int
    :param color: key color (ANSI compliant)
    :type color: str
    :returns: proper `click.echo` call to stdout
    :rtype: None
    """
    return click.echo(
        click.style('{key:<{padding}}'.format(
            key=key + ':',
            padding=padding
        ), fg=color) +
        str(value)
    )
