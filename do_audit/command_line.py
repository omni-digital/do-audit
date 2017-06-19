# -*- coding: utf-8 -*-
"""
do-audit command line utility related code
"""
from __future__ import unicode_literals

import os

import click
import dns.zone
import requests
import six
import tablib

from do_audit import api
from do_audit.utils import add_options, get_do_manager, click_echo_kvp, yes_no, droplet_url


click.disable_unicode_literals_warning = True
tablib_formats = ('json', 'xls', 'yaml', 'csv', 'dbf', 'tsv', 'html', 'latex', 'xlsx', 'ods')

global_options = [
    click.option('--access-token', '-t', type=str, help="Digital Ocean API access token."),
    click.option('--output-file', '-o', type=click.File('wb'), help="Output file path."),
    click.option('--data-format', '-f', type=click.Choice(tablib_formats), default='csv',
                 help="Output file dat format."),
    click.option('--verbose', '-v', is_flag=True, help="Show extra information."),
]


@click.group()
@add_options(global_options)
@click.pass_context
def cli(ctx, access_token, **kwargs):
    """
    Simple command line interface for doing an audit of your Digital Ocean account and making sure
    you know what's up.

    See https://github.com/omni-digital/do-audit for more info.
    """
    # If it's not passed here, it could be passed as subcommand option
    if access_token:
        ctx.obj = get_do_manager(access_token)


@cli.command()
@add_options(global_options)
@click.pass_context
def account(ctx, access_token, output_file, data_format, verbose):
    """Show basic account info"""
    if not ctx.obj:
        ctx.obj = get_do_manager(access_token)
    do_account = ctx.obj.get_account()

    dataset = api.create_accounts_dataset(do_account, verbose=verbose)

    # Export to file
    if output_file:
        export_kwargs = {'lineterminator': os.linesep} if data_format == 'csv' else {}
        output_file.write(dataset.export(data_format, **export_kwargs).encode())

        click.secho(
            "{format} data was successfully exported to '{file_path}'".format(
                format=data_format.upper(),
                file_path=click.format_filename(output_file.name),
            ), fg='green',
        )
    # Print dataset to stdout
    else:
        for key, value in dataset.dict[0].items():
            click_echo_kvp(key, value)


@cli.command()
@add_options(global_options)
@click.pass_context
def droplets(ctx, access_token, output_file, data_format, verbose):
    """List your droplets"""
    if not ctx.obj:
        ctx.obj = get_do_manager(access_token)
    do_droplets = ctx.obj.get_all_droplets()

    dataset = api.create_droplets_dataset(do_droplets, verbose=verbose)

    # Export to file
    if output_file:
        export_kwargs = {'lineterminator': os.linesep} if data_format == 'csv' else {}
        output_file.write(dataset.export(data_format, **export_kwargs).encode())

        click.secho(
            "{format} data was successfully exported to '{file_path}'".format(
                format=data_format.upper(),
                file_path=click.format_filename(output_file.name),
            ), fg='green',
        )
    # Print dataset to stdout
    else:
        for n, row in enumerate(dataset.dict, start=1):
            droplet_name = row.pop('Name')
            droplet_status = row.pop('Status')

            click.secho(
                '# {} ({})'.format(droplet_name, droplet_status),
                fg='yellow', bold=True,
            )

            for key, value in row.items():
                click_echo_kvp(key, value)

            if n != len(dataset.dict):
                click.echo()  # Print a new line between droplets


@cli.command()
@add_options(global_options)
@click.pass_context
def domains(ctx, access_token, output_file, data_format, verbose):
    """List your domains"""
    if not ctx.obj:
        ctx.obj = get_do_manager(access_token)

    do_domains = ctx.obj.get_all_domains()

    dataset = api.create_domains_dataset(do_domains, verbose=verbose)

    # Export to file
    if output_file:
        export_kwargs = {'lineterminator': os.linesep} if data_format == 'csv' else {}
        output_file.write(dataset.export(data_format, **export_kwargs).encode())

        click.secho(
            "{format} data was successfully exported to '{file_path}'".format(
                format=data_format.upper(),
                file_path=click.format_filename(output_file.name),
            ), fg='green',
        )
    # Print dataset to stdout
    else:
        domain = None
        for n, row in enumerate(dataset.dict, start=1):
            # Group the record by the domain
            if domain != row['Domain']:
                if n > 1:
                    click.echo()  # Print a new line between droplets

                domain = row['Domain']
                click.secho('# {}'.format(domain), fg='yellow', bold=True)

            click.echo(
                '{subdomain:<35} {record_type:<10} {destination}'.format(
                    subdomain=row['Subdomain'],
                    record_type=row['Record type'],
                    destination=row['Destination'],
                )
            )


