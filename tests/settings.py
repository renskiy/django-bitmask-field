import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'secret_key'

MIDDLEWARE_CLASSES = []

INSTALLED_APPS = ['tests']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
