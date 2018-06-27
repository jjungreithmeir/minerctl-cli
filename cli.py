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

def _prepare_folder():
    if not os.path.isdir(CONFIG_FILE_LOCATION):
        os.makedirs(CONFIG_FILE_LOCATION)

def _load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        return config['Setup']['key_location']
    else:
        print('please use the -k/--key option to set the location of your\
              private key first.')

def _create_config(key):
    config = configparser.ConfigParser()
    config['Setup'] = {'key_location': key}
    with open(CONFIG_FILE, 'w') as file:
        config.write(file)
    return key

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--info', help='show basic version info about\
                        the CLI tool and the backend', default=False,
                        dest='info', action='store_true')
    parser.add_argument('-k', '--key', help='set private key location',
                        dest='key')
    parser.add_argument('-t', '--temp', help='show temperatures',
                        default=False, dest='temp', action='store_true')
    parser.add_argument('-f', '--filter', help='show filter status and data',
                        default=False, dest='filter', action='store_true')
    parser.add_argument('-v', '--ventilation', help='show ventilation status\
                        and data', default=False, dest='ventilation',
                        action='store_true')
    parser.add_argument('-o', '--operation', help='show active mining mode and\
                        respective configuration values', default=False,
                        dest='operation', action='store_true')
    parser.add_argument('-p', '--pid', help='show pid configuration',
                        default=False, dest='pid', action='store_true')
    parser.add_argument('-m', '--miner', help='show pid configuration',
                        dest='miner', action='store_true')

    _prepare_folder()
    args = parser.parse_args()
    if args.key:
        key_location = _create_config(args.key)
    else:
        key_location = _load_config()

    sec_handler = SecureHandler(key_location, 'http://127.0.0.1:12345')

    if args.info:
        pass
    if args.temp:
        print(sec_handler.get('/temp'))
    if args.filter:
        pass
    if args.ventilation:
        pass
    if args.operation:
        pass
    if args.pid:
        pass
    if args.miner:
        pass
    if len(sys.argv) == 1:
        parser.print_help()
