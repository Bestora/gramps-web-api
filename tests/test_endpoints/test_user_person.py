# tests/test_endpoints/test_user_person.py
"""Tests for linking an account to a person (family mode)."""

import unittest

from gramps_webapi.auth.const import ROLE_EDITOR, ROLE_OWNER

from . import BASE_URL, get_test_client
from .util import fetch_header

KEY = "frontend.userPersons"


class TestUserPerson(unittest.TestCase):
    """PUT /api/users/<name>/person/."""

    @classmethod
    def setUpClass(cls):
        cls.client = get_test_client()

    def _config(self, header):
        rv = self.client.get(BASE_URL + "/trees/-/config", headers=header)
        self.assertEqual(rv.status_code, 200)
        return rv.json.get(KEY, {})

    def test_link_and_clear_own_person(self):
        header = fetch_header(self.client, role=ROLE_EDITOR)
        rv = self.client.put(
            BASE_URL + "/users/-/person/", json={"handle": "H1"}, headers=header
        )
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(self._config(header)["editor"], "H1")
        rv = self.client.put(
            BASE_URL + "/users/-/person/", json={"handle": ""}, headers=header
        )
        self.assertEqual(rv.status_code, 200)
        self.assertNotIn("editor", self._config(header))

    def test_editor_cannot_link_someone_else(self):
        header = fetch_header(self.client, role=ROLE_EDITOR)
        rv = self.client.put(
            BASE_URL + "/users/owner/person/", json={"handle": "H2"}, headers=header
        )
        self.assertEqual(rv.status_code, 403)

    def test_owner_links_another_account_and_keeps_other_config(self):
        header = fetch_header(self.client, role=ROLE_OWNER)
        rv = self.client.put(
            BASE_URL + "/trees/-/config",
            json={"frontend.appTitle": "Familie"},
            headers=header,
        )
        self.assertEqual(rv.status_code, 200)
        rv = self.client.put(
            BASE_URL + "/users/member/person/", json={"handle": "H3"}, headers=header
        )
        self.assertEqual(rv.status_code, 200)
        rv = self.client.get(BASE_URL + "/trees/-/config", headers=header)
        self.assertEqual(rv.json["frontend.appTitle"], "Familie")
        self.assertEqual(rv.json[KEY]["member"], "H3")

    def test_unknown_user(self):
        header = fetch_header(self.client, role=ROLE_OWNER)
        rv = self.client.put(
            BASE_URL + "/users/nobody/person/", json={"handle": "H4"}, headers=header
        )
        self.assertEqual(rv.status_code, 404)