@cli.command(name='ping-domains')
@click.option('--timeout', '-t', type=int, default=3, help="How many seconds to wait for the server before giving up.")
@add_options(global_options)
@click.pass_context
def ping_domains(ctx, timeout, access_token, output_file, data_format, verbose):
    """Ping your domains and see what's the response"""
    if not ctx.obj:
        ctx.obj = get_do_manager(access_token)

    do_domains = ctx.obj.get_all_domains()
    do_droplets = {
        droplet.ip_address: (droplet.name, droplet_url(droplet.id))
        for droplet in ctx.obj.get_all_droplets()
    }

    # Create dataset with the data we want
    headers = ['Domain', 'URL', 'Status code', 'IP', 'Port', 'Droplet', 'Default NGINX', 'Error', 'Exception']
    dataset = tablib.Dataset(headers=headers)

    if output_file:
        click.secho('Working...', fg='yellow')

    for n, domain in enumerate(do_domains, start=1):
        # We could use Digital Ocean domain records API endpoint but parsing the zone file is *much* quicker
        zone = dns.zone.from_text(domain.zone_file)
        domain = zone.origin.to_text(omit_final_dot=True)

        if not output_file:
            click.secho('# {}'.format(domain), fg='yellow', bold=True)

        for record in zone.nodes:
            absolute_url = record.derelativize(zone.origin).to_text(omit_final_dot=True)
            url_http = 'http://' + absolute_url
            url_https = 'https://' + absolute_url

            for url in [url_http, url_https]:
                # Do our best to specify why the request crashes, if it does
                try:
                    error = None
                    response = requests.get(url, timeout=timeout, stream=True)
                except requests.exceptions.Timeout as e:
                    error = ("Request timed out", e)
                except requests.exceptions.SSLError as e:
                    error = ("SSL error", e)
                except requests.exceptions.ConnectionError as e:
                    error = ("Connection error", e)
                except requests.exceptions.TooManyRedirects as e:
                    error = ("Too many redirects", e)

                if error:
                    row = [domain, url, None, None, None, None, None, error[0], error[1]]
                else:
                    # Get the IP address from the underlying request socket
                    # Source: https://stackoverflow.com/a/36357465
                    if six.PY2:
                        ip, port = response.raw._fp.fp._sock.getpeername()
                    else:
                        ip, port = response.raw._fp.fp.raw._sock.getpeername()

                    status_code = '{} ({})'.format(response.status_code, response.reason)
                    droplet = '{} ({})'.format(do_droplets[ip][0], do_droplets[ip][1]) if ip in do_droplets else '-'
                    is_nginx = 'nginx' in response.text.lower()

                    row = [domain, url, status_code, ip, port, droplet, yes_no(is_nginx), None, None]

                dataset.append(row)

                # Let's print it here as we go instead of one large dump at the end of the whole loop
                if not output_file:
                    last_row = dataset.dict[-1]

                    click.secho('- {}'.format(last_row['URL']), bold=True)

                    if last_row['Error']:
                        click.secho("    {}".format(last_row['Error']), fg='red')
                        if verbose:
                            click.echo('    {}'.format(last_row['Exception']))
                    else:
                        for key, value in last_row.items():
                            if value and key not in ['Domain', 'URL']:
                                click_echo_kvp('    ' + key, value)

                    if n != len(do_domains):
                        click.echo()  # Print a new line between subdomains

    # Export to file
    if output_file:
        export_kwargs = {'lineterminator': os.linesep} if data_format == 'csv' else {}
        output_file.write(dataset.export(data_format, **export_kwargs).encode())

        click.secho(
            "{format} data was successfully exported to '{file_path}'".format(
                format=data_format.upper(),
                file_path=click.format_filename(output_file.name),
            ), fg='green',
        )


if __name__ == '__main__':
    cli()
