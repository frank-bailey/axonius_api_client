# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.auth."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

import axonius_api_client


DEVICE_FIELDS = {
    "generic": [
        {"name": "specific_data.data.hostname", "title": "Host Name", "type": "string"}
    ],
    "specific": {
        "known_adapter": [
            {
                "name": "adapters_data.known_adapter.hostname",
                "title": "Host Name",
                "type": "string",
            }
        ]
    },
}


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize("creds", ["creds_user", "creds_key"], indirect=True)
class TestApiClient(object):
    """Test axonius_api_client.api.ApiClient."""

    @pytest.fixture(scope="session")
    def api_client(self, api_url, creds):
        """Get an API client."""
        auth_cls = creds.pop("cls")
        if not any(list(creds.values())):
            pytest.skip("No credentials provided for {}: {}".format(auth_cls, creds))
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = auth_cls(http_client=http_client, **creds)
        api_client = axonius_api_client.api.ApiClient(auth=auth)
        return api_client

    def test_str_repr(self, api_client):
        """Test str/repr has URL."""
        assert "auth" in format(api_client)
        assert "auth" in repr(api_client)

    def test_get_device_fields(self, api_client):
        """Test devices/fields API call."""
        fields = api_client.get_device_fields()
        assert isinstance(fields, dict)
        assert "specific" in fields
        assert "generic" in fields
        assert "schema" in fields

    def test_get_user_fields(self, api_client):
        """Test users/fields API call."""
        fields = api_client.get_user_fields()
        assert isinstance(fields, dict)
        assert "specific" in fields
        assert "generic" in fields
        assert "schema" in fields

    @pytest.mark.parametrize(
        "fields",
        [
            {
                "fields": {"generic": ["hostname", "specific_data.data.hostname"]},
                "expected": ["specific_data.data.hostname"],
            },
            {
                "fields": {"generic": ["hostname"]},
                "expected": ["specific_data.data.hostname"],
            },
            {
                "fields": {"generic": ["hostname"], "known_adapter": ["hostname"]},
                "expected": [
                    "specific_data.data.hostname",
                    "adapters_data.known_adapter.hostname",
                ],
            },
        ],
    )
    def test__validate_fields_valid(self, api_client, fields):
        """Test valid dup fields dont show up and prefix gets added properly."""
        device_fields = {}
        device_fields.update(api_client.get_device_fields())
        # this should be monkey patched but... shrug
        device_fields["specific"].update(DEVICE_FIELDS["specific"])

        r = api_client._validate_fields(known_fields=device_fields, **fields["fields"])
        assert r == fields["expected"]

    def test__validate_fields_invalid_field(self, api_client):
        """Test exc thrown when invalid generic field supplied."""
        device_fields = api_client.get_device_fields()
        with pytest.raises(axonius_api_client.exceptions.UnknownFieldName):
            api_client._validate_fields(
                known_fields=device_fields, generic=["this_wont_exist_yo"]
            )

    def test__validate_fields_invalid_adapter(self, api_client):
        """Test exc thrown when invalid adapter name supplied."""
        device_fields = api_client.get_device_fields()
        with pytest.raises(axonius_api_client.exceptions.UnknownAdapterName):
            api_client._validate_fields(
                known_fields=device_fields,
                generic=["hostname"],
                this_wont_exist_yo=["hostname"],
            )

    def test__get_devices_no_query_no_fields(self, api_client):
        """Test private get_devices method without query or fields."""
        r = api_client._get_devices(query=None, fields=None, row_start=0, page_size=1)
        assert "assets" in r
        if r["assets"]:
            for i in r["assets"]:
                assert "adapters" in i
                assert "specific_data" in i

    @pytest.mark.parametrize(
        "fields",
        [
            [
                "specific_data.data.hostname",
                "specific_data.data.network_interfaces.ips",
            ],
            "specific_data.data.hostname,specific_data.data.network_interfaces.ips",
        ],
    )
    @pytest.mark.parametrize(
        "query", [None, '(specific_data.data.id == ({"$exists":true,"$ne": ""}))']
    )
    def test__get_devices(self, api_client, query, fields):
        """Test private get_devices method."""
        r = api_client._get_devices(
            query=query, fields=fields, row_start=0, page_size=1
        )
        assert "assets" in r
        for i in r["assets"]:
            assert "adapters" in i
            assert "internal_axon_id" in i
            assert "specific_data.data.hostname" in i
            assert "specific_data.data.network_interfaces.ips" in i

    @pytest.mark.parametrize(
        "query", [None, '(specific_data.data.id == ({"$exists":true,"$ne": ""}))']
    )
    def test_get_devices_no_fields(self, api_client, query):
        """Test private get_devices method with default fields."""
        for dvc in api_client.get_devices(query=query, page_size=1, max_rows=2):
            assert "specific_data.data.hostname" in dvc
            assert "specific_data.data.network_interfaces.ips" in dvc
            # not every dvc will have "specific_data.data.network_interfaces.macs"
            # FUTURE: add cmd line option for adapter fields
            # --adapter_fields cisco:hostname,network_interfaces.ips

    def test_get_device_by_id_valid(self, api_client):
        """Test get_device_by_id with a valid dvc id."""
        dvcs = api_client._get_devices(page_size=1)
        for dvc in dvcs["assets"]:
            full_dvc = api_client.get_device_by_id(id=dvc["internal_axon_id"])
            assert "generic" in full_dvc
            assert "specific" in full_dvc

    def test_get_device_by_id_invalid(self, api_client):
        """Test get_device_by_id with an invalid dvc id."""
        with pytest.raises(axonius_api_client.exceptions.DeviceIDNotFound):
            api_client.get_device_by_id(id="this_wont_work_yo")

    def test_get_device_count(self, api_client):
        """Test devices/count API call."""
        r = api_client.get_device_count()
        assert isinstance(r, int)

    def test_get_device_count_query(self, api_client):
        """Test devices/count API call with query (unable to assume greater than 0)."""
        r = api_client.get_device_count(
            query='(specific_data.data.id == ({"$exists":true,"$ne": ""}))'
        )
        assert isinstance(r, int)

    def test_get_device_count_query_0(self, api_client):
        """Test devices/count API call with query that should return 0."""
        r = api_client.get_device_count(
            query='(specific_data.data.id == ({"$exists":false,"$ne": ""}))'
        )
        assert r == 0


