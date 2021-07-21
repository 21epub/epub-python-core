# epub-python-core

[![django_action](https://github.com/21epub/epub-python-core/actions/workflows/django.yml/badge.svg)](https://github.com/21epub/epub-python-core/actions)
[![codecov](https://codecov.io/gh/21epub/epub-python-core/branch/master/graph/badge.svg?token=f6brEueSJ1)](https://codecov.io/gh/21epub/epub-python-core)


公司项目基础库

项目配置

### settings.py
```python

### See  https://github.com/21epub/epub-python-core/blob/master/epub/conf/settings.py
from epub.conf.settings import *

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "epub.apps.epub_auth", # epub_auth.User model for AUTH_USER_MODEL
    "your_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "your_project.urls"


WSGI_APPLICATION = "your_project.wsgi.application"
```


### 项目根路径下配置： .env 文件
```
DEBUG=on
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///my-local-sqlite.db
CACHE_URL=locmemcache://
```

