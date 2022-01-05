from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics


# Create your views here.
from epub.apps.epub_labels.views.filters import LabelFilter
from epub.apps.epub_logs.mixins import LoggingViewSetMixin
from epub.apps.epub_remarks.views.api import RemarkListCreateAPIView
from epub.core.http.renderer import JSRenderer
from books.models import Book
from books.serializers import BookListSerializer
from epub.apps.epub_categories.views.filters import ContentCategoryFilterBackend
from epub.apps.epub_folders.views.filters import ContentFolderFilterBackend


class JSView(APIView):
    renderer_classes = [JSRenderer]

    def get(self, request):
        return Response("var js=1;", content_type="application/javascript")


class BookListCreateAPIView(LoggingViewSetMixin, generics.ListCreateAPIView):
    serializer_class = BookListSerializer
    queryset = Book.objects.all()
    filter_backends = [
        ContentCategoryFilterBackend,
        ContentFolderFilterBackend,
        LabelFilter,
    ]

    permissions = {
        "GET": "{module_type}.list"
    }

    label_linked_app = "cbt"


class BookRemarkListCreateAPIView(RemarkListCreateAPIView):
    app_name = "books"
    model_name = "book"

    def create_remark_for_obj(self):
        pk = self.kwargs.get("pk")
        book = Book.objects.get(pk=pk)
        return book

    def list_remark_for_obj_ids(self):
        pk = self.kwargs.get("pk")
        book_ids = Book.objects.filter(pk__in=[pk]).values_list("id", flat=True)
        return book_ids
