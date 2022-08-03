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

"""Manage domains hosted on All-Inkl.com through the KAS server API"""

import json
import hashlib
import logging
import math
import netrc
import os
import time

import pbr.version
import zeep
import zeep.helpers

__version__ = pbr.version.VersionInfo("kasserver").release_string()

LOGGER = logging.getLogger(__name__)


class KasServer:
    """Manage domains hosted on All-Inkl.com through the KAS server API"""

    FLOOD_TIMEOUT = 1

    def __init__(self):
        wsdl_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "KasApi.wsdl"
        )
        self._client = zeep.Client(wsdl_file)
        self._get_credentials()

    def _get_credentials(self):
        self._username = os.environ.get("KASSERVER_USER", None)
        self._password = os.environ.get("KASSERVER_PASSWORD", None)
        if self._username:
            return

        server = "kasapi.kasserver.com"
        try:
            info = netrc.netrc().authenticators(server)
            self._username = info[0]
            self._password = info[2]
        except (FileNotFoundError, netrc.NetrcParseError) as err:
            LOGGER.warning(
                "Cannot load credentials for %s from .netrc: %s", server, err
            )

    def _request(self, request, params):
        request = {
            "KasUser": self._username,
            "KasAuthType": "plain",
            "KasAuthData": self._password,
            "KasRequestType": request,
            "KasRequestParams": params,
        }

        def _send_request(request):
            try:
                result = self._client.service.KasApi(json.dumps(request))
                time.sleep(KasServer.FLOOD_TIMEOUT)
                return result
            except zeep.exceptions.Fault as exc:
                if exc.message == "flood_protection":
                    timeout = (
                        math.ceil(float(exc.detail.text)) + KasServer.FLOOD_TIMEOUT
                    )
                    LOGGER.warning("Hit flood protection, retrying in %ds", timeout)
                    time.sleep(timeout)
                    return _send_request(request)
                raise

        return _send_request(request)

    @staticmethod
    def _split_fqdn(fqdn):
        """Split a FQDN into record_name and zone_name values"""
        if not fqdn:
            raise ValueError("Error: No valid FQDN given.")
        split_dns = fqdn.rstrip(".").rsplit(".", 2)
        return "".join(split_dns[:-2]), ".".join(split_dns[-2:]) + "."

    def get_dns_records(self, fqdn):
        """Get list of DNS records."""
        _, zone_name = self._split_fqdn(fqdn)
        res = self._request("get_dns_settings", {"zone_host": zone_name})

        # Put the DNS records into a list of dicts
        items = res[1]["value"]["item"][2]["value"]["_value_1"]
        result = []
        for item in items:
            result.append(
                {i["key"].split("_", 1)[-1]: i["value"] for i in item["item"]}
            )
        return result

    def get_dns_record(self, fqdn, record_type):
        """Get a specific DNS record for a FQDN and type"""
        record_name, zone_name = self._split_fqdn(fqdn)
        result = self.get_dns_records(zone_name)
        for item in result:
            if item["name"] == record_name and item["type"] == record_type:
                return item
        return None

    def add_dns_record(self, fqdn, record_type, record_data, record_aux=None):
        """Add or update an DNS record"""
        record_name, zone_name = self._split_fqdn(fqdn)
        params = {
            "zone_host": zone_name,
            "record_name": record_name,
            "record_type": record_type,
            "record_data": record_data,
            "record_aux": record_aux if record_aux else "0",
        }
        existing_record = self.get_dns_record(fqdn, record_type)
        if existing_record:
            params["record_id"] = existing_record["id"]
            self._request("update_dns_settings", params)
        else:
            self._request("add_dns_settings", params)

    def delete_dns_record(self, fqdn, record_type):
        """Removes an existing DNS record"""
        existing_record = self.get_dns_record(fqdn, record_type)
        if existing_record:
            self._request("delete_dns_settings", {"record_id": existing_record["id"]})
