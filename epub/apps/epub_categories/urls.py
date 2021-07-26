from django.urls import path
from epub.apps.epub_categories.views.category import (
    CategoryListCreateAPIView,
    CategoryRetrieveUpdateDestroyAPIView,
    CategorySortAPIView,
    CategoryBatchAPIView,
)

urlpatterns = [
    path("", CategoryListCreateAPIView.as_view(), name="category_list_create_api"),
    path(
        "<int:pk>/",
        CategoryRetrieveUpdateDestroyAPIView.as_view(),
        name="category_retrieve_update_destroy_api",
    ),
    path("sort", CategorySortAPIView.as_view(), name="category_sort_api"),
    path("batch", CategoryBatchAPIView.as_view(), name="category_batch_api"),
]
