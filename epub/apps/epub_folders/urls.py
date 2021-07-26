from django.urls import path
from epub.apps.epub_folders.views.folder import (
    FolderListCreateAPIView,
    FolderRetrieveUpdateDestroyAPIView,
    FolderSortAPIView,
    FolderBatchAPIView,
)

urlpatterns = [
    path("", FolderListCreateAPIView.as_view(), name="folder_list_create_api"),
    path(
        "<int:pk>/",
        FolderRetrieveUpdateDestroyAPIView.as_view(),
        name="folder_retrieve_update_destroy_api",
    ),
    path("sort", FolderSortAPIView.as_view(), name="folder_sort_api"),
    path("batch", FolderBatchAPIView.as_view(), name="folder_batch_api"),
]
