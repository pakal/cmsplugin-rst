"""Minimal django settings to run the pytest suite (see also test_settings.py for the demo project)."""

import os

import cms

CMS_VERSION = tuple(int(x) for x in cms.__version__.split(".")[:2])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = "cmsplugin-rst-tests"
DEBUG = False
ALLOWED_HOSTS = ["*"]
SITE_ID = 1
USE_TZ = True
ROOT_URLCONF = "tests.urls"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "cms",
    "menus",
    "treebeard",
    "sekizai",
    "cmsplugin_rst",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "cms.context_processors.cms_settings",
            ],
        },
    }
]

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("fr", "French")]

CMS_TEMPLATES = [("page.html", "Page")]
CMS_CONFIRM_VERSION4 = True  # needed by django-cms>=4, ignored by older versions
