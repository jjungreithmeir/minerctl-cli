import os
import sys
import argparse
import configparser
import pkg_resources
from collections import Counter
from pathlib import Path
from secure_handler import SecureHandler

HOME = str(Path.home())
CONFIG_FILE_LOCATION = HOME + '/' + '.minerctl'
CONFIG_FILE_NAME = 'config.ini'
CONFIG_FILE = CONFIG_FILE_LOCATION + '/' + CONFIG_FILE_NAME
PARSER = argparse.ArgumentParser()
SUBPARSERS = PARSER.add_subparsers(dest='set_mode', metavar='modes')
SET_PARSER = SUBPARSERS.add_parser('set', help='SET mode for remote configuration')

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

def _error_exit(parser):
    parser.print_help()
    sys.exit(1)

def _setup_arguments():
    PARSER.add_argument('-i', '--info', help='show basic version info about\
                        the CLI tool and the backend', default=False,
                        dest='info', action='store_true')
    PARSER.add_argument('-k', '--key', help='set private key location',
                        dest='key', metavar='<path>')
    PARSER.add_argument('-b', '--backend', help='set backend address and port \
                        (eg: 127.0.0.1:12345)', dest='backend', metavar='<ip:port>')
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
    PARSER.add_argument('-m', '--miners', help='show miner overview',
                        dest='miners', action='store_true')
    PARSER.add_argument('-s', '--summary', help='show miner summary',
                        dest='summary', action='store_true')
    PARSER.add_argument('-q', '--query', help='query state of specific miner',
                        dest='query', metavar='<ID>')

    SET_PARSER.add_argument('--target', help='set target temperature',
                            dest='set_target', metavar='<temperature>')
    SET_PARSER.add_argument('--sensor_id', help='set main sensor id',
                            dest='set_sensor_id', metavar='<ID>')
    SET_PARSER.add_argument('--external', help='set external reference temperature',
                            dest='set_external', metavar='<temperature>')
    SET_PARSER.add_argument('--threshold', help='set differential pressure threshold',
                            dest='set_threshold', metavar='<pressure>')
    SET_PARSER.add_argument('--min-rpm', help='set minimum fan RPM',
                            dest='set_min_rpm', metavar='<rpm>')
    SET_PARSER.add_argument('--max-rpm', help='set maximum fan RPM',
                            dest='set_max_rpm', metavar='<rpm>')
    SET_PARSER.add_argument('--miner', help='set miner state to on, off, enable (=on), disable',
                            dest='set_miner', nargs=2, metavar=('<ID>', '<state>'))
    SET_PARSER.add_argument('--proportional', help='set PID proportional value',
                            dest='set_proportional', metavar='<number>')
    SET_PARSER.add_argument('--integral', help='set PID integral value',
                            dest='set_integral', metavar='<number>')
    SET_PARSER.add_argument('--derivative', help='set PID derivative value',
                            dest='set_derivative', metavar='<number>')
    SET_PARSER.add_argument('--bias', help='set PID bias value',
                            dest='set_bias', metavar='<number>')

