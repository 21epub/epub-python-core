import copy

from epub.apps.epub_folders.models.folder import Folder
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.apps import apps
from epub.core.serializers import (
    CommonFolderListCreateSerializers,
    CommonRetrieveUpdateDeleteSerializer,
    CommonSortSerializer,
)


class FolderSerializer(CommonFolderListCreateSerializers):
    class Meta(CommonFolderListCreateSerializers.Meta):
        model = Folder
        fields = "__all__"
        extra_kwargs = {
            "folder_type": {"read_only": True},
            "id": {"read_only": True},
        }

    def set_extra_attrs(self, attrs):
        folder_type = getattr(self.context.get("view"), "kwargs", {}).get("folder_type", None)
        if folder_type:
            attrs["folder_type"] = folder_type
        else:
            raise serializers.ValidationError({"folder_type": "folder_type must be provided"})


class FolderRetrieveUpdateDeleteSerializer(CommonRetrieveUpdateDeleteSerializer):
    class Meta:
        model = Folder
        fields = ["title", "children", "user_id", "subuser_id", "position"]
        extra_kwargs = {
            "children": {"read_only": True},
            "user_id": {"read_only": True},
            "subuser_id": {"read_only": True},
            "position": {"read_only": True},
        }


class FolderSortSerializer(CommonSortSerializer):
    class Meta:
        model = Folder
        fields = ["id", "position", "parent"]


class FolderBatchSerializers(serializers.ModelSerializer):
    def validate(self, attrs):
        kwargs = self.context.get("view").kwargs
        attrs["app_name"] = kwargs.get("app_name")
        attrs["model_name"] = kwargs.get("model_name")
        try:
            app_model = apps.get_model(attrs.get("app_name"), attrs.get("model_name"))
        except LookupError:
            raise ValidationError("数据类型不存在.")
        content_ids = self.initial_data.get("content_ids")
        folder_id = self.initial_data.get("folder_id")
        validate_content_ids = copy.copy(content_ids)
        for content_id in content_ids:
            try:
                app_model.objects.get(id=content_id)
            except app_model.DoesNotExist:
                validate_content_ids.remove(content_id)
                continue
        try:
            Folder.objects.get(id=folder_id)
        except Folder.DoesNotExist:
            raise ValidationError("数据不存在.")
        attrs["content_ids"] = validate_content_ids
        attrs["folder_id"] = folder_id
        return attrs

    class Meta:
        model = Folder
        fields = ["id"]
