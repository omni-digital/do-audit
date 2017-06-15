# -*- coding: utf-8 -*-
"""
Test do_audit.command_line.py file
"""
from __future__ import unicode_literals

import os
from datetime import datetime
from uuid import uuid4

import pytest
import digitalocean
from click.testing import CliRunner

from do_audit.command_line import cli, DO_ACCESS_TOKEN_ENV


# Module fixtures
@pytest.fixture(scope='module')
def runner():
    """Get CliRunner"""
    return CliRunner()


# Tests
def test_incorrect_access_token(runner):
    """Test invoking the script with incorrect access token"""
    result = runner.invoke(
        cli, args=['--access-token', str(uuid4()), 'account']
    )

    assert isinstance(result.exception, SystemExit)
    assert result.exit_code == 1


def test_account_subcommand(mocker, runner):
    """
    Test invoking the script 'account' subcommand
    """
    do_manager_instance = mocker.MagicMock(autospec=digitalocean.Manager)
    do_manager = mocker.patch('digitalocean.Manager', return_value=do_manager_instance)
    do_manager_instance.get_account.return_value = mocker.MagicMock(autospec=digitalocean.Account)

    result = runner.invoke(
        cli, args=['account'],
    )

    assert result.exit_code == 0
    assert result.output

    do_manager.assert_called_once_with(token=os.getenv(DO_ACCESS_TOKEN_ENV))
    do_manager_instance.get_account.assert_called_with()


def test_droplets_subcommand(mocker, runner):
    """Test invoking the script 'droplets' subcommand"""
    do_manager_instance = mocker.MagicMock(autospec=digitalocean.Manager)
    do_manager = mocker.patch('digitalocean.Manager', return_value=do_manager_instance)
    do_manager_instance.get_all_droplets.return_value = [
        mocker.MagicMock(autospec=digitalocean.Droplet, created_at=datetime.now().isoformat()),
        mocker.MagicMock(autospec=digitalocean.Droplet, created_at=datetime.now().isoformat()),
    ]

    result = runner.invoke(
        cli, args=['droplets'],
    )

    assert result.exit_code == 0
    assert result.output

    do_manager.assert_called_once_with(token=os.getenv(DO_ACCESS_TOKEN_ENV))
    do_manager_instance.get_all_droplets.assert_called_once_with()


# TODO: Add 'domains' and 'ping-domains' subcommands tests
# TODO: Mock API responses with example responses from DigitalOcean docs
