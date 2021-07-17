from django.urls import path

from epub.apps.epub_labels.views.api import (
    LableListAPIView,
    LableDetailAPIView,
    AppLabelListAPIView,
)

urlpatterns = [
    path("", LableListAPIView.as_view(), name="label_list_api"),
    path("app/<slug:type>/", AppLabelListAPIView.as_view(), name="app_label_list_api"),
    path("<int:pk>", LableDetailAPIView.as_view(), name="label_detail_api"),
]
