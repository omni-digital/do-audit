"""
do-audit command line utility related code
"""
import os

import click
import dateutil.parser
import digitalocean

from do_audit.utils import click_echo_kvp


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

    ctx.obj = digitalocean.Manager(token=token)


@cli.command()
@click.pass_context
def account(ctx):
    """Show your Digital Ocean account basic info"""
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
@click.option('--verbose', '-v', is_flag=True)
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

        click_echo_kvp('Created at', created_at.strftime('%a, %x %X'))

        if n != len(do_droplets):
            click.echo()  # Print a new line between droplets

if __name__ == '__main__':
    cli()
