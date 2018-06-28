import os
import sys
import argparse
import configparser
from pathlib import Path
from secure_handler import SecureHandler

HOME = str(Path.home())
CONFIG_FILE_LOCATION = HOME + '/' + '.minerctl'
CONFIG_FILE_NAME = 'config.ini'
CONFIG_FILE = CONFIG_FILE_LOCATION + '/' + CONFIG_FILE_NAME
PARSER = argparse.ArgumentParser()

def _prepare_folder():
    if not os.path.isdir(CONFIG_FILE_LOCATION):
        os.makedirs(CONFIG_FILE_LOCATION)

def _load_config(section, attr):
    config = configparser.ConfigParser()
    try:
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
            return config[section][attr]
    except KeyError:
        print('Could not find {} attribute in config. Did you set this value accordingly? View the help (-h) for more information'.format(attr))
        sys.exit(1)

def _parse_url(url):
    if not url.startswith('http://'):
        url = 'http://' + url
    return url

def _create_config(section, attr, val):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    for sec in config.sections():
        for (existing_key, existing_val) in config.items(sec):
            config[sec][existing_key] = existing_val
    if config.has_option(section, attr):
        config[section][attr] = val
    else:
        config[section] = {attr: val}
    with open(CONFIG_FILE, 'w') as file:
        config.write(file)

def _check_config_file_integrity(section_attr):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    response = True
    for section, attr in section_attr.items():
        if not config.has_option(section, attr):
            print('Could not find {} attribute in config.'.format(attr))
            response = False
    return response

def _only_certain_attributes_given(args, attributes):
    arguments = vars(args)
    for attr in attributes:
        arguments.pop(attr, None)
    for arg, val in arguments.items():
        if val:
            return False
    return True

def _error_exit():
    PARSER.print_help()
    sys.exit(1)

def main():
    PARSER.add_argument('-i', '--info', help='show basic version info about\
                        the CLI tool and the backend', default=False,
                        dest='info', action='store_true')
    PARSER.add_argument('-k', '--key', help='set private key location',
                        dest='key')
    PARSER.add_argument('-b', '--backend', help='set backend address and port \
                        (eg: 127.0.0.1:12345)', dest='backend')
    PARSER.add_argument('-a', '--all', help='show all available data',
                        default=False, dest='all', action='store_true')
    PARSER.add_argument('-t', '--temp', help='show temperatures',
                        default=False, dest='temp', action='store_true')
    PARSER.add_argument('-f', '--filter', help='show filter status and data',
                        default=False, dest='filter', action='store_true')
    PARSER.add_argument('-v', '--ventilation', help='show ventilation status\
                        and data', default=False, dest='ventilation',
                        action='store_true')
    PARSER.add_argument('-o', '--operation', help='show active mining mode and\
                        respective configuration values', default=False,
                        dest='operation', action='store_true')
    PARSER.add_argument('-p', '--pid', help='show pid configuration',
                        default=False, dest='pid', action='store_true')
    PARSER.add_argument('-m', '--miner', help='show pid configuration',
                        dest='miner', action='store_true')

    _prepare_folder()
    args = PARSER.parse_args()
    if len(sys.argv) == 1:
        _error_exit()

    if args.key:
        _create_config('PKI', 'key_location', args.key)
    if args.backend:
        _create_config('Connection', 'backend_addr', args.backend)

    # exit program if only the config values have been updated
    if _only_certain_attributes_given(args, ['key', 'backend']):
        sys.exit(0)

    if not _check_config_file_integrity({'Connection': 'backend_addr',
                                         'PKI': 'key_location'}):
        _error_exit()

    backend_addr = _parse_url(_load_config('Connection', 'backend_addr'))
    key_location = _load_config('PKI', 'key_location')

    sec_handler = SecureHandler(key_location, backend_addr)

    if args.info or args.all:
        print(sec_handler.get('/info'))
    if args.temp or args.all:
        print(sec_handler.get('/temp'))
    if args.filter or args.all:
        print(sec_handler.get('/filter'))
    if args.ventilation or args.all:
        print(sec_handler.get('/fans'))
    if args.operation or args.all:
        print(sec_handler.get('/mode'))
    if args.pid or args.all:
        print(sec_handler.get('/pid'))
    if args.miner or args.all:
        # TODO
        pass
