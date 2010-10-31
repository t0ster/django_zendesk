from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote

from hashlib import md5

@never_cache
@login_required
def authorize(request):
    try:
        timestamp = request.GET['timestamp']
    except KeyError:
        raise Http404

    u = request.user

    first = u.first_name
    last = u.last_name
    if not first and not last:
        first = "Anonymous"
        last = "User"
  
    data = u'%s %+s%s%s%s' % (first, last, u.email, settings.ZENDESK_TOKEN, timestamp)
    hash = md5(data.encode('utf-8')).hexdigest()

    url = u"%s/access/remote/?name=%s %s&email=%s&timestamp=%s&hash=%s" % (settings.ZENDESK_URL, urlquote(first), urlquote(last), urlquote(u.email), timestamp, hash)

    return HttpResponseRedirect(iri_to_uri(url))
