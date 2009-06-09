from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.conf import settings

from hashlib import md5

@never_cache
@login_required
def authorize(request):
    
    try:
        timestamp = request.GET['timestamp']
    except KeyError:
        raise Http404
    
    u = request.user
    
    if not u.first_name and not u.last_name:
        u.first_name = 'Anonymous'
        u.last_name = 'User'
    
    data = u'%s %+s%s%s%s' % (u.first_name, u.last_name, u.email, settings.ZENDESK_TOKEN, timestamp)
    
    hash = md5(data.encode('utf-8')).hexdigest()
    
    url = "%s/access/remote/?name=%s %s&email=%s&timestamp=%s&hash=%s" % (settings.ZENDESK_URL, u.first_name, u.last_name, u.email, timestamp, hash)
    
    return HttpResponseRedirect(url)