import copy

from epub.apps.epub_categories.models.category import Category
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.apps import apps
from epub.core.serializers import (
    CommonFolderListCreateSerializers,
    CommonRetrieveUpdateDeleteSerializer,
    CommonSortSerializer,
)


class CategorySerializer(CommonFolderListCreateSerializers):
    class Meta:
        model = Category

        fields = "__all__"
        extra_kwargs = {
            "category_type": {"read_only": True},
            "id": {"read_only": True},
        }

    def set_extra_attrs(self, attrs):
        category_type = getattr(self.context.get("view"), "kwargs", {}).get("category_type", None)
        if category_type:
            attrs["category_type"] = category_type
        else:
            raise serializers.ValidationError({"category_type": "folder_type must be provided"})


class CategoryRetrieveUpdateDeleteSerializer(CommonRetrieveUpdateDeleteSerializer):
    class Meta:
        model = Category
        fields = ["title", "children", "user_id", "subuser_id", "position"]
        extra_kwargs = {
            "children": {"read_only": True},
            "user_id": {"read_only": True},
            "subuser_id": {"read_only": True},
            "position": {"read_only": True},
        }


class CategorySortSerializer(CommonSortSerializer):
    class Meta:
        model = Category
        fields = ["id", "position", "parent"]


class CategoryBatchSerializers(serializers.ModelSerializer):
    def validate(self, attrs):
        kwargs = self.context.get("view").kwargs
        attrs["app_name"] = kwargs.get("app_name")
        attrs["model_name"] = kwargs.get("model_name")
        try:
            app_model = apps.get_model(attrs.get("app_name"), attrs.get("model_name"))
        except LookupError:
            raise ValidationError("数据类型不存在.")
        content_ids = self.initial_data.get("content_ids")
        category_ids = self.initial_data.get("category_ids")
        validate_content_ids = copy.copy(content_ids)
        validate_category_ids = copy.copy(category_ids)
        for content_id in content_ids:
            try:
                app_model.objects.get(id=content_id)
            except app_model.DoesNotExist:
                validate_content_ids.remove(content_id)
                continue
        for category_id in category_ids:
            try:
                Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                validate_category_ids.remove(category_id)
                continue
        attrs["content_ids"] = validate_content_ids
        attrs["category_ids"] = validate_category_ids
        return attrs

    class Meta:
        model = Category
        fields = ["id"]
