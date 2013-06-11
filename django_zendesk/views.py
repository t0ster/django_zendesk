import base64
from collections import OrderedDict
import hashlib
import hmac
import json
import uuid
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote

from hashlib import md5
import time

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

# ----- New JWT Based Authentication

signing_methods = {
    'HS256': lambda msg, key: hmac.new(key, msg, hashlib.sha256).digest(),
    'HS384': lambda msg, key: hmac.new(key, msg, hashlib.sha384).digest(),
    'HS512': lambda msg, key: hmac.new(key, msg, hashlib.sha512).digest(),
}

def base64url_encode(input):
    return base64.urlsafe_b64encode(input).replace('=', '')


def jwt_encode(payload, key, algorithm='HS256'):
    segments = []
    header = {"typ": "JWT", "alg": algorithm}
    segments.append(base64url_encode(json.dumps(header)))
    segments.append(base64url_encode(json.dumps(payload)))
    signing_input = '.'.join(segments)
    try:
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        signature = signing_methods[algorithm](signing_input, key)
    except KeyError:
        raise NotImplementedError("Algorithm not supported")
    segments.append(base64url_encode(signature))
    return '.'.join(segments)


@never_cache
@login_required
def authorize_jwt(request):

    user = request.user
    data = OrderedDict()
    data['iat'] = int(time.time())
    data['jti'] = str(uuid.uuid1())
    data['name'] = user.get_full_name()
    data['email'] = user.email
    data['external_id'] = int(user.id)
    data['organization'] = u""
    data['tags'] = u""
    data['remote_photo_url'] = u""

    tags = []
    if user.userprofile.company:
        data['organization'] = user.userprofile.company.name
        tags.append(user.userprofile.company.company_type.capitalize())
        if user.userprofile.company.sponsors.count():
            tags.append(u"sponsored")
            for company in user.userprofile.company.sponsors.all():
                tags.append(company.slug)
        if user.userprofile.is_company_admin:
            tags.append(u"company_admin")
        if user.userprofile.company.is_customer:
            tags.append(u"customer")
    if len(tags):
        data['tags'] = tags

    jwt_string = jwt_encode(data, settings.ZENDESK_SHARED_KEY)
    return_url = "https://" + settings.ZENDESK_SUBDOMAIN + ".zendesk.com/access/jwt?jwt=" + jwt_string
    if request.GET.get("return_to"):
        return_url += "&return_to={}".format(request.GET.get("return_to"))
    return HttpResponseRedirect(return_url)
