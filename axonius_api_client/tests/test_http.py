# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.http."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import sys

import pytest
import requests

import axonius_api_client


class TestHttpClient(object):
    """Test axonius_api_client.http.HttpClient."""

    def test_str_repr(self, httpbin_secure):
        """Test str/repr has URL."""
        url = httpbin_secure.url
        http_client = axonius_api_client.http.HttpClient(url=url)
        assert httpbin_secure.url in format(http_client)
        assert httpbin_secure.url in repr(http_client)

    def test_user_agent(self, httpbin_secure):
        """Test user_agent has version in it."""
        url = httpbin_secure.url
        http_client = axonius_api_client.http.HttpClient(url=url)
        assert axonius_api_client.version.__version__ in http_client.user_agent

    def test_not_quiet_urllib(self, httpbin_secure):
        """Test quiet_urllib=False shows warning from urllib3."""
        url = httpbin_secure.url
        http_client = axonius_api_client.http.HttpClient(url=url, quiet_urllib=False)
        with pytest.warns(requests.urllib3.exceptions.InsecureRequestWarning):
            http_client()

    @pytest.mark.skipif(
        sys.version_info < (3, 6), reason="requires python3.6 or higher"
    )
    def test_verify_ca_bundle(self, httpbin_secure, httpbin_ca_bundle):
        """Test quiet_urllib=False no warning from urllib3 when using ca bundle."""
        url = httpbin_secure.url
        http_client = axonius_api_client.http.HttpClient(url=url, quiet_urllib=False)
        response = http_client()
        assert response.status_code == 200

    def test_save_last(self, httpbin_secure):
        """Test last req/resp with save_last=True."""
        url = httpbin_secure.url
        http_client = axonius_api_client.http.HttpClient(url=url, save_last=True)
        response = http_client()
        assert response == http_client.last_response
        assert response.request == http_client.last_request

    def test_save_history(self, httpbin_secure):
        """Test last resp added to history with save_history=True."""
        url = httpbin_secure.url
        http_client = axonius_api_client.http.HttpClient(url=url, save_history=True)
        response = http_client()
        assert response in http_client.history

    def test_logging(self, httpbin_secure, caplog, log_check):
        """Test logging of request/response."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http_client = axonius_api_client.http.HttpClient(url=url)
        http_client()
        entries = [
            "request.*{}".format(httpbin_secure.url + "/"),
            "response.*{}".format(httpbin_secure.url + "/"),
        ]
        log_check(caplog, entries)

    def test_no_logging(self, httpbin_secure, caplog):
        """Test no logging of request/response when attrs are empty."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http_client = axonius_api_client.http.HttpClient(url=url)
        http_client.LOG_REQUEST_ATTRS = []
        http_client.LOG_RESPONSE_ATTRS = []
        assert not caplog.records
