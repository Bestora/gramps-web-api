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

"""Tests for the page title and description of link previews."""

import unittest

from gramps_webapi.api.util import get_single_tree_id
from gramps_webapi.auth import get_tree_config, set_tree_config

from . import BASE_URL, get_single_tree_test_client

META_URL = BASE_URL + "/site-meta/"


class TestSiteMeta(unittest.TestCase):
    """Test cases for GET /api/site-meta/."""

    @classmethod
    def setUpClass(cls):
        cls.client = get_single_tree_test_client()

    def _set(self, **values):
        with self.client.application.test_request_context():
            tree = get_single_tree_id()
            config = dict(get_tree_config(tree))
            config.update(values)
            set_tree_config(tree=tree, config=config)

    def tearDown(self):
        self._set(**{"frontend.siteTitle": "", "frontend.siteDescription": ""})

    def test_default(self):
        rv = self.client.get(META_URL)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.mimetype, "text/html")
        self.assertIn("<title>Gramps Web</title>", rv.text)

    def test_admin_values_escaped(self):
        self._set(
            **{
                "frontend.siteTitle": "Familie <Müller>",
                "frontend.siteDescription": 'Unser "Baum"',
            }
        )
        rv = self.client.get(META_URL)
        self.assertIn("<title>Familie &lt;Müller&gt;</title>", rv.text)
        self.assertIn(
            '<meta property="og:title" content="Familie &lt;Müller&gt;">', rv.text
        )
        self.assertIn(
            '<meta name="description" content="Unser &quot;Baum&quot;">', rv.text
        )
