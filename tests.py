#! /usr/bin/env python
# -*- coding: utf8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import django.test
from django.conf import settings

from django_zendesk import views

class ViewsTestCase(django.test.TestCase):
    urls = 'django_zendesk.test_urls'
    
    def testLoginRedirect(self):
        """Test that if no user is logged in, the client is redirected to log in."""
        
        response = self.client.get(reverse(views.authorize))
        self.assertEqual(302, response.status_code)
        self.assertEqual(response['Location'], r'http://testserver/accounts/login.html?next=/authenticate.html')

    def testNormalAuthentiction(self):
        """Test the regular case."""
        
        u = User.objects.create_user('alice', 'alice@example.com', password='secret')
        u.first_name = "Alice"
        u.last_name = "Smith"
        u.save()

        self.client.login(username='alice', password='secret')
        settings.ZENDESK_URL = "http://example.com"
        response = self.client.get(reverse(views.authorize), { 'timestamp': 100 }, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], r'http://example.com/access/remote/?name=Alice%20Smith&email=alice%40example.com&timestamp=100&hash=a52b47c95dd9c3298599629ced1cb462')

    def testAnonymous(self):
        """Test a login with no name."""
        
        u = User.objects.create_user('anon', 'anona@example.com', password='secret')
        u.save()

        self.client.login(username='anon', password='secret')
        settings.ZENDESK_URL = "http://example.com"
        response = self.client.get(reverse(views.authorize), { 'timestamp': 100 }, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], r'http://example.com/access/remote/?name=Anonymous%20User&email=anona%40example.com&timestamp=100&hash=528fa7fde15817dd150e1ffa70bd5984')
        
    def testUtfName(self):
        """Test a login with UTF characters in the name. This requires special URL encoding."""
        u = User.objects.create_user('nikos', 'kazantzakis@example.com', password='secret')
        u.first_name = "Δεν ελπίζω τίποτε."
        u.last_name = "Δεν φοβούμαι τίποτε. Είμαι λεύτερος."
        u.save()
        
        self.client.login(username='nikos', password='secret')
        settings.ZENDESK_URL = "http://example.com"
        response = self.client.get(reverse(views.authorize), { 'timestamp': 100 }, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], r'http://example.com/access/remote/?name=%CE%94%CE%B5%CE%BD%20%CE%B5%CE%BB%CF%80%CE%AF%CE%B6%CF%89%20%CF%84%CE%AF%CF%80%CE%BF%CF%84%CE%B5.%20%CE%94%CE%B5%CE%BD%20%CF%86%CE%BF%CE%B2%CE%BF%CF%8D%CE%BC%CE%B1%CE%B9%20%CF%84%CE%AF%CF%80%CE%BF%CF%84%CE%B5.%20%CE%95%CE%AF%CE%BC%CE%B1%CE%B9%20%CE%BB%CE%B5%CF%8D%CF%84%CE%B5%CF%81%CE%BF%CF%82.&email=kazantzakis%40example.com&timestamp=100&hash=c087311a8e0f86c59c7b8bb5eabeebf1')
