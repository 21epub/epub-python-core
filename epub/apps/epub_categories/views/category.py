from rest_framework import generics
from rest_framework.response import Response
from django.apps import apps

# Create your views here.
from epub.core.http.mixins import CreateResponseMixin, RetrieveUpdateDeleteResponseMixin
from epub.apps.epub_categories.serializers.category import (
    CategorySerializer,
    CategoryRetrieveUpdateDeleteSerializer,
    CategorySortSerializer,
    CategoryBatchSerializers,
)
from epub.apps.epub_categories.models.category import Category
from epub.core.filters import CommonTypeFilterBackend, CommonUserFilterBackend


class CategoryListCreateAPIView(CreateResponseMixin, generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    filter_backends = [CommonTypeFilterBackend, CommonUserFilterBackend]

    def get_queryset(self):
        order_by = self.kwargs.get("order_by", "position")
        queryset = Category.objects.filter(parent=None).order_by(order_by)
        return queryset


class CategoryRetrieveUpdateDestroyAPIView(
    RetrieveUpdateDeleteResponseMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = CategoryRetrieveUpdateDeleteSerializer
    queryset = Category.objects.all()


class CategorySortAPIView(CreateResponseMixin, generics.CreateAPIView):
    serializer_class = CategorySortSerializer
    queryset = Category.objects.all()


class CategoryBatchAPIView(CreateResponseMixin, generics.CreateAPIView):
    serializer_class = CategoryBatchSerializers

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_model = apps.get_model(
            serializer.validated_data.get("app_name"),
            serializer.validated_data.get("model_name"),
        )
        for content_id in serializer.validated_data.get("content_ids"):
            content_obj = app_model.objects.get(id=content_id)
            content_obj.categories.clear()
            content_obj.categories.add(*serializer.validated_data.get("category_ids"))
        return Response(data={"data": "操作成功"}, status=200)
