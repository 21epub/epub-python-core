from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, serializers

# Create your views here.
from epub.apps.epub_labels.views.filters import LabelFilter
from epub.apps.epub_logs.mixins import LoggingViewSetMixin, LoggingMixin
from epub.apps.epub_logs.models import LogEntry
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


class BookListAPIView(LoggingViewSetMixin, generics.UpdateAPIView, generics.ListCreateAPIView):
    serializer_class = BookListSerializer
    queryset = Book.objects.all()
    filter_backends = [
        ContentCategoryFilterBackend,
        ContentFolderFilterBackend,
        LabelFilter,
    ]

    label_linked_app = "cbt"

    def get_queryset(self):
        data = self.request.data
        # 只有批量 更新 才会运行以下代码
        if isinstance(data, list):
            title_list = [x["title"] for x in data]
            if len(title_list) != len(set(title_list)):
                raise serializers.ValidationError(
                    "Multiple updates to a single slug not found"
                )
            if title_list:
                return Book.objects.filter(title__in=title_list)
        return Book.objects.all()

    def get_object(self):
        return self.get_queryset()

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)


class BookPublishAPIView(LoggingMixin, generics.CreateAPIView):
    serializer_class = BookListSerializer
    queryset = Book.objects.all()

    def get_object(self):
        return self.queryset.filter(id=self.kwargs.get("id")).first()

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.wf_publish()
        self.log(instance, action_type=LogEntry.PUBLISH, action_name="发布", user_id=instance.user_id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=200)


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
