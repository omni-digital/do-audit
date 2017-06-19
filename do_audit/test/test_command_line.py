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
@pytest.mark.vcr
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
        Test invoking the script 'account' subcommand with export and verbose options
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


@pytest.mark.vcr
class TestDropletsSubcommand(object):
    """
    Test 'droplets' subcommand
    """
    def test_droplets_subcommand(self, runner):
        """
        Test invoking the script 'droplets' subcommand
        """
        result = runner.invoke(
            cli, args=['droplets'],
        )

        assert result.exit_code == 0
        assert result.output

        assert result.output == (
            "# test-centos (off)\n"
            "OS:                 CentOS 6.5 x64 vmlinuz-2.6.32-431.1.2.0.1.el6.x86_64\n"
            "IP:                 192.169.1.0\n"
            "CPU:                1\n"
            "Memory:             1024 MB\n"
            "Disk:               30 GB\n"
            "URL:                https://cloud.digitalocean.com/droplets/1/graphs\n"
            "Created at:         Mon, 03/17/14 09:10:24\n"
            "\n"
            "# ubuntu-512mb-lon1-01 (active)\n"
            "OS:                 Ubuntu 16.04.2x 64\n"
            "IP:                 192.168.1.0\n"
            "CPU:                1\n"
            "Memory:             512 MB\n"
            "Disk:               20 GB\n"
            "URL:                https://cloud.digitalocean.com/droplets/2/graphs\n"
            "Created at:         Mon, 05/08/17 12:52:22\n"
        )

    def test_droplets_subcommand_verbose(self, runner):
        """
        Test invoking the script 'droplets' subcommand with verbose option
        """
        result = runner.invoke(
            cli, args=['droplets', '-v'],
        )

        assert result.exit_code == 0
        assert result.output

        assert result.output == (
            "# test-centos (off)\n"
            "OS:                 CentOS 6.5 x64 vmlinuz-2.6.32-431.1.2.0.1.el6.x86_64\n"
            "IP:                 192.169.1.0\n"
            "CPU:                1\n"
            "Memory:             1024 MB\n"
            "Disk:               30 GB\n"
            "Tags:               to-delete\n"
            "Backups:            No\n"
            "Locked:             No\n"
            "Monitoring:         No\n"
            "Features:           virtio\n"
            "Region:             Amsterdam 2\n"
            "URL:                https://cloud.digitalocean.com/droplets/1/graphs\n"
            "Created at:         Mon, 03/17/14 09:10:24\n"
            "\n"
            "# ubuntu-512mb-lon1-01 (active)\n"
            "OS:                 Ubuntu 16.04.2x 64\n"
            "IP:                 192.168.1.0\n"
            "CPU:                1\n"
            "Memory:             512 MB\n"
            "Disk:               20 GB\n"
            "Tags:               test-tag-1, test-tag-2\n"
            "Backups:            No\n"
            "Locked:             No\n"
            "Monitoring:         No\n"
            "Features:           \n"
            "Region:             London 1\n"
            "URL:                https://cloud.digitalocean.com/droplets/2/graphs\n"
            "Created at:         Mon, 05/08/17 12:52:22\n"
        )

    def test_droplets_subcommand_export(self, tmpdir, runner):
        """
        Test invoking the script 'droplets' subcommand with export option
        """
        filepath = tmpdir.mkdir('do-audit').join('output_file')

        result = runner.invoke(
            cli, args=['droplets', '-o', str(filepath)],
        )

        assert result.exit_code == 0
        assert result.output

        assert result.output == "CSV data was successfully exported to '{}'\n".format(str(filepath))

        assert filepath.read() == (
            "Name,Status,OS,IP,CPU,Memory,Disk,URL,Created at\n"
            "test-centos,off,CentOS 6.5 x64 vmlinuz-2.6.32-431.1.2.0.1.el6.x86_64,192.169.1.0,1,1024 MB,30 GB,https://cloud.digitalocean.com/droplets/1/graphs,\"Mon, 03/17/14 09:10:24\"\n"  # noqa
            "ubuntu-512mb-lon1-01,active,Ubuntu 16.04.2x 64,192.168.1.0,1,512 MB,20 GB,https://cloud.digitalocean.com/droplets/2/graphs,\"Mon, 05/08/17 12:52:22\"\n"  # noqa
        )

    def test_droplets_subcommand_export_verbose(self, tmpdir, runner):
        """
        Test invoking the script 'droplets' subcommand with export and verbose options
        """
        filepath = tmpdir.mkdir('do-audit').join('output_file')

        result = runner.invoke(
            cli, args=['droplets', '-v', '-o', str(filepath)],
        )

        assert result.exit_code == 0
        assert result.output

        assert result.output == "CSV data was successfully exported to '{}'\n".format(str(filepath))

        assert filepath.read() == (
            "Name,Status,OS,IP,CPU,Memory,Disk,Tags,Backups,Locked,Monitoring,Features,Region,URL,Created at\n"
            "test-centos,off,CentOS 6.5 x64 vmlinuz-2.6.32-431.1.2.0.1.el6.x86_64,192.169.1.0,1,1024 MB,30 GB,to-delete,No,No,No,virtio,Amsterdam 2,https://cloud.digitalocean.com/droplets/1/graphs,\"Mon, 03/17/14 09:10:24\"\n"  # noqa
            "ubuntu-512mb-lon1-01,active,Ubuntu 16.04.2x 64,192.168.1.0,1,512 MB,20 GB,\"test-tag-1, test-tag-2\",No,No,No,,London 1,https://cloud.digitalocean.com/droplets/2/graphs,\"Mon, 05/08/17 12:52:22\"\n"  # noqa
        )
