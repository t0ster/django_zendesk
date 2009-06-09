django_zendesk provides single-sign on functionality between a django.contrib.auth based site and Zendesk. Other authentication systems are compatible as long as they implement the @login_required decorator. 

SETUP:

django_zendesk needs to settings.py variables to be implemented:

ZENDESK_URL     = The URL of your support page, will either be on zendesk.com or your own domain (via a CNAME record)
ZENDESK_TOKEN   = The API token you receive from Zendesk

The only other code setup required is pointing a URL at the django_zendesk.views.authorize method, it will look something like:

(r'zendesk/$', 'django_zendesk.views.authorize')

Zendesk itself needs a bit of setup, including the URL we just set up above and a log-out URL which already should be implemented somewhere in your site.

CREDIT:

Initial idea by Jon Gales <me@jongales.com) with improvements by Alexander Ljungberg.

See initial idea/blog post here: http://www.jongales.com/blog/2009/05/12/zendesk-remote-authentication-with-django/