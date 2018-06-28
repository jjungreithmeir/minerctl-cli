import sys
import jwt
import requests
import time
import getpass


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

    def get(self, resource):
        return self.session.get(self.connection + resource,
                                headers=self.header).json()

    def put(self, resource, data):
        resp = self.session.put(self.connection + resource, data=data,
                                headers=self.header)
        return resp.raise_for_status()

    def patch(self, resource, data):
        resp = self.session.patch(self.connection + resource, data=data,
                                headers=self.header)
        return resp.raise_for_status()
