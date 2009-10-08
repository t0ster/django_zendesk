# These URLs are used in tests.py.

from django.conf.urls.defaults import *

urlpatterns = patterns('django_zendesk.views',
    (r'^authenticate\.html', 'authorize'),
)