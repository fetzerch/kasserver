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

"""Tests for kasserver_dns cli"""

from unittest import mock

import click
import click.testing
import pytest

from kasserver.kasserver_dns import cli
from .test_kasserver import TestKasServer


RECORD_FQDN = "new.example.com"
RECORD_VALUE = "123456"
RECORD_TYPE = "CNAME"
RECORD_TTL = "10"


@mock.patch("kasserver.KasServer", autospec=True)
def test_list(kasserver):
    """Test the list command"""
    kasserver.return_value.get_dns_records.return_value = TestKasServer.RESPONSE_PARSED
    result = click.testing.CliRunner().invoke(cli, ["list", "example.com"])
    assert result.exit_code == 0
    assert "example.com" in result.output


@mock.patch("kasserver.KasServer", autospec=True)
@pytest.mark.parametrize(
    "command,expected",
    [
        (
            "add",
            {
                "method": "add_dns_record",
                "params": ["--ttl", RECORD_TTL, RECORD_FQDN, RECORD_TYPE, RECORD_VALUE],
                "args": [RECORD_FQDN, RECORD_TYPE, RECORD_VALUE, RECORD_TTL],
            },
        ),
        (
            "remove",
            {
                "method": "delete_dns_record",
                "params": [RECORD_FQDN, RECORD_TYPE],
                "args": [RECORD_FQDN, RECORD_TYPE],
            },
        ),
    ],
)
def test_add_remove(kasserver, command, expected):
    """Test the add and remove command"""
    result = click.testing.CliRunner().invoke(cli, [command, *expected["params"]])
    assert result.exit_code == 0
    getattr(kasserver.return_value, expected["method"]).assert_any_call(
        *expected["args"]
    )
