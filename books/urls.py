from django.urls import re_path, include


urlpatterns = [
    re_path("categorys/",
            include(("epub.apps.epub_categories.urls", "epub_categories"), namespace="epub_categories"),
            {"category_type": "h5", "app_name": "books", "model_name": "Book", "user_filter": ["user_id", "subuser_id"]})
]