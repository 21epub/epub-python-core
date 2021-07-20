from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics


# Create your views here.
from epub.apps.epub_labels.views.filters import LabelFilter
from epub.core.http.renderer import JSRenderer
from books.models import Book
from books.serializers import BookListSerializer
from epub.apps.epub_categories.views.filters import ContentCategoryFilterBackend
from epub.apps.epub_folders.views.filters import ContentFolderFilterBackend


class JSView(APIView):
    renderer_classes = [JSRenderer]

    def get(self, request):
        return Response("var js=1;", content_type="application/javascript")


class BookListAPIView(generics.ListAPIView):
    serializer_class = BookListSerializer
    queryset = Book.objects.all()
    filter_backends = [
        ContentCategoryFilterBackend,
        ContentFolderFilterBackend,
        LabelFilter,
    ]

    label_linked_app = "cbt"
