from rest_framework import generics
from rest_framework.response import Response
from django.apps import apps

# Create your views here.
from epub.core.http.mixins import CreateResponseMixin, RetrieveUpdateDeleteResponseMixin
from epub.apps.epub_folders.serializers.folder import (
    FolderSerializer,
    FolderRetrieveUpdateDeleteSerializer,
    FolderSortSerializer,
    FolderBatchSerializers,
)
from epub.apps.epub_folders.models.folder import Folder
from epub.core.filters import CommonTypeFilterBackend, CommonUserFilterBackend
from epub.core.http.paginations import LargeResultsSetPagination


class FolderListCreateAPIView(CreateResponseMixin, generics.ListCreateAPIView):
    serializer_class = FolderSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [CommonTypeFilterBackend, CommonUserFilterBackend]

    def get_queryset(self):
        queryset = Folder.objects.filter(parent=None).order_by("-position")
        return queryset


class FolderRetrieveUpdateDestroyAPIView(
    RetrieveUpdateDeleteResponseMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = FolderRetrieveUpdateDeleteSerializer
    queryset = Folder.objects.all()


class FolderSortAPIView(CreateResponseMixin, generics.CreateAPIView):
    serializer_class = FolderSortSerializer
    queryset = Folder.objects.all()


class FolderBatchAPIView(CreateResponseMixin, generics.CreateAPIView):
    serializer_class = FolderBatchSerializers

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_model = apps.get_model(
            serializer.validated_data.get("app_name"),
            serializer.validated_data.get("model_name"),
        )
        for content_id in serializer.validated_data.get("content_ids"):
            content_obj = app_model.objects.get(id=content_id)
            content_obj.folder_id = serializer.validated_data.get("folder_id")
            content_obj.save()
        return Response(data={"data": "操作成功"}, status=200)
