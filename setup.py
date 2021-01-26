from setuptools import setup, find_packages

APP = ['app.py']
DATA_FILES = [
    ('static', ['static/icon.png']),
    ('gcal', ['gcal/credentials.json'])
]
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'iconfile': 'static/icon.icns',
    'packages': [
        'rumps',
        'googleapiclient',
        'google',
        'google.api',
        'google.api_core',
        'google.auth',
        'google.longrunning',
        'google.oauth2',
        'google.protobuf',
        'google.rpc',
        'google.type',
        'google_auth_oauthlib',
        'dateutil'
    ],
}

setup(
    name="Caddy",
    version="0.0.1",
    author="Mike Hanssen",
    author_email="contact@mikehanssen.com",
    description="Never miss a meeting again.",
    license="MIT",
    keywords="Google,MacOS,toolbar,rumps",
    url="https://github.com/mikehanssen/caddy",
    app=APP,
    data_files=DATA_FILES,
    packages=find_packages(),
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'rumps',
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'python-dateutil'],
    dependency_links=['http://github.com/snare/rumps/tarball/master#egg=rumps'],
    zip_safe=False
)
