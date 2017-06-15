# -*- coding: utf-8 -*-
"""
do-audit command line utility related code
"""
from __future__ import unicode_literals

import os

import click
import dateutil.parser
import digitalocean
import dns.zone
import requests

from do_audit.utils import click_echo_kvp


click.disable_unicode_literals_warning = True

DO_ACCESS_TOKEN_ENV = 'DO_ACCESS_TOKEN'


@click.group()
@click.option('--access-token', '-t', type=str, help="Digital Ocean API access token.")
@click.pass_context
def cli(ctx, access_token):
    """
    Simple command line interface for doing an audit of your Digital Ocean account and making sure
    you know what's up.

    See https://github.com/omni-digital/do-audit for more info.
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
        ctx.obj = digitalocean.Manager(token=token)
        ctx.obj.get_account()  # To make sure we're authenticated
    except digitalocean.Error as e:
        raise click.ClickException("We were unable to connect to your Digital Ocean account: {}".format(repr(e)))


@cli.command()
@click.pass_context
def account(ctx):
    """Show basic account info"""
    do_account = ctx.obj.get_account()

    email = do_account.email
    if not do_account.email_verified:
        email += ' (unverified)'

    status = do_account.status
    if do_account.status_message:
        status += ' ({})'.format(do_account.status_message)

    click_echo_kvp('Email', email)
    click_echo_kvp('Status', status)
    click_echo_kvp('Droplet limit', do_account.droplet_limit)
    click_echo_kvp('Floating IP limit', do_account.floating_ip_limit)
    click_echo_kvp('UUID', do_account.uuid)


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help="Show extra information.")
@click.pass_context
def droplets(ctx, verbose):
    """List your droplets"""
    do_droplets = ctx.obj.get_all_droplets()

    for n, droplet in enumerate(do_droplets, start=1):
        created_at = dateutil.parser.parse(droplet.created_at)

        if droplet.kernel:
            do_os = droplet.kernel.get('name', 'unknown')
        elif droplet.image:
            do_os = '{} {}'.format(droplet.image['distribution'], droplet.image['name'])
        else:
            do_os = 'unknown'

        click.secho(
            '# {} ({})'.format(droplet.name, droplet.status),
            fg='green', bold=True,
        )
        click_echo_kvp('OS', do_os)
        click_echo_kvp('IP', droplet.ip_address)
        click_echo_kvp('CPU', droplet.vcpus)
        click_echo_kvp('Memory', str(droplet.memory) + ' MB')
        click_echo_kvp('Disk', str(droplet.disk) + ' GB')

        if verbose:
            click_echo_kvp('Tags', ', '.join(droplet.tags))
            click_echo_kvp('Backups', 'Yes' if droplet.backups else 'No')
            click_echo_kvp('Locked', 'Yes' if droplet.locked else 'No')
            click_echo_kvp('Monitoring', 'Yes' if droplet.monitoring else 'No')
            click_echo_kvp('Features', ', '.join(droplet.features))
            click_echo_kvp('Region', droplet.region['name'])

        click_echo_kvp('URL', 'https://cloud.digitalocean.com/droplets/{}/graphs'.format(droplet.id))
        click_echo_kvp('Created at', created_at.strftime('%a, %x %X'))

        if n != len(do_droplets):
            click.echo()  # Print a new line between droplets


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help="Show extra information.")
@click.pass_context
def domains(ctx, verbose):
    """List your domains"""
    do_domains = ctx.obj.get_all_domains()

    for n, domain in enumerate(do_domains, start=1):
        # We could use Digital Ocean domain records API endpoint but parsing the zone file is *much* quicker
        zone = dns.zone.from_text(domain.zone_file)

        domain = zone.origin.to_text(omit_final_dot=True)
        click.secho('# {}'.format(domain), fg='green', bold=True)

        for key, value in zone.nodes.items():
            subdomain = key.to_text(omit_final_dot=True)

            for rd in value.rdatasets:
                # Non verbose output only contains A and CNAME records
                if not verbose and rd.rdtype not in [dns.rdatatype.A, dns.rdatatype.CNAME]:
                    continue

                for address in rd:
                    click.echo(
                        '{name:<35} {record_type:<10} {address}'.format(
                            name=subdomain,
                            record_type=dns.rdatatype.to_text(rd.rdtype),
                            address=str(address),
                        )
                    )

        if n != len(do_domains):
            click.echo()  # Print a new line between domains


@cli.command(name='ping-domains')
@click.option('--timeout', '-t', type=int, default=3, help="How many seconds to wait for the server before giving up.")
@click.option('--verbose', '-v', is_flag=True, help="Show extra information.")
@click.pass_context
def ping_domains(ctx, timeout, verbose):
    """Ping your domains and see what's the response"""
    do_domains = ctx.obj.get_all_domains()
    do_droplets = {
        droplet.ip_address: (droplet.name, 'https://cloud.digitalocean.com/droplets/{}/graphs'.format(droplet.id))
        for droplet in ctx.obj.get_all_droplets()
    }

    for n, domain in enumerate(do_domains, start=1):
        # We could use Digital Ocean domain records API endpoint but parsing the zone file is *much* quicker
        zone = dns.zone.from_text(domain.zone_file)

        domain = zone.origin.to_text(omit_final_dot=True)
        click.secho('# {}'.format(domain), fg='green', bold=True)

        for record in zone.nodes:
            absolute_url = record.derelativize(zone.origin).to_text(omit_final_dot=True)
            url_http = 'http://' + absolute_url
            url_https = 'https://' + absolute_url

            for url in [url_http, url_https]:
                click.secho('- {}'.format(url), bold=True)

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
                    # Source: https://stackoverflow.com/a/36357465
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
