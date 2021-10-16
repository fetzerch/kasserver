# kasserver - Manage domains hosted on All-Inkl.com through the KAS server API
# Copyright (c) 2018 Christian Fetzer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Request Let's encrypt certificates for All-Inkl.com domains with lego"""

import logging

import click

import kasserver

LOGGER = logging.getLogger("kasserver_dns_lego")


@click.group()
@click.version_option(kasserver.__version__)
def cli():
    """Request Let's encrypt (wildcard) certificates for All-Inkl.com domains.

    This program is designed to be used with lego
    (https://github.com/xenolf/lego) for resolving Let's encrypt / ACME DNS
    challenges.

    Usage: EXEC_PATH=kasserver-dns-lego lego --dns exec
    --domains foo.example.com --email invalid@example.com run

    See https://github.com/xenolf/lego/blob/master/providers/dns/exec/doc.go
    for more detailed information.
    """
    logging.basicConfig(
        format="%(asctime)s %(name)s: %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        level=logging.INFO,
    )


@cli.command()
@click.argument("fqdn")
@click.argument("value")
@click.argument("ttl", required=False)
def present(fqdn, value, ttl):
    """Add a DNS record for fqdn with value (and ttl)."""
    LOGGER.info(
        "Setting DNS TXT record for domain %s to %s (TTL: %s)", fqdn, value, ttl
    )
    kas = kasserver.KasServer()
    kas.add_dns_record(fqdn, "TXT", value, ttl)


@cli.command()
@click.argument("fqdn")
@click.argument("value")
@click.argument("ttl", required=False)
def cleanup(fqdn, value, ttl):
    """Remove a DNS record for fqdn with value (and ttl)."""
    # pylint: disable=unused-argument
    LOGGER.info("Removing DNS TXT record for domain %s", fqdn)
    kas = kasserver.KasServer()
    kas.delete_dns_record(fqdn, "TXT")
