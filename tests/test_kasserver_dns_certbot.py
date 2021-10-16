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

"""Tests for kasserver_dns_certbot cli"""

from unittest import mock

import click
import click.testing
import pytest

from kasserver.kasserver_dns_certbot import cli


RECORD_FQDN = "new.example.com"
RECORD_FQDN_ACME = f"_acme-challenge.{RECORD_FQDN}"
RECORD_VALUE = "123456"
RECORD_VALUE_DIFFERENT = "654321"
RECORD_TYPE = "TXT"


@mock.patch("kasserver.KasServer", autospec=True)
@pytest.mark.parametrize(
    "record,expected",
    [
        (
            None,
            [
                {
                    "method": "add_dns_record",
                    "args": [RECORD_FQDN_ACME, RECORD_TYPE, RECORD_VALUE],
                }
            ],
        ),
        (
            {"data": RECORD_VALUE},
            [{"method": "delete_dns_record", "args": [RECORD_FQDN_ACME, RECORD_TYPE]}],
        ),
        (
            {"data": RECORD_VALUE_DIFFERENT},
            [
                {
                    "method": "delete_dns_record",
                    "args": [RECORD_FQDN_ACME, RECORD_TYPE],
                },
                {
                    "method": "add_dns_record",
                    "args": [RECORD_FQDN_ACME, RECORD_TYPE, RECORD_VALUE],
                },
            ],
        ),
    ],
)
def test_authentication_cleanup(kasserver, record, expected):
    """Test the authentication and cleanup"""
    kasserver.return_value.get_dns_record.return_value = record
    result = click.testing.CliRunner().invoke(cli, [RECORD_FQDN, RECORD_VALUE])
    assert result.exit_code == 0
    print(kasserver.mock_calls)
    all(
        getattr(kasserver.return_value, call["method"]).assert_any_call(*call["args"])
        for call in expected
    )
