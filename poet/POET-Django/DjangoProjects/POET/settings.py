'''
Approved for Public Release: 12-3351. Distribution Unlimited
			(c)2012-The MITRE Corporation. 
Licensed under the Apache License, Version 2.0 (the "License");
			you may not use this file except in compliance with the License.
			You may obtain a copy of the License at
			http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
'''

# Django settings for POET project.
LOCAL = True

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SESSION_COOKIE_SECURE = False

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

if LOCAL:
	DATABASE_NAME = 'C:/POET/POET-Django/DjangoProjects/POET/poetDatabase.db'
	LOG_NAME = 'C:/POET/POET-Django/DjangoProjects/POET/poet_debug.log'
	SURVEY_DIR = 'survey_results/'
	REQUEST_LOG_NAME = 'C:/POET/POET-Django/DjangoProjects/POET/poet_request.log'
	MEDIA_ROOT = 'C:/POET/POET-Django/DjangoTemplates/media/'
	MEDIA_URL = ''
	STATIC_ROOT = ''
	STATIC_URL = '/static/'
	MEDIA_STATIC_URL = '/static/'
	STATICFILES_DIRS = (
	"C:/POET/POET-Django/DjangoTemplates/css",
	"C:/POET/POET-Django/DjangoTemplates/media",
	"C:/POET/POET-Django/DjangoTemplates/media/node_videos",)
	TEMPLATE_DIRS = ("C:/POET/POET-Django/DjangoTemplates")
else:
	DATABASE_NAME = '/var/www/html/poet-svn/POET-Django/DjangoProjects/POET/poetDatabase.db'
	LOG_NAME = '/var/www/html/poet-svn/POET-Django/DjangoProjects/POET/poet_debug.log'
	SURVEY_DIR = '/var/www/html/poet-svn/POET-Django/DjangoTemplates/static/survey_results/'
	REQUEST_LOG_NAME = '/var/www/html/poet-svn/POET-Django/DjangoProjects/POET/poet_request.log'
	MEDIA_ROOT  = '/var/www/html/poet-svn/POET-Django/DjangoTemplates/'
	MEDIA_URL   = 'http://poet.mitre.org/media/'
	STATIC_ROOT = '/var/www/html/poet-svn/POET-Django/DjangoTemplates/static'
	STATIC_URL = '/static/'
	MEDIA_STATIC_URL = ''
	STATICFILES_DIRS = (
        "/var/www/html/poet-svn/POET-Django/DjangoTemplates/css",
        "/var/www/html/poet-svn/POET-Django/DjangoTemplates/media",
        "/var/www/html/poet-svn/POET-Django/DjangoTemplates/media/node_images",
        "/var/www/html/poet-svn/POET-Django/DjangoTemplates/media/node_videos",)
	TEMPLATE_DIRS = ("/var/www/html/poet-svn/POET-Django/DjangoTemplates")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DATABASE_NAME,  # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

AUTH_PROFILE_MODULE = 'brainstorming.UserProfile'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index.html'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = 'C:/POET/POET-Django/DjangoTemplates/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
#MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
#STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
#STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
'''
STATICFILES_DIRS = (
	"C:/POET/POET-Django/DjangoTemplates/css",
	"C:/POET/POET-Django/DjangoTemplates/media",
	"C:/POET/POET-Django/DjangoTemplates/media/node_videos",
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
'''

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'mbt5kn-^)3fnf&vm^fh(-3qj1!2b2+kb_wxbs&@(qhh7kj6cl$'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'brainstorming.middleware.RedirectionAndLoggingMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'POET.urls'

'''
TEMPLATE_DIRS = (
	"C:/POET/POET-Django/DjangoTemplates"
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
'''

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'brainstorming',
    'easy_thumbnails',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
	'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
		'request': {
            'format': '%(asctime)s %(message)s '
        },
		'standard': {
            'format': '%(levelname)-7s %(asctime)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
		'log_file':{
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'formatter': 'standard',
			'filename': LOG_NAME # defined above
        },
		'request_log':{
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'formatter': 'request',
			'filename': REQUEST_LOG_NAME # defined above
        },
		'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple',
        },
		
    },
    'loggers': {
	    'POET': {
			'handlers': ['log_file'],
			'level': 'DEBUG',
			'propagate': False,
		},
		'POET.brainstorming': {
			'handlers': ['log_file'],
			'level': 'DEBUG',
			'propagate': False, #ensures that message don't get sent to POET at well
		},
		'Access_Logger': {
			'handlers': ['log_file'],
			'level': 'DEBUG',
			'propagate': False,
		},
		'Request_Logger': {
			'handlers': ['request_log'],
			'level': 'DEBUG',
			'propagate': False,
		},
    }
}

'''
# this logs SQL queries
'django': {
			'handlers':['log_file'],
			'propagate': True,
			'level':'DEBUG',
		},
'''
