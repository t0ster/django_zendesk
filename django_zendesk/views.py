from collections import OrderedDict
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
    """This will SSO authorize a user.  This passes back to  the newer remoteauth url"""

    try:
        timestamp = request.GET['timestamp']
    except KeyError:
        raise Http404

    user = request.user

    data = OrderedDict()
    data['name'] = user.get_full_name()
    data['email'] = user.email
    data['external_id'] = str(user.id)
    data['organization'] = u""
    data['tags'] = u""
    data['remote_photo_url'] = u""
    data['token'] = settings.ZENDESK_TOKEN
    data['timestamp'] = timestamp

    tags = []
    if user.userprofile.company:
        data['organization'] = user.userprofile.company.name
        tags.append(user.userprofile.company.company_type.capitalize())
        if user.userprofile.company.sponsors.count():
            tags.append("sponsored")
            for company in user.userprofile.company.sponsors.all():
                tags.append(company.slug)
        if user.userprofile.is_company_admin:
            tags.append("company_admin")
        if user.userprofile.company.is_customer:
            tags.append("customer")
    if len(tags):
        data['tags'] = ",".join(tags)

    hash_str = "|".join(data.values()).encode('utf-8')
    hash = md5(hash_str).hexdigest()

    # Build our URL..
    url = u"{}/access/remoteauth/?name={}".format(settings.ZENDESK_URL, urlquote(data['name']))
    url += u"&email={}&timestamp={}".format(urlquote(data['email']), timestamp)
    url += u"&hash={}&external_id={}".format(hash, data['external_id'])

    if user.userprofile.company:
        url += u"&organization={}".format(urlquote(data['organization']))
    if data['tags'] != u"":
        url += u"&tags={}".format(urlquote(data['tags']))
    if data['remote_photo_url'] != u"":
        url += u"&remote_photo_url={}".format(urlquote(data['remote_photo_url']))

    return HttpResponseRedirect(iri_to_uri(url))
