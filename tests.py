import pytest
import subprocess
import random


def _test(*args):
    return subprocess.run(['minerctl', *args],
                          universal_newlines=True,
                          stdout=subprocess.PIPE)

def _in(actual, *values):
    return all(s in actual for s in (*values,))

def test_helper_in():
    assert _in('hello world', 'hello', 'world')
    assert not _in('hello world', 'hello', 'spam and eggs')
    assert not _in('eggs and bacon', 'hello', 'world')

def test_no_arg_help():
    result = _test()
    assert result.returncode == 1
    assert _in(result.stdout, 'help', 'usage: minerctl')

@pytest.fixture(scope="module")
def setup():
    _test('-b', '127.0.0.1:12345', '-k', 'testing/jwtRS256.key')

def test_temp():
    for param in ('-t', '--temp'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Measurements', 'External reference', 'Sensor',
                   'Target temperature')
        assert not _in(result.stdout, 'None')

def test_info():
    for param in ('-i', '--info'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Firmware version', 'minerctl_cli')
        assert not _in(result.stdout, 'None')

def test_filter():
    for param in ('-f', '--filter'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Differential pressure', 'threshold',
                   'needs cleaning')
        assert not _in(result.stdout, 'None')

def test_ventilation():
    for param in ('-v', '--ventilation'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Minimum RPM', 'Maximum RPM', 'Current RPM')
        assert not _in(result.stdout, 'None')

def test_operation():
    for param in ('-o', '--operation'):
        result = _test('-o')
        assert result.returncode == 0
        assert _in(result.stdout, 'Active mode')
        if 'gpu' in result.stdout:
            assert _in(result.stdout, 'ontime', 'offtime')
        elif 'asic' in result.stdout:
            assert _in(result.stdout, 'restime')
        else:
            pytest.fail('mode not recognized')
        assert not _in(result.stdout, 'None')

def test_pid():
    for param in ('-p', '--pid'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'proportional', 'integral', 'derivative',
                   'bias')
        assert not _in(result.stdout, 'None')

def test_miners():
    for param in ('-m', '--miners'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Miner states', 'on', 'off', 'disabled')
        assert not _in(result.stdout, 'None')

def test_summary():
    for param in ('-s', '--summary'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Miners turned on', 'Miners turned off',
                   'Disabled miners')
        assert not _in(result.stdout, 'None')

def test_query():
    for param in ('-q', '--query'):
        rand_id = str(random.randint(0, 100))
        result = _test(param, rand_id)
        assert result.returncode == 0
        assert _in(result.stdout, 'Miner #{} state:'.format(rand_id))
        assert not _in(result.stdout, 'None')

def test_set_no_arg_help():
    result = _test('set')
    assert result.returncode == 1
    assert _in(result.stdout, 'help', 'usage: minerctl')

def test_set_target():
    rand = str(random.randint(0, 50))
    _test('set', '--target', rand)
    for param in ('-t', '--temp'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Measurements', 'External reference', 'Sensor',
                   'Target temperature: {}'.format(rand))
        assert not _in(result.stdout, 'None')

def test_set_sensor_id():
    rand = str(random.randint(0, 3))
    _test('set', '--sensor_id', rand)
    for param in ('-t', '--temp'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Measurements', 'External reference',
                   'Main sensor id: #{}'.format(rand), 'Target temperature')
        assert not _in(result.stdout, 'None')

def test_set_external():
    rand = str(random.randint(0, 50))
    _test('set', '--external', rand)
    for param in ('-t', '--temp'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Measurements', 'Main sensor',
                   'Target temperature',
                   'External reference temperature: {}'.format(rand))
        assert not _in(result.stdout, 'None')

def test_set_threshold():
    rand = str(random.randint(500, 1000))
    _test('set', '--threshold', rand)
    for param in ('-f', '--filter'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Differential pressure', 'needs cleaning',
                   'Differential pressure threshold: {}mBar'.format(rand))
        assert not _in(result.stdout, 'None')

def test_set_min_rpm():
    rand = str(random.randint(1, 49))
    _test('set', '--min-rpm', rand)
    for param in ('-v', '--ventilation'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Minimum RPM: {}%'.format(rand),
                   'Maximum RPM', 'Current RPM')
        assert not _in(result.stdout, 'None')

def test_set_max_rpm():
    rand = str(random.randint(50, 99))
    _test('set', '--max-rpm', rand)
    for param in ('-v', '--ventilation'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'Maximum RPM: {}%'.format(rand),
                   'Minimum RPM', 'Current RPM')
        assert not _in(result.stdout, 'None')

def test_set_miner():
    rand = str(random.randint(0, 100))
    action_response = {'on': 'on',
                       'off': 'off',
                       'register': 'on',
                       'deregister': 'disabled'}

    for action, response in action_response.items():
        _test('set', '--miner', rand, action)
        for param in ('-q', '--query'):
            result = _test(param, rand)
            assert result.returncode == 0
            assert _in(result.stdout, 'Miner #{} state: {}'
                       .format(rand, response))
            assert not _in(result.stdout, 'None')

def test_set_miner_non_integer_id():
    result = _test('set', '--miner', 'HELLO', 'off')
    assert result.returncode == 1
    assert _in(result.stdout, 'help', 'usage: minerctl',
               'Miner ID has to be an integer!')

def test_set_miner_unsupported_action():
    rand = str(random.randint(0, 100))
    result = _test('set', '--miner', rand, 'HELLO')
    assert result.returncode == 1
    assert _in(result.stdout, 'help', 'usage: minerctl',
               'Invalid miner action!')

def test_set_proportional():
    rand = str(random.randint(0, 10))
    _test('set', '--proportional', rand)
    for param in ('-p', '--pid'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'proportional: {}'.format(rand),
                   'integral', 'derivative', 'bias')
        assert not _in(result.stdout, 'None')

def test_set_integral():
    rand = str(random.randint(0, 10))
    _test('set', '--integral', rand)
    for param in ('-p', '--pid'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'integral: {}'.format(rand),
                   'proportional', 'derivative', 'bias')
        assert not _in(result.stdout, 'None')

def test_set_derivative():
    rand = str(random.randint(0, 10))
    _test('set', '--derivative', rand)
    for param in ('-p', '--pid'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'derivative: {}'.format(rand),
                   'integral', 'proportional', 'bias')
        assert not _in(result.stdout, 'None')

def test_set_bias():
    rand = str(random.randint(0, 10))
    _test('set', '--bias', rand)
    for param in ('-p', '--pid'):
        result = _test(param)
        assert result.returncode == 0
        assert _in(result.stdout, 'bias: {}'.format(rand),
                   'integral', 'derivative', 'proportional')
        assert not _in(result.stdout, 'None')