def main():
    _setup_arguments()
    _prepare_folder()

    args = PARSER.parse_args()
    if len(sys.argv) == 1:
        _error_exit(PARSER)

    if args.key:
        _create_config('PKI', 'key_location', args.key)
    if args.backend:
        _create_config('Connection', 'backend_addr', args.backend)

    # exit program if only the config values have been updated
    if _only_certain_attributes_given(args, ['key', 'backend']):
        sys.exit(0)

    if not _check_config_file_integrity({'Connection': 'backend_addr',
                                         'PKI': 'key_location'}):
        _error_exit(PARSER)

    backend_addr = _parse_url(_load_config('Connection', 'backend_addr'))
    key_location = _load_config('PKI', 'key_location')

    sec_handler = SecureHandler(key_location, backend_addr)

    if args.info or args.all:
        info = sec_handler.get('/info')
        version = pkg_resources.require('minerctl_cli')[0].version
        print('Firmware version of microcontroller: {}, Version of minerctl_cli: {}'
              .format(info['firmware_version'], version))
    if args.temp or args.all:
        temp = sec_handler.get('/temp')
        temps = ', '.join([f'Sensor #{key}: {value}°C' \
                           for key, value in temp['measurements'].items()])
        print('Measurements: {}'.format(temps))
        print('Target temperature: {}°C'.format(temp['target']))
        print('Main sensor id: #{}'.format(temp['sensor_id']))
        print('External reference temperature: {}°C'.format(temp['external']))
    if args.filter or args.all:
        filter = sec_handler.get('/filter')
        print('Differential pressure: {}mBar'.format(filter['pressure_diff']))
        print('Differential pressure threshold: {}mBar'
              .format(filter['threshold']))
        print('Filter needs cleaning: {}'.format(str(filter['status_ok'])))
    if args.ventilation or args.all:
        vent = sec_handler.get('/fans')
        print('Minimum RPM: {}%, Maximum RPM: {}%, Current RPM: {}%'
              .format(vent['min_rpm'], vent['max_rpm'], vent['rpm']))
    if args.operation or args.all:
        op = sec_handler.get('/mode')
        mode = op.pop('active_mode', None)
        mode_settings = ', '.join([f'{key}: {value}ms' \
                           for key, value in op.items()])
        print('Active mode: {}, {}'.format(mode, mode_settings))
    if args.pid or args.all:
        pid = sec_handler.get('/pid')
        pid_settings = ', '.join([f'{key}: {value}' \
                           for key, value in pid.items()])
        print('PID: {}'.format(pid_settings))
    if args.miners or args.all:
        cfg = sec_handler.get('/cfg')
        cntr = Counter(miners)
        summary = {'on': cntr[True], 'off': cntr[False], 'disabled': cntr[None]}
        summary_text = ', '.join([f'{key}: {value}'\
                                    for key, value in summary.items()])
        print('Miner states: {}'.format(summary_text))
    if args.query:
        state = sec_handler.get('/miner?id={}'.format(args.query))['running']
        if state == None:
            msg = 'disabled'
        elif state:
            msg = 'on'
        elif not state:
            msg = 'off'
        print('Miner #{} state: {}'.format(args.query, msg))
    if args.summary:
        states = sec_handler.get('/cfg')['miners']
        ids_on = [i for i, x in enumerate(states) if x == True]
        ids_off = [i for i, x in enumerate(states) if x == False]
        ids_disabled = [i for i, x in enumerate(states) if x == None]
        print('Miners turned on: {}'.format(', '.join('#{}'.format(i) for i in ids_on)))
        print('Miners turned off: {}'.format(', '.join('#{}'.format(i) for i in ids_off)))
        print('Disabled miners: {}'.format(', '.join('#{}'.format(i) for i in ids_disabled)))

    if args.set_mode:
        # exit if only `minerctl set` has been entered
        if len(sys.argv) == 2:
            _error_exit(SET_PARSER)

        if args.set_target:
            sec_handler.safe_patch('/temp', {'target': args.set_target})
        if args.set_sensor_id:
            sec_handler.safe_patch('/temp', {'sensor_id': args.set_sensor_id})
        if args.set_external:
            sec_handler.safe_patch('/temp', {'external': args.set_external})
        if args.set_threshold:
            sec_handler.safe_patch('/filter', {'threshold': args.set_threshold})
        if args.set_min_rpm:
            sec_handler.safe_patch('/fans', {'min_rpm': args.set_min_rpm})
        if args.set_max_rpm:
            sec_handler.safe_patch('/fans', {'max_rpm': args.set_max_rpm})
        if args.set_miner:
            try:
                id = int(args.set_miner[0])
            except ValueError:
                print('The miner ID has to be an integer!')
                _error_exit(SET_PARSER)
            if args.set_miner[1] not in('on', 'off', 'enable', 'disable'):
                print('Invalid miner action!')
                _error_exit(SET_PARSER)

            sec_handler.safe_patch('/miner?id={}&action={}'.format(id, args.set_miner[1]), {})
        if args.set_proportional:
            sec_handler.safe_patch('/pid', {'proportional': args.set_proportional})
        if args.set_derivative:
            sec_handler.safe_patch('/pid', {'derivative': args.set_derivative})
        if args.set_integral:
            sec_handler.safe_patch('/pid', {'integral': args.set_integral})
