#
# Gramps Web API - A RESTful API for the Gramps genealogy program
#
# Copyright (C) 2026      Gramps Web contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#

"""Tests for logging in with a share key and a full name."""

import unittest

from gramps_webapi.auth import get_user_details
from gramps_webapi.auth.const import ROLE_EDITOR

from . import BASE_URL, get_single_tree_test_client, get_test_client

SHARE_URL = BASE_URL + "/token/share/"


class TestTokenShare(unittest.TestCase):
    """Test cases for POST /api/token/share/."""

    @classmethod
    def setUpClass(cls):
        cls.client = get_single_tree_test_client()
        cls.client.application.config["SHARE_KEY"] = "s3cret"

    @classmethod
    def tearDownClass(cls):
        cls.client.application.config["SHARE_KEY"] = ""

    def test_creates_editor_on_first_login(self):
        rv = self.client.post(
            SHARE_URL, json={"key": "s3cret", "name": " Max  Müller "}
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn("refresh_token", rv.json)
        with self.client.application.app_context():
            details = get_user_details("max müller")
        self.assertEqual(details["role"], ROLE_EDITOR)
        self.assertEqual(details["full_name"], "Max Müller")
        self.assertTrue(details["tree"])
        # second login reuses the account
        rv = self.client.post(
            SHARE_URL, json={"key": "s3cret", "name": "max müller"}
        )
        self.assertEqual(rv.status_code, 200)

    def test_wrong_key(self):
        rv = self.client.post(SHARE_URL, json={"key": "nope", "name": "Eve"})
        self.assertEqual(rv.status_code, 403)

    def test_cannot_reach_owner(self):
        rv = self.client.post(SHARE_URL, json={"key": "s3cret", "name": "Owner"})
        self.assertEqual(rv.status_code, 403)

    def test_disabled_without_key(self):
        client = get_test_client()
        rv = client.post(SHARE_URL, json={"key": "s3cret", "name": "Eve"})
        self.assertEqual(rv.status_code, 404)
