from django.urls import re_path, include, path
from books.views import BookListAPIView


urlpatterns = [
    path("books/", BookListAPIView.as_view(), name="book_list_api"),
    re_path(
        "categories/",
        include(
            ("epub.apps.epub_categories.urls", "epub_categories"),
            namespace="epub_categories",
        ),
        {
            "category_type": "h5",
            "app_name": "books",
            "model_name": "Book",
            "user_filter": ["user_id", "subuser_id"],
        },
    ),
    re_path(
        "folders/",
        include(
            ("epub.apps.epub_folders.urls", "epub_folders"), namespace="epub_folders"
        ),
        {
            "folder_type": "h5",
            "app_name": "books",
            "model_name": "Book",
            "user_filter": ["user_id", "subuser_id"],
        },
    ),
]
