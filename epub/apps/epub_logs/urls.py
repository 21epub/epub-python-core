from django.conf.urls import url
from django.urls import path
from .views import LogAdminView, LogObjectView

urlpatterns = [
    path(
        "all/",
        LogAdminView.as_view(),
        name="log-admin-list",
    ),
    path(
        "<str:object_type>/<str:pk>/",
        LogObjectView.as_view(),
        name="log-object-list",
    ),
]
