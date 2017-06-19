# -*- coding: utf-8 -*-
"""
do-audit DigitalOcean API related code
"""
from __future__ import unicode_literals

import dateutil.parser
import dns.zone
import tablib

from do_audit.utils import yes_no, droplet_url


def create_accounts_dataset(account, verbose=False):
    """
    Create DigitalOcean account dataset

    :param account: DigitalOcean account
    :type account: digitalocean.Account.Account
    :param verbose: if account information should be verbose
    :type verbose: bool
    :returns: account dataset
    :rtype: tablib.Dataset
    """
    email = account.email
    if not account.email_verified:
        email += ' (unverified)'

    status = account.status
    if account.status_message:
        status += ' ({})'.format(account.status_message)

    # Create dataset with the data we want
    headers = ['Email', 'Status', 'Droplet limit']
    row = [email, status, account.droplet_limit]
    if verbose:
        headers += ['Floating IP limit', 'UUID']
        row += [account.floating_ip_limit, account.uuid]

    dataset = tablib.Dataset(headers=headers)
    dataset.append(row)

    return dataset


def create_droplets_dataset(droplets, verbose=False):
    """
    Create DigitalOcean droplets dataset

    :param droplets: list of DigitalOcean droplets
    :type droplets: list of digitalocean.Droplet.Droplet
    :param verbose: if droplets information should be verbose
    :type verbose: bool
    :returns: droplets dataset
    :rtype: tablib.Dataset
    """
    headers = ['Name', 'Status', 'OS', 'IP', 'CPU', 'Memory', 'Disk']
    if verbose:
        headers += ['Tags', 'Backups', 'Locked', 'Monitoring', 'Features', 'Region']
    headers += ['URL', 'Created at']

    dataset = tablib.Dataset(headers=headers)

    for droplet in droplets:
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

    return dataset


def create_domains_dataset(domains, verbose=False):
    """
    Create DigitalOcean domains dataset

    :param domains: list of DigitalOcean domains
    :type domains: list of digitalocean.Domain.Domain
    :param verbose: if domains information should be verbose
    :type verbose: bool
    :returns: domains dataset
    :rtype: tablib.Dataset
    """
    headers = ['Domain', 'Subdomain', 'Record type', 'Destination']
    dataset = tablib.Dataset(headers=headers)

    for domain in domains:
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

    return dataset
