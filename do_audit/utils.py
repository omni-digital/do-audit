# -*- coding: utf-8 -*-
"""
do-audit utils
"""
from __future__ import unicode_literals

import os

import click
import digitalocean


DO_ACCESS_TOKEN_ENV = 'DO_ACCESS_TOKEN'


def add_options(options):
    """
    Helper function for grouping click options

    Source:
        https://github.com/pallets/click/issues/108#issuecomment-255547347
    """
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def get_do_manager(access_token):
    """
    Helper function for initializing `digitalocean.Manager` instance

    :param access_token: Digital Ocean access token
    :type access_token: str
    :returns: Digital Ocean manager instance
    :rtype: digitalocean.Manager
    :raises click.ClickException: when the token isn't passed or is incorrect
    """
    token = access_token or os.getenv(DO_ACCESS_TOKEN_ENV)

    if not token:
        raise click.ClickException(
            "You need to either pass your Digital Ocean access token explicitly ('-t ...') "
            "or set is as an environment variable ('export {DO_ACCESS_TOKEN_ENV}=...').".format(
                DO_ACCESS_TOKEN_ENV=DO_ACCESS_TOKEN_ENV,
            )
        )

    try:
        manager = digitalocean.Manager(token=token)
        manager.get_account()  # To make sure we're authenticated
    except digitalocean.Error as e:
        raise click.ClickException("We were unable to connect to your Digital Ocean account: '{}'".format(e))

    return manager


def click_echo_kvp(key, value, padding=20, color='green'):
    """
    Helper function for pretty printing key value pairs in click

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


def yes_no(value):
    """
    Helper function for converting bool values to their English counterparts

    :param value: boolean value
    :type value: bool
    :returns: yes or no
    :rtype: str
    """
    return 'Yes' if value else 'No'


def droplet_url(droplet_id):
    """
    Helper function for returning droplet URL based

    :param droplet_id: droplet id
    :type droplet_id: str
    :returns: droplet URL
    :rtype: str
    """
    return 'https://cloud.digitalocean.com/droplets/{}/graphs'.format(droplet_id)
