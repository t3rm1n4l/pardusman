# -*- coding: utf-8 -*-
# Django settings for pardusman project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'pardus'             # Or path to database file if using sqlite3.
DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
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

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/mycode/pardusman/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''


#Path of the directory where repositories are located
REPOS_URL = '/mnt/sda7/pardus-repo'

#A directory which acts as /tmp for pardusman
TMP_FILES = '/home/mycode/files'

#A directory used to keep uploaded wallpapers
TMP_WALLPAPERS = '/home/mycode/wallpapers_collection'

#A directory used to keep generated project files (.tar.gz)
PROJECT_FILES = '/home/mycode/project_files'

#A directory for keeping build logs
BUILD_LOGS = '/home/mycode/logs'

#Max number of builds that can be handled by the server at a time
BUILD_LIMIT = 2

#A directory where all the built images are stored
BUILDS_DIR = '/home/mycode/builds'

#Base url for making download links available [ A reference link ]
BASE_PROJECTS_URL = 'http://localhost/pardusman'

#Time interval for the Buildfarm Queue
TIME_INTERVAL = 2

#Build cache directory for Pardusman image builds
BUILD_CACHE_DIR = '/mnt/sda7/pardus-repo/buildcache'

# Supported Image formats for builds
IMAGE_FORMATS = ['.iso','.qemu']

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+(@bf4wwoc0*k^@qn37#%f!6fhc&lfq4+-pa6mou9vdjd2(9ix'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.CacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'pardusman.urls'

TEMPLATE_DIRS = (
     '/home/mycode/pardusman/templates/',
     '/home/mycode/pardusman/templates/pages',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'pardusman.wizard',
)
