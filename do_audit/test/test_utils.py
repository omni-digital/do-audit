# -*- coding: utf-8 -*-
"""
Test 'do_audit.utils' file
"""
from __future__ import unicode_literals

from uuid import uuid4

import click
import pytest

from do_audit import utils


@pytest.mark.parametrize('key,value,padding,color', [
    ('key', 'value', 50, 'red'),
    (str(uuid4()), str(uuid4()), 10, 'green'),
])
def test_click_echo_kvp(key, value, padding, color, mocker):
    """
    Test 'do_audit.utils.click_echo_kvp'
    """
    click_echo = mocker.patch('click.echo')

    utils.click_echo_kvp(key, value, padding=padding, color=color)

    click_echo.assert_called_once_with(
        click.style('{key:<{padding}}'.format(
            key=key + ':',
            padding=padding
        ), fg=color) +
        str(value)
    )

    # Check default padding and color values
    click_echo = mocker.patch('click.echo'
                              )
    utils.click_echo_kvp(key, value)

    click_echo.assert_called_once_with(
        click.style('{key:<{padding}}'.format(
            key=key + ':',
            padding=20
        ), fg='green') +
        str(value)
    )


def test_yes_no():
    """
    Test 'do_audit.utils.yes_no'
    """
    assert utils.yes_no(True) == 'Yes'
    assert utils.yes_no(False) == 'No'


def test_droplet_url():
    """
    Test 'do_audit.utils.droplet_url'
    """
    uuid = str(uuid4())
    assert utils.droplet_url(uuid) == 'https://cloud.digitalocean.com/droplets/{}/graphs'.format(uuid)
