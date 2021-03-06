# -*- coding: utf-8 -*-
#
"""
Python library for the Withings API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Withings Body metrics Services API
<http://www.withings.com/en/api/wbsapiv2>

Uses Oauth 1.0 to authentify. You need to obtain a consumer key
and consumer secret from Withings by creating an application
here: <https://oauth.withings.com/partner/add>

Usage:

auth = WithingsAuth(CONSUMER_KEY, CONSUMER_SECRET)
authorize_url = auth.get_authorize_url()
print "Go to %s allow the app and copy your oauth_verifier" % authorize_url
oauth_verifier = raw_input('Please enter your oauth_verifier: ')
creds = auth.get_credentials(oauth_verifier)

client = WithingsApi(creds)
measures = client.get_measures(limit=1)
print "Your last measured weight: %skg" % measures[0].weight

"""

__title__ = 'withings'
__version__ = '0.1'
__author__ = 'Maxime Bouroumeau-Fuseau'
__license__ = 'MIT'
__copyright__ = 'Copyright 2012 Maxime Bouroumeau-Fuseau'

__all__ = ['WithingsCredentials', 'WithingsAuth', 'WithingsApi',
           'WithingsMeasures', 'WithingsMeasureGroup']

import requests
from requests_oauthlib import OAuth1, OAuth1Session
import json
import datetime


class WithingsCredentials(object):
    def __init__(self, access_token=None, access_token_secret=None,
                 consumer_key=None, consumer_secret=None, user_id=None):
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.user_id = user_id


class WithingsAuth(object):
    URL = 'https://developer.health.nokia.com/account'

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth_token = None
        self.oauth_secret = None

    def get_authorize_url(self):
        oauth = OAuth1Session(self.consumer_key,
                              client_secret=self.consumer_secret)

        tokens = oauth.fetch_request_token('%s/request_token' % self.URL)
        self.oauth_token = tokens['oauth_token']
        self.oauth_secret = tokens['oauth_token_secret']

        return oauth.authorization_url('%s/authorize' % self.URL)

    def get_credentials(self, oauth_verifier):
        oauth = OAuth1Session(self.consumer_key,
                              client_secret=self.consumer_secret,
                              resource_owner_key=self.oauth_token,
                              resource_owner_secret=self.oauth_secret,
                              verifier=oauth_verifier)
        tokens = oauth.fetch_access_token('%s/access_token' % self.URL)
        return WithingsCredentials(access_token=tokens['oauth_token'],
                                   access_token_secret=tokens['oauth_token_secret'],
                                   consumer_key=self.consumer_key,
                                   consumer_secret=self.consumer_secret,
                                   user_id=tokens['userid'])


class WithingsApi(object):
    URL = 'http://api.health.nokia.com'
    v2_URL = 'http://api.health.nokia.com/v2'

    def __init__(self, credentials):
        self.credentials = credentials
        self.oauth = OAuth1(credentials.consumer_key,
                            credentials.consumer_secret,
                            credentials.access_token,
                            credentials.access_token_secret,
                            signature_type='query')
        self.client = requests.Session()
        self.client.auth = self.oauth
        self.client.params.update({'userid': credentials.user_id})

    def request(self, service, action, params=None, method='GET'):
        if params is None:
            params = {}
        params['action'] = action
        if action == 'getactivity' or service == 'sleep': #activity requests are sent to a different URL
            r = self.client.request(method, '%s/%s' % (self.v2_URL, service), params=params)
        else:
            r = self.client.request(method, '%s/%s' % (self.URL, service), params=params)
        try:
            response = json.loads(r.text)
            status = response['status']
            if status != 0:
                raise WithingsAPIError("%d" % status)
            return response.get('body', None)
        except json.decoder.JSONDecodeError as e:
            return { "error" : e.message }

    def get_user(self):
        return self.request('user', 'getbyuserid')

    def get_measures(self, **kwargs):
        r = self.request('measure', 'getmeas', kwargs)
        return WithingsMeasures(r)

    def get_activity(self, **kwargs):
        r = self.request('measure', 'getactivity', kwargs)
        return r

    def get_sleep(self, **kwargs):
        r = self.request('sleep', 'get', kwargs)
        return r

    def get_sleepsummary(self, **kwargs):
        r = self.request('sleep', 'getsummary', kwargs)
        return r

    def subscribe(self, callback_url, comment, appli=1):
        params = {'callbackurl': callback_url,
                  'comment': comment,
                  'appli': appli}
        self.request('notify', 'subscribe', params)

    def unsubscribe(self, callback_url, appli=1):
        params = {'callbackurl': callback_url, 'appli': appli}
        self.request('notify', 'revoke', params)

    def is_subscribed(self, callback_url, appli=1):
        params = {'callbackurl': callback_url, 'appli': appli}
        try:
            self.request('notify', 'get', params)
            return True
        except:
            return False

    def list_subscriptions(self, appli=1):
        r = self.request('notify', 'list', {'appli': appli})
        return r['profiles']


class WithingsMeasures(list):
    def __init__(self, data):
        super(WithingsMeasures, self).__init__([WithingsMeasureGroup(g) for g in data['measuregrps']])
        self.updatetime = datetime.datetime.fromtimestamp(data['updatetime'])


class WithingsMeasureGroup(object):
    MEASURE_TYPES = (('weight', 1), ('height', 4), ('fat_free_mass', 5),
                     ('fat_ratio', 6), ('fat_mass_weight', 8),
                     ('diastolic_blood_pressure', 9), ('systolic_blood_pressure', 10),
                     ('heart_pulse', 11), ('temperature', 12), ('sp02', 54),
                     ('body_temperature', 71), ('skin_temperature', 73), ('muscle_mass', 76),
                     ('hydration', 77), ('bone_mass', 88), ('pulse_wave_velocity', 91))

    def __init__(self, data):
        self.data = data
        self.grpid = data['grpid']
        self.attrib = data['attrib']
        self.category = data['category']
        self.date = datetime.datetime.fromtimestamp(data['date'])
        self.measures = data['measures']
        for n, t in self.MEASURE_TYPES:
            self.__setattr__(n, self.get_measure(t))

    def is_ambiguous(self):
        return self.attrib == 1 or self.attrib == 4

    def is_measure(self):
        return self.category == 1

    def is_target(self):
        return self.category == 2

    def get_measure(self, measure_type):
        for m in self.measures:
            if m['type'] == measure_type:
                return m['value'] * pow(10, m['unit'])
        return None

class WithingsException(Exception):
    pass

class WithingsAPIError(WithingsException):
    DESCRIPTIONS = {
        100: 'The hash is missing, invalid, or does not match the provided email',
        247: 'The userid is absent, or incorrect',
        250: 'The userid and publickey do not match, or the user does not share its data',
        264: 'The email address provided is either unknown or invalid',
        286: 'No such subscription was found',
        293: 'The callback URL is either absent or incorrect',
        294: 'No such subscription could be deleted',
        304: 'The comment is either absent or incorrect',
        2555: 'An unknown error occured',
    }

    def __init__(self, status=2555):
        self.status = status
        self.message = self.DESCRIPTIONS.get(status, 'unknown status')

