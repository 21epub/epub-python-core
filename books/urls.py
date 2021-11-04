from django.urls import re_path, include, path
from books.views import BookListAPIView, BookRemarkListCreateAPIView
from epub.apps.epub_remarks.views.api import RemarkRetrieveDestroyAPIView

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
    # 为了验证单元测试 数据类型不存在的情况
    re_path(
        "folders_for_test/",
        include(
            ("epub.apps.epub_folders.urls", "epub_folders"),
            namespace="epub_folders_test",
        ),
        {
            "folder_type": "h5",
            "app_name": "books",
            "model_name": "Book_temp",
            "user_filter": ["user_id", "subuser_id"],
        },
    ),
    path("books/<int:pk>/remarks", BookRemarkListCreateAPIView.as_view(), name="book_remark_list_create_api"),
    # path("books/<int:pk>/remarks/<int:remark_id>", RemarkRetrieveDestroyAPIView.as_view(), name="book_remark_single_api")
    path("books/<int:pk>/remarks/",
         include(("epub.apps.epub_remarks.urls.api", "epub_remarks"), namespace="book_remarks"))
]
