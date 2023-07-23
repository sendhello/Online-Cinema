import os


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'corsheaders',
    'movies',
    'users',
]

if os.environ.get('DEBUG', 'False').title() == 'True':
    INSTALLED_APPS.append('debug_toolbar')
