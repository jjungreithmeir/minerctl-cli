from setuptools import setup

setup(
    name='minerctl_cli',
    version='1.0',
    py_modules=['cli'],
    install_requires=[
        'argparse',
        'PyJWT',
        'requests',
        'configparser',
        'cryptography'
    ],
    entry_points='''
        [console_scripts]
        minerctl=cli:main
    ''',
)
