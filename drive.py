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
        '''Establish Google credentials.  This will load stored credentials
        and validate them, and it will call self.login() if stored
        credentials are unavailable or fail to validate.'''

        self.load_credentials()

        if self.token is None:
            self.login()
        else:
            try:
                # Always refresh the token.  This is a dirty hack to avoid
                # doing anything more complicated.
                self.refresh()
                self.validate()
            except ValueError:
                self.login()

        # Add an Authorization header to all requests made through
        # our requests.Session object.
        self.session.headers.update({
            'Authorization': 'Bearer %(access_token)s' % self.token
            })

    def refresh(self):
        '''Use a refresh_token to refresh the access_token.  See
        https://developers.google.com/drive/about-auth'''

        if not 'refresh_token' in self.token:
            raise ValueError('no refresh token')

        r = self.session.post('%s/token' % OAUTH_URI, {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.token['refresh_token'],
            'grant_type': 'refresh_token'})

        if not r:
            raise ValueError('failed to refresh token')

        self.token['access_token'] = r.json()['access_token']
        self.store_credentials()

    def login(self):
        '''Perform OAuth authentication.'''

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

        self.token = r.json()
        self.store_credentials()

    def store_credentials(self):
        '''Write credentials to file.'''
        with open(self.credentials, 'w') as fd:
            fd.write(yaml.safe_dump(self.token, encoding='utf-8',
                default_flow_style=False))

    def load_credentials(self):
        '''Read credentials from file.'''
        try:
            with open(self.credentials) as fd:
                self.token = yaml.load(fd)
        except IOError:
            pass

    def validate(self):
        '''Validate token.'''

        r = requests.get('%s?access_token=%s' % (
            VALIDATE_URI, self.token['access_token']
            ))

        self._validate_response = r

        if not r:
            raise ValueError('failed to validate')

    def files(self):
        '''Return an iterator over the files in Google Drive.'''

        r = self.session.get('%s/files' % DRIVE_URI).json()

        for fspec in r['items']:
            yield fspec

    def get_file_metadata(self, fid):
        '''Return the file metadata for a file identified by its ID.'''

        return self.session.get('%s/files/%s' % (DRIVE_URI, fid)).json()

    def revisions(self, fid):
        '''Return an iterator over the revisions of a file
        identified by its ID.'''

        r = self.session.get('%s/files/%s/revisions' % (
            DRIVE_URI, fid)).json()

        for rev in r['items']:
            yield rev

if __name__ == '__main__':
    cfg = yaml.load(open('gd.conf'))
    gd = GoogleDrive(
            client_id=cfg['googledrive']['client id'],
            client_secret=cfg['googledrive']['client secret'],
            scopes=[DRIVE_RW_SCOPE],
            )

    gd.authenticate()

