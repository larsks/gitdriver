#!/usr/bin/python

import os
import sys
import argparse
import urllib
import yaml
import json
import requests

OAUTH_URI='https://accounts.google.com/o/oauth2'
VALIDATE_URI='https://www.googleapis.com/oauth2/v1/tokeninfo'
DRIVE_URI='https://www.googleapis.com/drive/v2'

OAUTH_SCOPES = [
      'https://www.googleapis.com/auth/userinfo.email',
      'https://www.googleapis.com/auth/userinfo.profile',
]

DRIVE_RW_SCOPE = 'https://www.googleapis.com/auth/drive'
DRIVE_RO_SCOPE = 'https://www.googleapis.com/auth/drive.readonly'

REDIRECT_URI='urn:ietf:wg:oauth:2.0:oob'

class GoogleDrive(object):
    def __init__(self,
            client_id,
            client_secret,
            credentials=None,
            scopes=None):

        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = OAUTH_SCOPES
        self.session = requests.Session()
        self.token = None

        if scopes is not None:
            self.scopes.extend(scopes)

        if credentials is None:
            credentials = os.path.join(os.environ['HOME'], '.googledrive')

        self.credentials = credentials

    def authenticate(self):
        self.load_credentials()

        if self.token is None:
            self.login()
        else:
            try:
                self.refresh()
                self.validate()
            except ValueError:
                self.login()

        self.session.headers.update({
            'Authorization': 'Bearer %(access_token)s' % self.token
            })

    def refresh(self):
        if not 'refresh_token' in self.token:
            raise ValueError('no refresh token')

        r = self.session.post('%s/token' % OAUTH_URI, {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.token['refresh_token'],
            'grant_type': 'refresh_token'})

        if not r:
            raise ValueError('failed to refresh token')

        self.token['access_token'] = r.json['access_token']
        self.store_credentials()

    def login(self):
        params = {
            'client_id': self.client_id,
            'scope': ' '.join(OAUTH_SCOPES),
            'redirect_uri': REDIRECT_URI,
            'access_type': 'offline',
            'response_type': 'code',
            }

        url = '%s?%s' % ('%s/auth' % OAUTH_URI, urllib.urlencode(params))

        print 'Point your browser at the following URL and then '
        print 'enter the authorization code at the prompt:'
        print
        print url
        print
        code = raw_input('Enter code: ')
        self.code = code
        r = requests.post('%s/token' % OAUTH_URI, {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code',
            })
        
        if not r:
            raise ValueError('failed to authenticate')

        self.token = r.json
        self.store_credentials()

    def store_credentials(self):
        with open(self.credentials, 'w') as fd:
            fd.write(yaml.safe_dump(self.token, encoding='utf-8',
                default_flow_style=False))

    def load_credentials(self):
        try:
            with open(self.credentials) as fd:
                self.token = yaml.load(fd)
        except IOError:
            pass

    def validate(self):
        r = requests.get('%s?access_token=%s' % (
            VALIDATE_URI, self.token['access_token']
            ))

        if not r:
            raise ValueError('failed to validate')

    def files(self):
        r = self.session.get('%s/files' % DRIVE_URI).json

        for fspec in r['items']:
            yield fspec

    def get_file_metadata(self, fid):
        return self.session.get('%s/files/%s' % (DRIVE_URI, fid)).json

    def revisions(self, fid):
        r = self.session.get('%s/files/%s/revisions' % (
            DRIVE_URI, fid)).json

        for rev in r['items']:
            yield rev

