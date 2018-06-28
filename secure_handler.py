import sys
import time
import getpass
import jwt
import requests
from requests.exceptions import ConnectionError


class SecureHandler:

    def __init__(self, private_key_location, connection):
        try:
            with open(private_key_location, 'rb') as file:
                private_key = file.read()
        except FileNotFoundError:
            print('The specified key file does not exist.')
            sys.exit(1)

        tmstmp = time.strftime("%Y%m%d-%H%M%S")
        access_token = jwt.encode({'jti': tmstmp, 'identity': getpass.getuser(),
                                   'type': 'access', 'fresh': False},
                                  private_key,
                                  algorithm='RS256').decode("utf-8")
        self.header = {'Authorization': 'Bearer {}'.format(access_token)}
        self.connection = connection
        self.session = requests.Session()
        self.adapter = requests.adapters.HTTPAdapter(max_retries=10)
        self.session.mount('http://', self.adapter)

    @staticmethod
    def _check_authorization_success(resp):
        if 'msg' in resp:
            print('JWT token authorization unsuccessfull. '
                  'Please check with your administrator whether your '
                  'public key was stored in the backend config.')
            print('Error: {}'.format(resp['msg']))
            sys.exit(1)

    @staticmethod
    def _connection_error():
        print('Connection to backend could not be established. '
              'Check your settings and try again.')
        sys.exit(1)

    def get(self, resource):
        try:
            resp = self.session.get(self.connection + resource,
                                    headers=self.header).json()
            self._check_authorization_success(resp)
            return resp
        except ConnectionError:
            self._connection_error()

    def put(self, resource, data):
        try:
            resp = self.session.put(self.connection + resource, data=data,
                                    headers=self.header)
            self._check_authorization_success(resp)
            return resp.raise_for_status()
        except ConnectionError:
            self._connection_error()

    def patch(self, resource, data):
        try:
            resp = self.session.patch(self.connection + resource, data=data,
                                      headers=self.header)
            self._check_authorization_success(resp)
            return resp.raise_for_status()
        except ConnectionError:
            self._connection_error()

    def safe_patch(self, resource, data):
        """
        GETs the data before patching and updates the values of the returned
        JSON dict. This is done in order to avoid resetting any values that have
        not been passed.
        """
        try:
            curr_data = self.get(resource)
            for key, value in data.items():
                curr_data[key] = value

            self.patch(resource, curr_data)
        except ConnectionError:
            self._connection_error()
