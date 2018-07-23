import sys
import time
import getpass
import jwt
import requests
from requests.exceptions import ConnectionError


class SecureHandler:
    """
    Small Wrapper for requests which automatically handles JWT token authorization.
    """
    def __init__(self, private_key_location, connection):
        """
        Initializing the wrapper and reading the private key file. If it is not
        found the program is stopped and exitcode 1 is thrown.

        :param private_key_location: key file location
        :param connection: http://<ip/domain>:port
        """
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
        """
        Checks wether a resp looks like it was created by flask-jwt-extended
        and therefore represents a failed authorization attempt.

        :param resp: json dict
        """
        if 'msg' in resp:
            print('JWT token authorization unsuccessfull. '
                  'Please check with your administrator whether your '
                  'public key was stored in the backend config.')
            print('Error: {}'.format(resp['msg']))
            sys.exit(1)

    @staticmethod
    def _connection_error():
        """
        Prints an error message and shuts down the program.
        """
        print('Connection to backend could not be established. '
              'Check your settings and try again.')
        sys.exit(1)

    def get(self, resource):
        """
        GETs the resource. If an error is thrown the program is shut down.

        :param resource: JSON resource to be consumed
        :returns: json dict
        """
        try:
            resp = self.session.get(self.connection + resource,
                                    headers=self.header).json()
            self._check_authorization_success(resp)
            return resp
        except ConnectionError:
            self._connection_error()

    def put(self, resource, data):
        """
        PUTs the resource. If an error is thrown the program is shut down.

        :param resource: JSON resource to be contacted
        :param data: dict
        """
        try:
            resp = self.session.put(self.connection + resource, data=data,
                                    headers=self.header).json()
            self._check_authorization_success(resp)
            return resp
        except ConnectionError:
            self._connection_error()

    def safe_put(self, resource, data):
        """
        GETs the data before PUTing and updates the values of the returned
        JSON dict. This is done in order to avoid resetting any values that have
        not been passed.

        :param resource: JSON resource to be contacted
        :param data: dict
        """
        try:
            curr_data = self.get(resource)
            for key, value in data.items():
                curr_data[key] = value

            self.put(resource, curr_data)
        except ConnectionError:
            self._connection_error()

    def patch(self, resource, data):
        """
        PATCHes the resource. If an error is thrown the program is shut down.

        :param resource: JSON resource to be contacted
        :param data: dict
        """
        try:
            resp = self.session.patch(self.connection + resource, data=data,
                                      headers=self.header).json()
            self._check_authorization_success(resp)
        except ConnectionError:
            self._connection_error()

    def safe_patch(self, resource, data):
        """
        GETs the data before patching and updates the values of the returned
        JSON dict. This is done in order to avoid resetting any values that have
        not been passed.

        :param resource: JSON resource to be contacted
        :param data: dict
        """
        try:
            curr_data = self.get(resource)
            for key, value in data.items():
                curr_data[key] = value

            self.patch(resource, curr_data)
        except ConnectionError:
            self._connection_error()
