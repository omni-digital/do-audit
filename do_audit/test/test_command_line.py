# -*- coding: utf-8 -*-
"""
Test 'do_audit.command_line' file
"""
from __future__ import unicode_literals

import pytest
from click.testing import CliRunner

from do_audit.command_line import cli


# Module fixtures
@pytest.fixture(scope='module')
def runner():
    """Get CliRunner"""
    return CliRunner()


# Tests
@pytest.mark.vcr()
class TestAccountSubcommand(object):
    """
    Test 'account' subcommand
    """
    def test_account_subcommand(self, runner):
        """
        Test invoking the script 'account' subcommand
        """
        result = runner.invoke(
            cli, args=['account'],
        )

        assert result.exit_code == 0
        assert result.output

        assert result.output == (
            "Email:              user@example.com\n"
            "Status:             active\n"
            "Droplet limit:      25\n"
        )

    def test_account_subcommand_verbose(self, runner):
        """
        Test invoking the script 'account' subcommand with verbose option
        """
        result = runner.invoke(
            cli, args=['account', '-v'],
        )

        assert result.exit_code == 0
        assert result.output

        assert result.output == (
            "Email:              user@example.com\n"
            "Status:             active\n"
            "Droplet limit:      25\n"
            "Floating IP limit:  3\n"
            "UUID:               uuid\n"
        )

    def test_account_subcommand_export(self, tmpdir, runner):
        """
        Test invoking the script 'account' subcommand with export option
        """
        filepath = tmpdir.mkdir('do-audit').join('output_file')

        result = runner.invoke(
            cli, args=['account', '-o', str(filepath)],
        )

        assert result.exit_code == 0
        assert result.output

        assert result.output == "CSV data was successfully exported to '{}'\n".format(str(filepath))

        assert filepath.read() == (
            "Email,Status,Droplet limit\n"
            "user@example.com,active,25\n"
        )

    def test_account_subcommand_export_verbose(self, tmpdir, runner):
        """
        Test invoking the script 'account' subcommand with export option
        """
        filepath = tmpdir.mkdir('do-audit').join('output_file')

        result = runner.invoke(
            cli, args=['account', '-v', '-o', str(filepath)],
        )

        assert result.exit_code == 0
        assert result.output

        assert result.output == "CSV data was successfully exported to '{}'\n".format(str(filepath))

        assert filepath.read() == (
            "Email,Status,Droplet limit,Floating IP limit,UUID\n"
            "user@example.com,active,25,3,uuid\n"
        )
