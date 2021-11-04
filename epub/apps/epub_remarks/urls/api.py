from django.urls import re_path, path
from epub.apps.epub_remarks.views.api import (
    RemarkListCreateAPIView,
    RemarkRetrieveDestroyAPIView,
)

urlpatterns = [
    path("", RemarkListCreateAPIView.as_view(), name="remarks_list_create_api"),
    re_path(
        r"^(?P<remark_id>\d+)/?$",
        RemarkRetrieveDestroyAPIView.as_view(),
        name="remarks_single_api",
    ),
]
