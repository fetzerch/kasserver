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

"""Tests for KasServer"""

import json
import logging

from unittest import mock

import pytest
import zeep

from kasserver import KasServer


LOGGER = logging.getLogger(__name__)

USERNAME = "username"
PASSWORD = "password"

# pylint: disable=protected-access
# pylint: disable=attribute-defined-outside-init
# pylint: disable=too-few-public-methods


class TestKasServerCredentials:
    """Unit tests for credentials"""

    @staticmethod
    @mock.patch.dict(
        "os.environ", {"KASSERVER_USER": USERNAME, "KASSERVER_PASSWORD": PASSWORD}
    )
    @mock.patch("netrc.netrc", autospec=True)
    def test_getcredentials_from_env(netrc):
        """Test getting credentials from env variables"""
        netrc.side_effect = FileNotFoundError("")
        server = KasServer()
        assert server._username == USERNAME
        assert server._password == PASSWORD

    @staticmethod
    @mock.patch.dict("os.environ", {})
    @mock.patch("netrc.netrc", autospec=True)
    def test_getcredentials_from_netrc(netrc):
        """Test getting credentials from netrc file"""
        netrc.return_value.authenticators.return_value = (USERNAME, "", PASSWORD)
        server = KasServer()
        assert server._username == USERNAME
        assert server._password == PASSWORD

    @staticmethod
    @mock.patch.dict("os.environ", {})
    @mock.patch("netrc.netrc", autospec=True)
    def test_getcredentials_failed_netrc(netrc):
        """Test failed getting credentials from netrc file"""
        netrc.side_effect = FileNotFoundError("")
        server = KasServer()
        assert not server._username
        assert not server._password


