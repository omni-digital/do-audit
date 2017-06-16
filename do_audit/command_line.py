# -*- coding: utf-8 -*-
"""
do-audit command line utility related code
"""
from __future__ import unicode_literals

import click
import dateutil.parser
import dns.zone
import requests
import six
import tablib

from do_audit.utils import add_options, get_do_manager, click_echo_kvp, yes_no, droplet_url


click.disable_unicode_literals_warning = True
tablib_formats = ('json', 'xls', 'yaml', 'csv', 'dbf', 'tsv', 'html', 'latex', 'xlsx', 'ods')

global_options = [
    click.option('--access-token', '-t', type=str, help="Digital Ocean API access token."),
    click.option('--output-file', '-o', type=click.File('w'), help="Output file path."),
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

    email = do_account.email
    if not do_account.email_verified:
        email += ' (unverified)'

    status = do_account.status
    if do_account.status_message:
        status += ' ({})'.format(do_account.status_message)

    # Create dataset with the data we want
    headers = ['Email', 'Status', 'Droplet limit']
    row = [email, status, do_account.droplet_limit]
    if verbose:
        headers += ['Floating IP limit', 'UUID']
        row += [do_account.floating_ip_limit, do_account.uuid]

    dataset = tablib.Dataset(headers=headers)
    dataset.append(row)

    # Export to file
    if output_file:
        output_file.write(dataset.export(data_format))
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

    # Create dataset with the data we want
    headers = ['Name', 'Status', 'OS', 'IP', 'CPU', 'Memory', 'Disk']
    if verbose:
        headers += ['Tags', 'Backups', 'Locked', 'Monitoring', 'Features', 'Region']
    headers += ['URL', 'Created at']

    dataset = tablib.Dataset(headers=headers)

    for n, droplet in enumerate(do_droplets, start=1):
        created_at = dateutil.parser.parse(droplet.created_at)

        # Try to guess droplet OS
        if droplet.kernel:
            do_os = droplet.kernel.get('name', 'unknown')
        elif droplet.image:
            do_os = '{} {}'.format(droplet.image['distribution'], droplet.image['name'])
        else:
            do_os = 'unknown'

        # Generate human readable droplet info row
        row = [
            droplet.name, droplet.status, do_os, droplet.ip_address, droplet.vcpus,
            str(droplet.memory) + ' MB', str(droplet.disk) + ' GB',
        ]
        if verbose:
            row += [
                ', '.join(droplet.tags), yes_no(droplet.backups), yes_no(droplet.locked), yes_no(droplet.monitoring),
                ', '.join(droplet.features), droplet.region['name'],
            ]
        row += [droplet_url(droplet.id), created_at.strftime('%a, %x %X')]

        dataset.append(row)

    # Export to file
    if output_file:
        output_file.write(dataset.export(data_format))
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

    # Create dataset with the data we want
    headers = ['Domain', 'Subdomain', 'Record type', 'Destination']
    dataset = tablib.Dataset(headers=headers)

    for n, domain in enumerate(do_domains, start=1):
        # We could use Digital Ocean domain records API endpoint but parsing the zone file is *much* quicker
        zone = dns.zone.from_text(domain.zone_file)
        domain = zone.origin.to_text(omit_final_dot=True)

        for key, value in zone.nodes.items():
            subdomain = key.to_text(omit_final_dot=True)

            for rd in value.rdatasets:
                # Non verbose output only contains A and CNAME records
                if not verbose and rd.rdtype not in [dns.rdatatype.A, dns.rdatatype.CNAME]:
                    continue

                for address in rd:
                    dataset.append([domain, subdomain, dns.rdatatype.to_text(rd.rdtype), str(address)])

    # Export to file
    if output_file:
        output_file.write(dataset.export(data_format))
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
        droplet.ip_address: (droplet.name, 'https://cloud.digitalocean.com/droplets/{}/graphs'.format(droplet.id))
        for droplet in ctx.obj.get_all_droplets()
    }

    for n, domain in enumerate(do_domains, start=1):
        # We could use Digital Ocean domain records API endpoint but parsing the zone file is *much* quicker
        zone = dns.zone.from_text(domain.zone_file)

        domain = zone.origin.to_text(omit_final_dot=True)
        click.secho('# {}'.format(domain), fg='yellow', bold=True)

        for record in zone.nodes:
            absolute_url = record.derelativize(zone.origin).to_text(omit_final_dot=True)
            url_http = 'http://' + absolute_url
            url_https = 'https://' + absolute_url

            for url in [url_http, url_https]:
                click.secho('- {}'.format(url), bold=True)

                # Do our best to specify why the request crashes, if it does
                try:
                    response = requests.get(url, timeout=timeout, stream=True)
                except requests.exceptions.Timeout as e:
                    click.secho("    Request timed out", fg='red')
                    if verbose:
                        click.echo('    {}'.format(repr(e)))
                except requests.exceptions.SSLError as e:
                    click.secho("    SSL error", fg='red')
                    if verbose:
                        click.echo('    {}'.format(repr(e)))
                except requests.exceptions.ConnectionError as e:
                    click.secho("    Connection error", fg='red')
                    if verbose:
                        click.echo('    {}'.format(repr(e)))
                except requests.exceptions.TooManyRedirects as e:
                    click.secho("    Too many redirects", fg='red')
                    if verbose:
                        click.echo('    {}'.format(repr(e)))
                else:
                    # Get the IP address from the underlying request socket
                    # Source: https://stackoverflow.com/a/36357465
                    if six.PY2:
                        ip, port = response.raw._fp.fp._sock.getpeername()
                    else:
                        ip, port = response.raw._fp.fp.raw._sock.getpeername()

                    droplet = '{} ({})'.format(do_droplets[ip][0], do_droplets[ip][1]) if ip in do_droplets else '-'
                    is_nginx = 'nginx' in response.text.lower()

                    click_echo_kvp('    Status code', '{} ({})'.format(response.status_code, response.reason))
                    click_echo_kvp('    IP', ip)
                    click_echo_kvp('    Port', port)
                    click_echo_kvp('    Droplet', droplet)
                    click_echo_kvp('    Default NGINX', 'Yes' if is_nginx else 'No')

        if n != len(do_domains):
            click.echo()  # Print a new line between domains


if __name__ == '__main__':
    cli()
