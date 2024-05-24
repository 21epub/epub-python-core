from django.db import transaction
from django.db.models import RestrictedError
from epub.core.http.mixins import CreateResponseMixin, RetrieveUpdateDeleteResponseMixin
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from epub.core.http.paginations import LargeResultsSetPagination
from epub.apps.account.permissions import IsOwnerOrReadOnly
from epub.apps.epub_labels.models import Label, AppLabel
from epub.apps.epub_labels.serializers import LabelSerializer, AppLabelSerializers


class LableListAPIView(CreateResponseMixin, generics.ListCreateAPIView):
    serializer_class = LabelSerializer
    pagination_class = LargeResultsSetPagination
    permissions = {
        "POST": "admin.label.menu",
    }

    def get_queryset(self):
        queryset = Label.objects.filter(user_id=self.request.user.id).order_by("-id")
        return queryset


class LableDetailAPIView(
    RetrieveUpdateDeleteResponseMixin, RetrieveUpdateDestroyAPIView
):
    serializer_class = LabelSerializer
    queryset = Label.objects.all()
    lookup_url_kwarg = "pk"
    permission_classes = [
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        queryset = Label.objects.filter(user_id=self.request.user.id)
        return queryset

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except RestrictedError:
            raise ValidationError("linked")


class AppLabelListAPIView(CreateResponseMixin, generics.ListCreateAPIView):
    serializer_class = AppLabelSerializers
    pagination_class = LargeResultsSetPagination
    permissions = {
        "POST": "admin.label.menu",
    }

    def get_serializer(self, *args, **kwargs):
        many = kwargs.pop("many", True)
        _data = kwargs.get("data", [])
        for row in _data:
            row["type"] = self.kwargs.get("type")
        return super().get_serializer(many=many, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        _type = self.kwargs.get("type")
        AppLabel.objects.filter(linked_app=_type, user_id=self.request.user.id).delete()
        serializer.save()

    def get_queryset(self):
        return AppLabel.objects.filter(
            linked_app=self.kwargs["type"], user_id=self.request.user.id
        )
