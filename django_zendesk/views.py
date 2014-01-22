# -*- coding: utf-8 -*-
"""views.py: django zendesk"""

from __future__ import unicode_literals

import base64
from collections import OrderedDict
import hashlib
import hmac
import json
import uuid
from hashlib import md5
import time

from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote

from apps.company.models import COMPANY_TYPES


def get_tags(user):
    """Get a list of tags for a user"""
    tags = []
    if user.is_company_admin:
        tags.append("company_admin")
    if user.company:
        tags.append(user.company.slug)
        tags.append(user.company.company_type)
        tags.append("view_{}".format(user.company.company_type))
        if user.company.company_type == "provider":
            tags.append("view_{}".format("rater"))
        if user.company.is_eep_sponsor:
            tags.append("is_sponsor")
            tags.append("sponsor_{}".format(user.company.slug))
            for company_type in dict(COMPANY_TYPES).keys():
                if 'company.view_{}organization'.format(company_type) in user.get_all_permissions():
                    tags.append('sponsor_{}_{}'.format(user.company.slug,  company_type))
        if user.company.sponsors.count():
            tags.append("sponsored")
            for company in user.company.sponsors.all():
                tags.append("sponsor_{}".format(company.slug))
                tags.append('sponsor_{}_{}'.format(company.slug, user.company.company_type))
                if user.company.company_type == "provider":
                    tags.append('sponsor_{}_{}'.format(company.slug, "rater"))
        if user.company.is_customer:
            tags.append("customer")
    return tags



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
    data['organization'] = ""
    data['tags'] = ""
    data['remote_photo_url'] = ""
    data['token'] = settings.ZENDESK_TOKEN
    data['timestamp'] = timestamp

    tags = get_tags(user)
    if user.company:
        data['organization'] = user.company.name

    if len(tags):
        data['tags'] = ",".join(tags)

    hash_str = "|".join(data.values()).encode('utf-8')
    hash = md5(hash_str).hexdigest()

    # Build our URL..
    url = "{}/access/remoteauth/?name={}".format(settings.ZENDESK_URL, urlquote(data['name']))
    url += "&email={}&timestamp={}".format(urlquote(data['email']), timestamp)
    url += "&hash={}&external_id={}".format(hash, data['external_id'])

    if user.company:
        url += "&organization={}".format(urlquote(data['organization']))
    if data['tags'] != "":
        url += "&tags={}".format(urlquote(data['tags']))
    if data['remote_photo_url'] != "":
        url += "&remote_photo_url={}".format(urlquote(data['remote_photo_url']))

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
    data['organization'] = ""
    data['tags'] = ""
    data['remote_photo_url'] = ""

    if user.company:
        data['organization'] = user.company.name

    tags = get_tags(user)
    if len(tags):
        data['tags'] = tags

    jwt_string = jwt_encode(data, settings.ZENDESK_SHARED_KEY)
    return_url = "https://" + settings.ZENDESK_SUBDOMAIN + ".zendesk.com/access/jwt?jwt=" + jwt_string
    if request.GET.get("return_to"):
        return_url += "&return_to={}".format(request.GET.get("return_to"))
    return HttpResponseRedirect(return_url)