class TestKasServer:
    """Unit tests for KasServer"""

    REQUEST_TYPE = "test_request"
    REQUEST_PARAMS = {"test_param": 1}

    RESPONSE = [
        {},
        {
            "key": "Response",
            "value": {
                "item": [
                    {},
                    {},
                    {
                        "key": "ReturnInfo",
                        "value": {
                            "_value_1": [
                                {
                                    "item": [
                                        {"key": "record_zone", "value": "example.com"},
                                        {"key": "record_name", "value": "www"},
                                        {"key": "record_type", "value": "A"},
                                        {"key": "record_data", "value": "1.2.3.4"},
                                        {"key": "record_aux", "value": "0"},
                                        {"key": "record_id", "value": "1"},
                                        {"key": "record_changeable", "value": "N"},
                                    ]
                                },
                                {
                                    "item": [
                                        {"key": "record_zone", "value": "example.com"},
                                        {"key": "record_name", "value": "test"},
                                        {"key": "record_type", "value": "CNAME"},
                                        {
                                            "key": "record_data",
                                            "value": "www.example.com",
                                        },
                                        {"key": "record_aux", "value": "0"},
                                        {"key": "record_id", "value": "2"},
                                        {"key": "record_changeable", "value": "Y"},
                                    ]
                                },
                            ]
                        },
                    },
                ]
            },
        },
    ]

    RESPONSE_PARSED = [
        {
            "id": "1",
            "name": "www",
            "zone": "example.com",
            "type": "A",
            "data": "1.2.3.4",
            "aux": "0",
            "changeable": "N",
        },
        {
            "id": "2",
            "name": "test",
            "zone": "example.com",
            "type": "CNAME",
            "data": "www.example.com",
            "aux": "0",
            "changeable": "Y",
        },
    ]

    @pytest.fixture()
    def kasserver(self, mocker):
        """Fixture that sets up a KasServer instance with mocked KasApi"""
        mocker.patch.dict(
            "os.environ", {"KASSERVER_USER": USERNAME, "KASSERVER_PASSWORD": PASSWORD}
        )
        mocker.patch("netrc.netrc", autospec=True)
        mocker.patch("zeep.Client", autospec=True)
        KasServer.FLOOD_TIMEOUT = 0
        kasserver = KasServer()
        kasserver._client.service.KasApi.return_value = self.RESPONSE
        return KasServer()

    @staticmethod
    @pytest.fixture()
    def kasapi(kasserver):
        """Fixture to retrieve mocked KasApi from KasServer"""
        kasapi = kasserver._client.service.KasApi

        def _requests_contains(request_type):
            print("111111", kasapi.call_args_list)
            return any(
                json.loads(args[0])["KasRequestType"] == request_type
                for args, _ in kasapi.call_args_list
            )

        kasapi.requests_contains.side_effect = _requests_contains

        return kasapi

    def test_request(self, kasserver, kasapi):
        """Tests requesting data from KasServer"""
        kasserver._request(self.REQUEST_TYPE, self.REQUEST_PARAMS)
        request = {
            "KasUser": USERNAME,
            "KasAuthType": "plain",
            "KasAuthData": PASSWORD,
            "KasRequestType": self.REQUEST_TYPE,
            "KasRequestParams": self.REQUEST_PARAMS,
        }
        kasapi.assert_called_once_with(json.dumps(request))

    def test_request_failed(self, kasserver, kasapi):
        """Test failed request from KasServer"""
        kasapi.side_effect = zeep.exceptions.Fault("failed")
        with pytest.raises(zeep.exceptions.Fault):
            kasserver._request(self.REQUEST_TYPE, self.REQUEST_PARAMS)

    def test_request_floodprotection(self, kasserver, kasapi):
        """Test request retries when hitting KasServer flood protection"""
        floodprotection = mock.PropertyMock(text="0.0")
        kasapi.side_effect = [
            zeep.exceptions.Fault("flood_protection", detail=floodprotection),
            mock.DEFAULT,
        ]
        kasserver._request(self.REQUEST_TYPE, self.REQUEST_PARAMS)
        assert kasapi.call_count == 2

    def test_getdnsrecords(self, kasserver):
        """Test getting DNS record list"""
        assert kasserver.get_dns_records("example.com") == self.RESPONSE_PARSED

    def test_getdnsrecord(self, kasserver):
        """Test getting single DNS record"""
        assert (
            kasserver.get_dns_record("www.example.com", "A") == self.RESPONSE_PARSED[0]
        )

    @staticmethod
    def test_getdnsrecord_notfound(kasserver):
        """Test getting single DNS record"""
        assert not kasserver.get_dns_record("www.example.com", "MX")

    @staticmethod
    def test_adddnsrecord(kasserver, kasapi):
        """Test adding a new DNS record"""
        kasserver.add_dns_record("test1.example.com", "CNAME", "www.example.com")
        assert kasapi.requests_contains("add_dns_settings")

    @staticmethod
    def test_updatednsrecord(kasserver, kasapi):
        """Test updating an existing new DNS record"""
        kasserver.add_dns_record("test.example.com", "CNAME", "www.example2.com")
        assert kasapi.requests_contains("update_dns_settings")

    @staticmethod
    def test_deletednsrecord(kasserver, kasapi):
        """Test deleting an existing DNS record"""
        kasserver.delete_dns_record("test.example.com", "CNAME")
        assert kasapi.requests_contains("delete_dns_settings")

    @staticmethod
    def test_deletedbsrecord_notfound(kasserver, kasapi):
        """Test deleting a non existent DNS record"""
        kasserver.delete_dns_record("test.example.com", "MX")
        assert not kasapi.requests_contains("delete_dns_settings")


class TestKasServerUtils:
    """Unit tests for utilities"""

    @staticmethod
    def test_split_dqdn():
        """Tests splitting FQDN into dns_name and zone_host values."""
        assert KasServer._split_fqdn("hallo.welt.de.") == ("hallo", "welt.de.")
        assert KasServer._split_fqdn("hallo.welt.de") == ("hallo", "welt.de.")
        assert KasServer._split_fqdn("test.hallo.welt.de") == ("test.hallo", "welt.de.")
        assert KasServer._split_fqdn("hallowelt.de") == ("", "hallowelt.de.")
        with pytest.raises(ValueError):
            KasServer._split_fqdn("")
