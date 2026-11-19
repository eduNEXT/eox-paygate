"""
Settings for the tests of eox-paygate.

In a real-world use case the app is installed into the LMS, so these settings are not used. They mirror the test
settings of openedx-zeitlabs-payments, whose edx-platform mocks are on the ``PYTHONPATH`` while the tests run.
"""

USE_TZ = True
TIME_ZONE = 'UTC'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.sessions',
    'waffle',
    'fake_models',
    'zeitlabs_payments',
    'eox_paygate',
)

SECRET_KEY = 'insecure-secret-key'

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'edx_django_utils.cache.middleware.RequestCacheMiddleware',
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'django.template.context_processors.request',
        ],
    },
}]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

ECOMMERCE_PUBLIC_URL_ROOT = 'test.com'
ZEITLABS_PAYMENTS_SETTINGS = {
    'invoice_prefix': 'TEST',
    'organization_info': {'name': 'test_org', 'vat_no': '112233'},
    'valid_currency': 'EUR',
}
IS_ZEITLABS_PAYMENTS_ENABLED = False
SITE_ID = 1
