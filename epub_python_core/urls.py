"""test_epub_core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from epub.core.k8s.views import ping

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ping", ping, name="ping"),
    path(
        "v3/api/logs/",
        include(("epub.apps.epub_logs.urls", "epub_logs"), namespace="log_api_url"),
    ),
    path(
        "v3/api/labels/",
        include(
            ("epub.apps.epub_labels.urls", "epub_labels"), namespace="label_api_url"
        ),
    ),
    re_path(
        r"v3/api/(?P<book_type>cbt|quiz|doc|video|h5|docset|poster)/",
        include(("books.urls", "books"), namespace="book"),
    ),
]
