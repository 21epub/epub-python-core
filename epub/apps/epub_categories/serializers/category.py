import copy

from epub.apps.epub_categories.models.category import Category
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.http import Http404
from django.apps import apps


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(default=[])
    id = serializers.IntegerField(required=False)

    def get_user_and_subuser_id(self, request):
        if request and request.user.is_authenticated:
            user_id = request.user.id
            subuser_id = request.user.subuser_id

        else:
            subuser_id = None
            user_id = None

        return user_id, subuser_id

    def validate(self, attrs):
        parent_id = self.initial_data.get("parent")
        if parent_id:
            try:
                position = Category.get_current_max_position(parent_id=parent_id)
            except Category.DoesNotExist:
                raise Http404
            # 设置 parent
            try:
                obj = Category.objects.get(pk=parent_id)
            except Category.DoesNotExist:
                raise Http404
            attrs["parent"] = obj
        else:
            position = Category.get_current_max_position()

        # 设置 position
        if position:
            attrs["position"] = position + Category.POSITION_STEP
        else:
            attrs["position"] = Category.POSITION_STEP
        attrs['category_type'] = self.context.get('view').kwargs.get('category_type')
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user_id, subuser_id = self.get_user_and_subuser_id(request)
        validated_data['user_id'] = user_id
        validated_data['subuser_id'] = subuser_id
        return super().create(validated_data)

    def get_children(self, obj):
        try:
            ser = CategorySerializer(obj.children, many=True)
        except AttributeError:
            return []
        return ser.data

    class Meta:
        model = Category
        exclude = [
            "parent",
        ]
        extra_kwargs = {
            'category_type': {"required": False}
        }



class CategoryRetrieveUpdateDeleteSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(default=[])

    def get_children(self, obj):
        try:
            ser = CategorySerializer(obj.children, many=True)
        except AttributeError:
            return []
        return ser.data

    class Meta:
        model = Category
        fields = ["title", "children", "user_id", "subuser_id", "position"]
        extra_kwargs = {
            "children": {"read_only": True},
            "user_id": {"read_only": True},
            "subuser_id": {"read_only": True},
            "position": {"read_only": True}
        }


class CategorySortSerializer(serializers.ModelSerializer):

    def validate(self, attrs):

        target = self.initial_data.get("target")
        before = self.initial_data.get("before")
        after = self.initial_data.get("after")
        parent = self.initial_data.get("parent")

        self.target_obj = Category.objects.get(pk=target)

        self.set_position(before, after, parent)

        attrs["target_obj"] = self.target_obj

        return attrs

    def create(self, validated_data):
        instance = validated_data.get("target_obj")
        return instance

    def reset_position(self, parent):
        all_obj = Category.objects.filter(parent=parent).order_by("position")
        for cnt, obj in enumerate(all_obj, 1):
            obj.position = Category.POSITION_STEP * cnt
            obj.save()

    def set_position(self, before, after, parent):
        target_obj = self.target_obj

        if before and after:
            before_obj = Category.objects.filter(pk=before).first()
            after_obj = Category.objects.filter(pk=after).first()
            parent_obj = before_obj.parent

            # 移到两个之间
            position = (before_obj.position + after_obj.position) / 2

            if position <= 2:
                self.reset_position(parent_obj)

                before_obj = Category.objects.filter(pk=before).first()
                after_obj = Category.objects.filter(pk=after).first()

                # 移到两个之间
                position = (before_obj.position + after_obj.position) / 2

        elif before is None and after is not None:
            after_obj = Category.objects.filter(pk=after).first()
            parent_obj = after_obj.parent

            # 移到最前
            position = after_obj.position / 2

            if position <= 2:

                # 重新编排所有对象的顺序
                self.reset_position(parent=parent_obj)

                # 顺序重置后再次获取新的 position

                after_obj = Category.objects.filter(pk=after).first()
                # 移到最前
                position = after_obj.position / 2
        elif after is None and before is not None:
            before_obj = Category.objects.filter(pk=before).first()
            parent_obj = before_obj.parent

            # 移到最后
            position = before_obj.position + Category.POSITION_STEP
        else:
            # 作为子元素移动到一个元素的最后位置
            parent_obj = Category.objects.get(pk=parent)
            current_max_position = Category.get_current_max_position(
                parent_id=parent_obj.id
            )
            if current_max_position:
                position = current_max_position + Category.POSITION_STEP
            else:
                position = Category.POSITION_STEP

        target_obj.position = position
        target_obj.parent = parent_obj
        target_obj.save()


    class Meta:
        model = Category
        fields = ["id", "position", "parent"]


class CategoryBatchSerializers(serializers.ModelSerializer):

    def validate(self, attrs):
        kwargs = self.context.get('view').kwargs
        attrs["app_name"] = kwargs.get("app_name")
        attrs["model_name"] = kwargs.get("model_name")
        try:
            app_model = apps.get_model(attrs.get('app_name'), attrs.get('model_name'))
        except LookupError:
            raise ValidationError("数据类型不存在.")
        content_ids = self.initial_data.get('content_ids')
        category_ids = self.initial_data.get('category_ids')
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