@pytest.mark.parametrize("adapter", ["known", "known_adapter"])
class TestFindAdapter(object):
    """Test axonius_api_client.api.find_adapter."""

    @pytest.mark.parametrize("known_names", [None, ["known_adapter"]])
    def test_valid(self, adapter, known_names):
        """Test that _adapter gets added properly."""
        r = axonius_api_client.api.find_adapter(name=adapter, known_names=known_names)
        assert r == "known_adapter"

    def test_invalid(self, adapter):
        """Test exc thrown when name not in known_names."""
        with pytest.raises(axonius_api_client.exceptions.UnknownAdapterName):
            axonius_api_client.api.find_adapter(
                name=adapter, known_names=["other_known_adapter"]
            )


class TestFindFieldGeneric(object):
    """Test axonius_api_client.api.find_field with generic fields."""

    @pytest.mark.parametrize("fields", [None, DEVICE_FIELDS])
    @pytest.mark.parametrize("field", ["hostname", "specific_data.data.hostname"])
    def test_valid(self, field, fields):
        """Test field name found and/or prefixed properly."""
        r = axonius_api_client.api.find_field(
            name=field, adapter="generic", fields=fields
        )
        assert r == "specific_data.data.hostname"

    def test_invalid(self):
        """Test exc thrown when field not in DEVICE_FIELDS."""
        with pytest.raises(axonius_api_client.exceptions.UnknownFieldName):
            axonius_api_client.api.find_field(
                name="unknown_field", adapter="generic", fields=DEVICE_FIELDS
            )


@pytest.mark.parametrize("adapter", ["known", "known_adapter"])
class TestFindFieldAdapter(object):
    """Test axonius_api_client.api.find_field with adapter fields."""

    @pytest.mark.parametrize("fields", [None, DEVICE_FIELDS])
    @pytest.mark.parametrize(
        "field", ["hostname", "adapters_data.known_adapter.hostname"]
    )
    def test_valid(self, adapter, field, fields):
        """Test field name found and/or prefixed properly."""
        r = axonius_api_client.api.find_field(
            name=field, fields=fields, adapter=adapter
        )
        assert r == "adapters_data.known_adapter.hostname"

    def test_invalid(self, adapter):
        """Test exc thrown when field not in DEVICE_FIELDS."""
        with pytest.raises(axonius_api_client.exceptions.UnknownFieldName):
            axonius_api_client.api.find_field(
                name="unknown_field", fields=DEVICE_FIELDS, adapter=adapter
            )