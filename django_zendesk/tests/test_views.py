#! /usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import skipIf

from ..views import authorize

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from django.urls import reverse

User = get_user_model()


class ViewsTestCase(TestCase):
    def setUp(self):
        # Test data so we can get predictable results.
        self.original_zendesk_url, settings.ZENDESK_URL = settings.ZENDESK_URL, "http://example.com"
        self.original_zendesk_token, settings.ZENDESK_TOKEN = (
            settings.ZENDESK_TOKEN,
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        )

    def tearDown(self):
        # Reset these in case other unit tests need to use the real values.
        settings.ZENDESK_URL = self.original_zendesk_url
        settings.ZENDESK_TOKEN = self.original_zendesk_token

    def testLoginRedirect(self):
        """Test that if no user is logged in, the client is redirected to log in."""

        response = self.client.get(reverse(authorize))
        self.assertEqual(302, response.status_code)
        self.assertEqual(response["Location"], "/accounts/login/?next=/zendesk-auth/")

    def testNormalAuthentiction(self):
        """Test the regular case."""

        u = User.objects.create_user("alice", "alice@example.com", password="secret", id=9999)
        u.first_name = "Alice"
        u.last_name = "Smith"
        u.save()

        self.client.login(username="alice", password="secret")
        response = self.client.get(reverse(authorize), {"timestamp": 100}, follow=False)
        self.assertEqual(response.status_code, 302)
        expected = (
            "http://example.com/access/remoteauth/?name=Alice%20Smith&email=alice%40"
            "example.com&timestamp=100&hash=4e664407c589a777c397e162adac48a6&external_id=9999"
        )
        self.assertEqual(response["Location"], expected)

    def testAnonymous(self):
        """Test a login with no name."""

        u = User.objects.create_user("anon", "anona@example.com", password="secret", id=8888)
        u.save()

        self.client.login(username="anon", password="secret")
        response = self.client.get(reverse(authorize), {"timestamp": 100}, follow=False)
        self.assertEqual(response.status_code, 302)
        expected = (
            "http://example.com/access/remoteauth/?name=&email=anona%40"
            "example.com&timestamp=100&hash=e05da187b803cd1a1e282ad443c47198&external_id=8888"
        )
        self.assertEqual(response["Location"], expected)

    @skipIf(
        settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql",
        "Only can be run on SQLite Engine - it works on MySQL in practice but not in tests",
    )
    def testUtfName(self):
        """Test a login with UTF characters in the name. This requires special URL encoding."""

        u = User.objects.create_user("nikos", "kazantzakis@example.com", password="secret", id=7777)
        u.first_name = "Δεν ελπίζω τίποτε."
        u.last_name = "Δεν φοβούμαι τίποτε."
        u.save()

        self.client.login(username="nikos", password="secret")
        response = self.client.get(reverse(authorize), {"timestamp": 100}, follow=False)
        self.assertEqual(response.status_code, 302)
        expected = (
            "http://example.com/access/remoteauth/?name=%CE%94%CE%B5%CE%BD%20%CE%B5%CE%BB"
            "%CF%80%CE%AF%CE%B6%CF%89%20%CF%84%CE%AF%CF%80%CE%BF%CF%84%CE%B5.%20%CE%94%CE"
            "%B5%CE%BD%20%CF%86%CE%BF%CE%B2%CE%BF%CF%8D%CE%BC%CE%B1%CE%B9%20%CF%84%CE%AF"
            "%CF%80%CE%BF%CF%84%CE%B5.&email=kazantzakis%40example.com&timestamp=100&"
            "hash=c5db7d74fd2e1468cbc4f6878f16e752&external_id=7777"
        )
        self.assertEqual(response["Location"], expected)
