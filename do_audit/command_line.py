"""
do-audit command line utility related code
"""
import os

import click
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
    ctx.obj = dict()
    ctx.obj['token'] = access_token or os.getenv(DO_ACCESS_TOKEN_ENV)

    if not ctx.obj['token']:
        raise click.ClickException(
            "You need to either pass your Digital Ocean access token explicitly ('-t ...') "
            "or set is as an environment variable ('export {DO_ACCESS_TOKEN_ENV}=...').".format(
                DO_ACCESS_TOKEN_ENV=DO_ACCESS_TOKEN_ENV,
            )
        )


@cli.command()
@click.pass_context
def account(ctx):
    """Show your Digital Ocean account basic info"""
    do_account = digitalocean.Account.get_object(ctx.obj['token'])

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


if __name__ == '__main__':
    cli()
