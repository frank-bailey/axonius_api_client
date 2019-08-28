# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
import requests

import axonius_api_client as axonapi

CLASSES = [axonapi.api.Users, axonapi.Devices]

LABELS = ["badwolf_dundundun"]

QUERY_ID_EXISTS = '(specific_data.data.id == ({"$exists":true,"$ne": ""}))'

USERS_FIELD_MANUAL = "specific_data.data.username"
DEVICES_FIELD_MANUAL = "specific_data.data.hostname"
USERS_FIELDS_MANUALS = [USERS_FIELD_MANUAL]
DEVICES_FIELDS_MANUALS = ["specific_data.data.hostname"]

USERS_FIELD_VALIDATE = "username"
USERS_FIELDS_VALIDATES = [USERS_FIELD_VALIDATE]
DEVICES_FIELD_VALIDATE = "hostname"
DEVICES_FIELDS_VALIDATES = [DEVICES_FIELD_VALIDATE]


def need_creds(creds):
    """Pass."""
    if not any(list(creds["creds"].values())):
        pytest.skip("No credentials provided for {cls}: {creds}".format(**creds))


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize(
    "creds", ["creds_user", "creds_key"], indirect=True, scope="class"
)
@pytest.mark.parametrize("apicls", CLASSES, scope="class")
class TestBoth(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, url, creds, apicls):
        """Pass."""
        need_creds(creds)
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()
        api = apicls(auth=auth)
        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)
        assert axonapi.tools.is_type.dict(api._default_fields)
        assert isinstance(api._router, axonapi.api.routers.Router)
        assert isinstance(api.labels, axonapi.api.mixins.Child)
        assert isinstance(api.labels, axonapi.api.users_devices.Labels)
        assert isinstance(api.saved_query, axonapi.api.mixins.Child)
        assert isinstance(api.saved_query, axonapi.api.users_devices.SavedQuery)
        assert isinstance(api.fields, axonapi.api.mixins.Child)
        assert isinstance(api.fields, axonapi.api.users_devices.Fields)
        assert isinstance(api.reports, axonapi.api.mixins.Child)
        assert isinstance(api.reports, axonapi.api.users_devices.Reports)
        assert isinstance(api.adapters, axonapi.api.adapters.Adapters)
        return api

    @pytest.fixture(scope="class")
    def fields_list_manual(self, apiobj):
        """Pass."""
        api_type = apiobj._router._object_type
        if api_type == "users":
            return USERS_FIELDS_MANUALS
        elif api_type == "devices":
            return DEVICES_FIELDS_MANUALS

    @pytest.fixture(scope="class")
    def fields_list_validate(self, apiobj):
        """Pass."""
        api_type = apiobj._router._object_type
        if api_type == "users":
            return USERS_FIELDS_VALIDATES
        elif api_type == "devices":
            return DEVICES_FIELDS_VALIDATES

    @pytest.fixture(scope="class")
    def fields_list_mix(self, apiobj):
        """Pass."""
        api_type = apiobj._router._object_type
        if api_type == "users":
            return USERS_FIELDS_VALIDATES + USERS_FIELDS_MANUALS
        elif api_type == "devices":
            return DEVICES_FIELDS_VALIDATES + DEVICES_FIELDS_MANUALS

    @pytest.fixture(scope="class")
    def fields_dict_manual(self, apiobj):
        """Pass."""
        api_type = apiobj._router._object_type
        if api_type == "users":
            return {"generic": USERS_FIELDS_MANUALS}
        elif api_type == "devices":
            return {"generic": DEVICES_FIELDS_MANUALS}

    @pytest.fixture(scope="class")
    def fields_dict_validate(self, apiobj):
        """Pass."""
        api_type = apiobj._router._object_type
        if api_type == "users":
            return {"generic": USERS_FIELDS_VALIDATES}
        elif api_type == "devices":
            return {"generic": DEVICES_FIELDS_VALIDATES}

    @pytest.fixture(scope="class")
    def fields_dict_mix(self, apiobj):
        """Pass."""
        api_type = apiobj._router._object_type
        if api_type == "users":
            return {"generic": USERS_FIELDS_VALIDATES + USERS_FIELDS_MANUALS}
        elif api_type == "devices":
            return {"generic": DEVICES_FIELDS_VALIDATES + DEVICES_FIELDS_MANUALS}

    @pytest.fixture(scope="class")
    def single_asset(self, apiobj, fields_list_manual):
        """Pass."""
        api_type = apiobj._router._object_type
        data = apiobj._get(page_size=1, fields=fields_list_manual)
        assert axonapi.tools.is_type.dict(data)

        assets = data["assets"]
        assert axonapi.tools.is_type.list(assets)

        if not assets:
            reason = "No {} returned with no fields: {}"
            reason = reason.format(api_type, fields_list_manual)
            pytest.skip(reason=reason)

        assert len(assets) == 1

        asset = assets[0]
        assert axonapi.tools.is_type.dict(asset)

        for x in fields_list_manual:
            assert x in asset

        return asset

    @pytest.fixture(scope="class")
    def single_asset_query(self, single_asset):
        """Pass."""
        asset_id = single_asset["internal_axon_id"]
        return 'internal_axon_id == "{}"'.format(asset_id)

    @pytest.fixture(scope="class")
    def api_fields(self, apiobj):
        """Pass."""
        return apiobj.fields.get()

    @pytest.fixture(scope="class")
    def test_sq_get(self, apiobj):
        """Pass."""
        data = apiobj.saved_query.get()
        assert axonapi.tools.is_type.lod(data)
        for entry in data:
            assert "name" in entry
            assert axonapi.tools.is_type.str(entry["name"])
        return data

    def test__request_json(self, apiobj):
        """Test that JSON is returned when is_json=True."""
        response = apiobj._request(
            path=apiobj._router.fields,
            method="get",
            raw=False,
            is_json=True,
            check_status=True,
        )
        assert axonapi.tools.is_type.dict(response)

    def test__request_raw(self, apiobj):
        """Test that response is returned when raw=True."""
        response = apiobj._request(
            path=apiobj._router.fields,
            method="get",
            raw=True,
            is_json=True,
            check_status=True,
        )
        assert isinstance(response, requests.Response)

    def test__request_text(self, apiobj):
        """Test that str is returned when raw=False and is_json=False."""
        response = apiobj._request(
            path=apiobj._router.fields,
            method="get",
            raw=False,
            is_json=False,
            check_status=True,
        )
        assert axonapi.tools.is_type.str(response)

    def test_not_logged_in(self, url, creds, apicls):
        """Test exc thrown when auth method not logged in."""
        need_creds(creds)
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        with pytest.raises(axonapi.NotLoggedIn):
            apicls(auth=auth)

    @pytest.mark.parametrize("query", [None, QUERY_ID_EXISTS])
    @pytest.mark.parametrize("use_post", [True, False])
    @pytest.mark.parametrize("row_start", [0, 1])
    def test__get(self, apiobj, query, fields_list_manual, use_post, row_start):
        """Test private get."""
        api_type = apiobj._router._object_type
        data = apiobj._get(
            fields=fields_list_manual,
            row_start=row_start,
            page_size=1,
            query=query,
            use_post=use_post,
        )
        assert axonapi.tools.is_type.dict(data)
        assert "assets" in data
        assert axonapi.tools.is_type.list(data["assets"])

        if not data["assets"]:
            msg = "No {t} on system, unable to test _get"
            msg = msg.format(t=api_type)
            pytest.skip(msg)

        assert len(data["assets"]) == 1

        for entry in data["assets"]:
            assert axonapi.tools.is_type.dict(entry)
            assert "adapters" in entry
            for field in fields_list_manual:
                assert field in entry

    @pytest.mark.parametrize("query", [None, QUERY_ID_EXISTS])
    @pytest.mark.parametrize("use_post", [True, False])
    def test_count(self, apiobj, query, use_post):
        """Test count."""
        data = apiobj.count(query=query, use_post=use_post)
        assert axonapi.tools.is_type.int(data)

    def test_get_manual(self, apiobj, fields_list_manual, single_asset_query):
        """Pass."""
        data = apiobj.get(query=single_asset_query, manual_fields=fields_list_manual)
        assert axonapi.tools.is_type.list(data)
        assert len(data) == 1

    def test_get_validate(self, apiobj, fields_dict_mix, single_asset_query):
        """Pass."""
        data = apiobj.get(query=single_asset_query, **fields_dict_mix)
        assert axonapi.tools.is_type.list(data)
        assert len(data) == 1

    @pytest.mark.parametrize("query", [None, 'name == regex("a", "i")'])
    @pytest.mark.parametrize("row_start", [0, 1])
    def test_sq__get_direct(self, apiobj, query, row_start):
        """Test sq private get_direct."""
        data = apiobj.saved_query._get_direct(
            query=query, row_start=row_start, page_size=1
        )
        assert axonapi.tools.is_type.dict(data)
        assert "assets" in data
        assert axonapi.tools.is_type.list(data["assets"])
        assert len(data["assets"]) == 1

        for entry in data["assets"]:
            assert axonapi.tools.is_type.dict(entry)
            assert "name" in entry
            assert axonapi.tools.is_type.str(entry["name"])

    def test_sq__get(self, apiobj):
        """Test sq private get."""
        data = apiobj.saved_query._get()
        assert axonapi.tools.is_type.list(data)
        assert len(data) >= 1

        for entry in data:
            assert axonapi.tools.is_type.dict(entry)
            assert "name" in entry
            assert axonapi.tools.is_type.str(entry["name"])

    def test_sq_get_names(self, apiobj):
        """Test sq get_names."""
        data = apiobj.saved_query.get_names()
        assert axonapi.tools.is_type.list(data)
        assert len(data) >= 1

        for entry in data:
            assert axonapi.tools.is_type.str(entry)

    @pytest.mark.parametrize(
        "sort_field",
        [
            {"users": USERS_FIELD_MANUAL, "devices": DEVICES_FIELD_MANUAL},
            {"users": USERS_FIELD_VALIDATE, "devices": DEVICES_FIELD_VALIDATE},
            {"users": None, "devices": None},
        ],
    )
    def test_sq_create_delete_manual(self, sort_field, fields_list_manual, apiobj):
        """Pass."""
        api_type = apiobj._router._object_type
        api_sort_field = sort_field[api_type]

        name = "BADWOLF {}".format(axonapi.tools.dt.now())

        created = apiobj.saved_query.create(
            name=name,
            query=QUERY_ID_EXISTS,
            sort_field=api_sort_field,
            manual_fields=fields_list_manual,
        )
        assert axonapi.tools.is_type.dict(created)
        assert created["name"] == name

        apiobj.saved_query.delete(name=created["name"])

        with pytest.raises(axonapi.exceptions.ObjectNotFound):
            apiobj.saved_query.get(name=name)

    def test_sq_create_delete_validate(self, fields_dict_validate, apiobj):
        """Pass."""
        name = "BADWOLF {}".format(axonapi.tools.dt.now())

        created = apiobj.saved_query.create(
            name=name, query=QUERY_ID_EXISTS, **fields_dict_validate
        )
        assert axonapi.tools.is_type.dict(created)
        assert created["name"] == name

        apiobj.saved_query.delete(name=created["name"])

        with pytest.raises(axonapi.exceptions.ObjectNotFound):
            apiobj.saved_query.get(name=name)

    def test_sq_create_page_size_invalid(self, apiobj):
        """Pass."""
        with pytest.raises(axonapi.exceptions.ApiError):
            apiobj.saved_query.create(name="BADWOLF", query=None, page_size=99290)

    def test_sq_get_invalid(self, apiobj):
        """Pass."""
        with pytest.raises(axonapi.exceptions.ObjectNotFound):
            apiobj.saved_query.get(name="AJKSLDBIBRASNVOIRHOUHG")

    def test_sq_get_name(self, apiobj, test_sq_get):
        """Pass."""
        name = test_sq_get[0]["name"]
        data = apiobj.saved_query.get(name=name)
        assert axonapi.tools.is_type.dict(data)
        assert "name" in data
        assert axonapi.tools.is_type.str(data["name"])

    def test_sq_get_name_re(self, apiobj, test_sq_get):
        """Pass."""
        name = test_sq_get[0]["name"][0]
        data = apiobj.saved_query.get(name=name, regex=True)
        assert axonapi.tools.is_type.lod(data)
        assert len(data) >= 1

    def test_labels_get(self, apiobj):
        """Pass."""
        data = apiobj.labels.get()
        assert axonapi.tools.is_type.list(data)
        for entry in data:
            assert axonapi.tools.is_type.str(entry)

    def test_labels_add(self, single_asset_query, apiobj):
        """Pass."""
        data = apiobj.labels.add(query=single_asset_query, labels=LABELS)
        assert axonapi.tools.is_type.int(data)
        assert data == 1

    def test_labels_add_by_rows(self, single_asset, apiobj):
        """Pass."""
        data = apiobj.labels.add_by_rows(rows=[single_asset], labels=LABELS)
        assert axonapi.tools.is_type.int(data)
        assert data == 1

    def test_labels_delete(self, single_asset_query, apiobj):
        """Pass."""
        data = apiobj.labels.delete(query=single_asset_query, labels=LABELS)
        assert axonapi.tools.is_type.int(data)
        assert data == 1

    def test_labels_delete_by_rows(self, single_asset, apiobj):
        """Pass."""
        data = apiobj.labels.delete_by_rows(rows=[single_asset], labels=LABELS)
        assert axonapi.tools.is_type.int(data)
        assert data == 1

    def test_fields_get(self, api_fields):
        """Pass."""
        assert axonapi.tools.is_type.dict(api_fields)
        assert "generic" in api_fields

    @pytest.mark.parametrize("adapter_name", ["generic", "active_directory"])
    def test_fields_find_adapter(self, apiobj, api_fields, adapter_name):
        """Pass."""
        name, obj_fields = apiobj.fields.find_adapter(adapter_name, fields=api_fields)
        assert axonapi.tools.is_type.str(name)
        assert axonapi.tools.is_type.dict(obj_fields)

    def test_fields_find_adapter_invalid(self, apiobj, api_fields):
        """Pass."""
        with pytest.raises(axonapi.exceptions.UnknownError):
            apiobj.fields.find_adapter("badwolf", fields=api_fields)

    def test_fields_find_adapter_invalid_noerr(self, apiobj, api_fields):
        """Pass."""
        name, fields = apiobj.fields.find_adapter(
            "badwolf", fields=api_fields, error=False
        )
        assert name.startswith("INVALID_")
        assert fields == {}

    def test_fields_find(self, apiobj, api_fields, fields_list_mix):
        """Pass."""
        for field in fields_list_mix:
            aname, fname = apiobj.fields.find(
                adapter_name="generic", name=field, fields=api_fields
            )
            assert axonapi.tools.is_type.str(aname)
            assert axonapi.tools.is_type.str(fname)
            assert aname == "generic"

    def test_fields_find_invalid_field(self, apiobj, api_fields):
        """Pass."""
        with pytest.raises(axonapi.exceptions.UnknownError):
            apiobj.fields.find(adapter_name="generic", name="AJKSLJAKN")

    def test_fields_find_invalid_field_noerr1(self, apiobj, api_fields):
        """Pass."""
        name, field = apiobj.fields.find(
            adapter_name="generic", name="AJKSLJAKN", error=False
        )
        assert name == "generic"
        assert field == "INVALID_AJKSLJAKN"

    def test_fields_find_invalid_field_noerr2(self, apiobj, api_fields):
        """Pass."""
        name, field = apiobj.fields.find(
            adapter_name="moo", name="AJKSLJAKN", error=False
        )
        assert name == "INVALID_moo"
        assert field == "INVALID_AJKSLJAKN"

    def test_fields_find_invalid_adapter(self, apiobj, api_fields):
        """Pass."""
        with pytest.raises(axonapi.exceptions.UnknownError):
            apiobj.fields.find(adapter_name="SDNJS:LDJGSKLDJF", name="AJKSLJAKN")

    def test_fields_validate_ignores(self, apiobj, api_fields):
        """Pass."""
        kwargs = {"x": [None, set()]}
        data = apiobj.fields.validate(fields=api_fields, default_fields=False, **kwargs)
        assert not data

    def test_fields_validate_ignores_noerr(self, apiobj, api_fields):
        """Pass."""
        kwargs = {"x": ["x"], "y": ["y"], "generic": ["z"]}
        data = apiobj.fields.validate(
            fields=api_fields, default_fields=False, fields_error=False, **kwargs
        )
        assert not data

    def test_fields_validate_nonlist(self, apiobj, api_fields, fields_dict_mix):
        """Pass."""
        data = apiobj.fields.validate(
            fields=api_fields,
            default_fields=False,
            fields_error=False,
            **fields_dict_mix
        )
        assert axonapi.tools.is_type.list(data)
        assert len(data) == 1

    def test_fields_validate(self, apiobj, api_fields, fields_dict_mix):
        """Pass."""
        data = apiobj.fields.validate(
            fields=api_fields, default_fields=False, **fields_dict_mix
        )
        assert axonapi.tools.is_type.list(data)
        assert len(data) == 1
        for entry in data:
            assert axonapi.tools.is_type.str(entry)

    def test_fields_validate_all(self, apiobj, api_fields, fields_dict_mix):
        """Pass."""
        fields_dict_mix["generic"].append("all")
        data = apiobj.fields.validate(
            fields=api_fields, default_fields=False, **fields_dict_mix
        )
        assert axonapi.tools.is_type.list(data)
        assert len(data) == 1
        assert data[0] == "specific_data"

    def test_get_by_id(self, apiobj, single_asset):
        """Pass."""
        data = apiobj.get_by_id(single_asset["internal_axon_id"])
        assert axonapi.tools.is_type.dict(data)
        assert data
        keys = ["generic", "internal_axon_id", "specific", "accurate_for_datetime"]
        for key in keys:
            assert key in data

    def test_get_by_id_fail(self, apiobj):
        """Pass."""
        with pytest.raises(axonapi.exceptions.ObjectNotFound):
            apiobj.get_by_id("BADWOLF")

    def test_get_by_sq(self, apiobj, test_sq_get):
        """Pass."""
        name = test_sq_get[0]["name"]
        data = apiobj.get_by_saved_query(name=name)
        assert axonapi.tools.is_type.list(data)
        assert data
        keys = ["adapter_list_length", "adapters", "internal_axon_id"]
        for entry in data:
            for key in keys:
                assert key in entry

    def test_get_by_fv_re(self, apiobj, fields_dict_manual):
        """Pass."""
        for k, v in fields_dict_manual.items():
            adapter_name = k
            field_name = v[0]
            break

        data = apiobj.get_by_field_value(
            value="a",
            name=field_name,
            adapter_name=adapter_name,
            regex=True,
            **fields_dict_manual
        )
        assert axonapi.tools.is_type.list(data)
        assert data
        keys = ["adapter_list_length", "adapters", "internal_axon_id", field_name]
        for entry in data:
            for key in keys:
                assert key in entry

    def test_get_by_fv(self, apiobj, single_asset, fields_dict_manual):
        """Pass."""
        for k, v in fields_dict_manual.items():
            adapter_name = k
            field_name = v[0]
            break

        field_value = single_asset[field_name]
        if axonapi.tools.is_type.list(field_value):
            field_value = field_value[0]

        data = apiobj.get_by_field_value(
            value=field_value,
            name=field_name,
            adapter_name=adapter_name,
            **fields_dict_manual
        )

        assert axonapi.tools.is_type.dict(data)
        keys = ["adapter_list_length", "adapters", "internal_axon_id", field_name]
        for key in keys:
            assert key in data

    def test_get_by_fv_err(self, apiobj, fields_dict_manual):
        """Pass."""
        for k, v in fields_dict_manual.items():
            adapter_name = k
            field_name = v[0]
            break

        with pytest.raises(axonapi.exceptions.ObjectNotFound):
            apiobj.get_by_field_value(
                value="askdjfsdfsadgasg",
                name=field_name,
                adapter_name=adapter_name,
                **fields_dict_manual
            )


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize(
    "creds", ["creds_user", "creds_key"], indirect=True, scope="class"
)
class TestUsers(object):
    """Pass."""

    FIELDS = ["specific_data.data.username", "specific_data.data.mail"]

    @pytest.fixture(scope="class")
    def apiobj(self, url, creds):
        """Pass."""
        need_creds(creds)
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()
        api = axonapi.api.Users(auth=auth)
        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)
        assert axonapi.tools.is_type.dict(api._default_fields)
        assert isinstance(api._router, axonapi.api.routers.Router)
        assert isinstance(api.labels, axonapi.api.mixins.Child)
        assert isinstance(api.labels, axonapi.api.users_devices.Labels)
        assert isinstance(api.saved_query, axonapi.api.mixins.Child)
        assert isinstance(api.saved_query, axonapi.api.users_devices.SavedQuery)
        assert isinstance(api.fields, axonapi.api.mixins.Child)
        assert isinstance(api.fields, axonapi.api.users_devices.Fields)
        assert isinstance(api.reports, axonapi.api.mixins.Child)
        assert isinstance(api.reports, axonapi.api.users_devices.Reports)
        assert isinstance(api.adapters, axonapi.api.adapters.Adapters)
        return api

    @pytest.fixture(scope="class")
    def single_asset(self, apiobj):
        """Pass."""
        query = '(specific_data.data.username == ({"$exists":true,"$ne": ""})) and (specific_data.data.mail == ({"$exists":true,"$ne": ""}))'  # noqa

        data = apiobj._get(query=query, page_size=1, fields=self.FIELDS)
        assert axonapi.tools.is_type.dict(data)

        assets = data["assets"]
        assert axonapi.tools.is_type.list(assets)

        if not assets:
            reason = "No users returned with no fields: {}"
            reason = reason.format(self.FIELDS)
            pytest.skip(reason=reason)

        assert len(assets) == 1

        asset = assets[0]
        assert axonapi.tools.is_type.dict(asset)

        for x in self.FIELDS:
            assert x in asset
            assert asset[x]

        return asset

    def test_get_by_username(self, apiobj, single_asset):
        """Pass."""
        value = single_asset["specific_data.data.username"]
        value = value[0] if axonapi.tools.is_type.list(value) else value

        data = apiobj.get_by_username(value=value, **{"generic": self.FIELDS})

        assert axonapi.tools.is_type.dict(data)

        for x in self.FIELDS:
            assert x in data
            assert data[x]

    def test_get_by_mail(self, apiobj, single_asset):
        """Pass."""
        value = single_asset["specific_data.data.mail"]
        value = value[0] if axonapi.tools.is_type.list(value) else value

        data = apiobj.get_by_mail(value=value, **{"generic": self.FIELDS})

        assert axonapi.tools.is_type.dict(data)

        for x in self.FIELDS:
            assert x in data
            assert data[x]


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize(
    "creds", ["creds_user", "creds_key"], indirect=True, scope="class"
)
class TestDevices(object):
    """Pass."""

    FIELDS = [
        "specific_data.data.network_interfaces.ips",
        "specific_data.data.network_interfaces.mac",
        "specific_data.data.hostname",
    ]

    @pytest.fixture(scope="class")
    def apiobj(self, url, creds):
        """Pass."""
        need_creds(creds)
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()
        api = axonapi.api.Devices(auth=auth)
        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)
        assert axonapi.tools.is_type.dict(api._default_fields)
        assert isinstance(api._router, axonapi.api.routers.Router)
        assert isinstance(api.labels, axonapi.api.mixins.Child)
        assert isinstance(api.labels, axonapi.api.users_devices.Labels)
        assert isinstance(api.saved_query, axonapi.api.mixins.Child)
        assert isinstance(api.saved_query, axonapi.api.users_devices.SavedQuery)
        assert isinstance(api.fields, axonapi.api.mixins.Child)
        assert isinstance(api.fields, axonapi.api.users_devices.Fields)
        assert isinstance(api.reports, axonapi.api.mixins.Child)
        assert isinstance(api.reports, axonapi.api.users_devices.Reports)
        assert isinstance(api.adapters, axonapi.api.adapters.Adapters)
        return api

    @pytest.fixture(scope="class")
    def single_asset(self, apiobj):
        """Pass."""
        query = '(specific_data.data.network_interfaces.ips == ({"$exists":true,"$ne": ""})) and (specific_data.data.network_interfaces.mac == ({"$exists":true,"$ne": ""})) and (specific_data.data.hostname == ({"$exists":true,"$ne": ""}))'  # noqa

        data = apiobj._get(query=query, page_size=1, fields=self.FIELDS)
        assert axonapi.tools.is_type.dict(data)

        assets = data["assets"]
        assert axonapi.tools.is_type.list(assets)

        if not assets:
            reason = "No devices returned with no fields: {}"
            reason = reason.format(self.FIELDS)
            pytest.skip(reason=reason)

        assert len(assets) == 1

        asset = assets[0]
        assert axonapi.tools.is_type.dict(asset)

        for x in self.FIELDS:
            assert x in asset
            assert asset[x]

        return asset

    def test_get_by_hostname(self, apiobj, single_asset):
        """Pass."""
        value = single_asset["specific_data.data.hostname"]
        value = value[0] if axonapi.tools.is_type.list(value) else value

        data = apiobj.get_by_hostname(value=value, **{"generic": self.FIELDS})

        assert axonapi.tools.is_type.dict(data)

        for x in self.FIELDS:
            assert x in data
            assert data[x]

    def test_get_by_mac(self, apiobj, single_asset):
        """Pass."""
        value = single_asset["specific_data.data.network_interfaces.mac"]
        value = value[0] if axonapi.tools.is_type.list(value) else value

        data = apiobj.get_by_mac(value=value, **{"generic": self.FIELDS})

        assert axonapi.tools.is_type.dict(data)

        for x in self.FIELDS:
            assert x in data
            assert data[x]

    def test_get_by_ip(self, apiobj, single_asset):
        """Pass."""
        value = single_asset["specific_data.data.network_interfaces.ips"]
        value = value[0] if axonapi.tools.is_type.list(value) else value

        data = apiobj.get_by_ip(value=value, **{"generic": self.FIELDS})

        assert axonapi.tools.is_type.dict(data)

        for x in self.FIELDS:
            assert x in data
            assert data[x]


# TODO
# test response error by using invalid route
# test "error" in json response somehow (need to add code for it too)
# test invalid json response somehow
# test validate fields_error=False
# test parser fields
# test in subnet/not in subnet
# test check_count logic