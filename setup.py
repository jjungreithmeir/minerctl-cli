from setuptools import setup

setup(
    name='minerctl_cli',
    version='1.0',
    py_modules=['cli'],
    install_requires=[
        'PyJWT==1.6.4',
        'requests==2.19.1',
        'configparser==3.5.0',
        'cryptography==2.2.2'
    ],
    entry_points='''
        [console_scripts]
        minerctl=cli:main
    ''',
)
