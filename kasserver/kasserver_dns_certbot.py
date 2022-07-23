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

"""Request Let's encrypt certificates for All-Inkl.com domains with Certbot"""

import logging

import click

import kasserver

LOGGER = logging.getLogger("kasserver_dns_certbot")


@click.command()
@click.argument("fqdn", envvar="CERTBOT_DOMAIN")
@click.argument("value", envvar="CERTBOT_VALIDATION")
@click.version_option(kasserver.__version__)
def cli(fqdn, value):
    """Request Let's encrypt (wildcard) certificates for All-Inkl.com domains.

    This program is designed to be used with Certbot (https://certbot.eff.org)
    for resolving Let's encrypt / ACME DNS challenges.

    Usage: certbot certonly -d foo.exmaple.com --preferred-challenges dns
    --manual --manual-auth-hook kasserver-dns-certbot
    --manual-cleanup-hook kasserver-dns-certbot -m invalid@example.com

    See https://certbot.eff.org/docs/using.html#hooks more detailed
    information."""
    logging.basicConfig(level=logging.INFO)
    LOGGER.info("Received request for fqdn %s and value %a", fqdn, value)
    kas = kasserver.KasServer()
    fqdn = f"_acme-challenge.{fqdn}"
    record = kas.get_dns_record(fqdn, "TXT")
    if record:
        LOGGER.info(
            "Removing existing DNS TXT record for domain %s with value %s",
            fqdn,
            record["data"],
        )
        kas.delete_dns_record(fqdn, "TXT")
    if not record or record["data"] != value:
        LOGGER.info("Setting DNS TXT record for domain %s to %s", fqdn, value)
        kas.add_dns_record(fqdn, "TXT", value)
