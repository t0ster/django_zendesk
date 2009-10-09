#! /usr/bin/env python
# -*- coding: utf8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
import django.test
from django.conf import settings

from django_zendesk import views

class ViewsTestCase(django.test.TestCase):
    urls = 'django_zendesk.test_urls'
    
    def setUp(self):
      # Test data so we can get predictable results.
      self.original_zendesk_url, settings.ZENDESK_URL = settings.ZENDESK_URL, "http://example.com"
      self.original_zendesk_token, settings.ZENDESK_TOKEN = settings.ZENDESK_TOKEN, "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    
    def tearDown(self):
      # Reset these in case other unit tests need to use the real values.
      settings.ZENDESK_URL = self.original_zendesk_url
      settings.ZENDESK_TOKEN = self.original_zendesk_token
    
    def testLoginRedirect(self):
        """Test that if no user is logged in, the client is redirected to log in."""
        
        response = self.client.get(reverse(views.authorize))
        self.assertEqual(302, response.status_code)
        self.assertEqual(response['Location'], r'http://testserver%s?next=/authenticate.html' % settings.LOGIN_URL)

    def testNormalAuthentiction(self):
        """Test the regular case."""
        
        u = User.objects.create_user('alice', 'alice@example.com', password='secret')
        u.first_name = "Alice"
        u.last_name = "Smith"
        u.save()

        self.client.login(username='alice', password='secret')
        response = self.client.get(reverse(views.authorize), { 'timestamp': 100 }, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], r'http://example.com/access/remote/?name=Alice%20Smith&email=alice%40example.com&timestamp=100&hash=ce66b7fa9af52738cadab3e964bf5c88')

    def testAnonymous(self):
        """Test a login with no name."""
        
        u = User.objects.create_user('anon', 'anona@example.com', password='secret')
        u.save()

        self.client.login(username='anon', password='secret')
        response = self.client.get(reverse(views.authorize), { 'timestamp': 100 }, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], r'http://example.com/access/remote/?name=Anonymous%20User&email=anona%40example.com&timestamp=100&hash=85dcb5f66e2acd302039656ba16c212a')
        
    def testUtfName(self):
        """Test a login with UTF characters in the name. This requires special URL encoding."""
        
        u = User.objects.create_user('nikos', 'kazantzakis@example.com', password='secret')
        u.first_name = "Δεν ελπίζω τίποτε."
        u.last_name = "Δεν φοβούμαι τίποτε."
        u.save()
        
        self.client.login(username='nikos', password='secret')
        response = self.client.get(reverse(views.authorize), { 'timestamp': 100 }, follow=False)
        self.assertEqual(response.status_code, 302)
        name = urlquote("%s %s" % (u.first_name, u.last_name))
        self.assertEqual(response['Location'], r'%s/access/remote/?name=%s&email=%s&timestamp=100&hash=00d5e1de5c8a20b2d4aeb23c7eb07fe1' % (settings.ZENDESK_URL, name, urlquote(u.email)))
