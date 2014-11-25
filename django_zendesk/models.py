# -*- coding: utf-8 -*-
"""models.py: Zendesk models"""

from __future__ import unicode_literals
from __future__ import print_function

import json
import logging
import pprint

from django.conf import settings
import requests

__author__ = 'Steven Klass'
__date__ = '2011/06/22 09:56:26'
__copyright__ = 'Copyright 2011-2014 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass']


log = logging.getLogger(__name__)


class Zendesk(object):

    def __init__(self, *args, **kwargs):
        self.subdomain = kwargs.get('subdomain', settings.ZENDESK_SUBDOMAIN)
        self.api_token = kwargs.get('subdomain', settings.ZENDESK_API_TOKEN)
        self.agent_user = kwargs.get('agent_user', settings.ZENDESK_AGENT_EMAIL)
        self.agent_password = kwargs.get('agent_user', settings.ZENDESK_AGENT_PASSWORD)
        self.base_url = "https://{subdomain}.zendesk.com/api/v2/".format(subdomain=self.subdomain)

    def create_ticket(self, subject, user, comment=None):

        if not(hasattr(user, "email") and user.email):
            raise TypeError("Expect user to be a User object")

        data = {'request': {'subject': subject}}
        if comment:
            data['request']['comment'] = {'value': comment}

        url = self.base_url + "requests.json"
        auth = "{email_address}/token".format(email_address=user.email)

        response = requests.post(
            url, data=json.dumps(data),  auth=(auth, self.api_token),
            headers={'content-type': 'application/json'})

        if response.status_code == 201:
            data = json.loads(response.text)['request']
            log.debug("Created {status} ticket {id} - {subject}".format(**data))
            return data
        else:
            message = "Zendesk invalid response on create ticket %s - %s"
            log.error(message, response.status_code, data)
            raise IOError(message, response.status_code, data)

    def add_admin_comment(self, ticket_id, comment, public=True):

        data = {'ticket': {'comment': {'body': comment, 'public': public}}}

        url = self.base_url + "tickets/{id}.json".format(id=ticket_id)

        response = requests.put(
            url, data=json.dumps(data),  auth=(self.agent_user, self.agent_password),
            headers={'content-type': 'application/json'})

        if response.status_code == 200:
            data = json.loads(response.text)
            log.debug("Added comment to ticket {id} ".format(id=ticket_id))
            return data
        else:
            message = "Zendesk invalid response on admin comment [%s] for ticket %s - %s"
            log.error(message, response.status_code, ticket_id, data)
            raise IOError(message, response.status_code, ticket_id, data)

