from rest_framework import serializers
from django.http import Http404
from epub.apps.epub_categories.models.category import Category


class CommonListCreateSerializers(serializers.ModelSerializer):
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
        parent_id = self.initial_data.get(
            "parent", self.initial_data.get("parent_id", None)
        )
        model_name = self.Meta.model
        request = self.context.get("request")
        user_id, _ = self.get_user_and_subuser_id(request)
        if parent_id:
            try:
                position = model_name.get_current_max_position(
                    parent_id=parent_id, user_id=user_id
                )
            except model_name.DoesNotExist:
                raise Http404
            # 设置 parent
            try:
                obj = model_name.objects.get(pk=parent_id)
            except model_name.DoesNotExist:
                raise Http404
            attrs["parent"] = obj
        else:
            position = model_name.get_current_max_position(user_id=user_id)

        # 设置 position
        if position:
            attrs["position"] = position + model_name.POSITION_STEP
        else:
            attrs["position"] = model_name.POSITION_STEP
        type_key = "category_type" if self.Meta.model == Category else "folder_type"
        attrs[type_key] = self.context.get("view").kwargs.get(type_key)
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user_id, subuser_id = self.get_user_and_subuser_id(request)
        validated_data["user_id"] = user_id
        validated_data["subuser_id"] = subuser_id
        return super().create(validated_data)

    @classmethod
    def get_children(cls, obj):
        try:
            ser = cls(obj.children, many=True)
        except AttributeError:
            return []
        return ser.data


class CommonRetrieveUpdateDeleteSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(default=[])

    @classmethod
    def get_children(cls, obj):
        try:
            ser = cls(obj.children, many=True)
        except AttributeError:
            return []
        return ser.data


class CommonSortSerializer(serializers.ModelSerializer):
    def validate(self, attrs):

        target = self.initial_data.get("target")
        before = self.initial_data.get("before")
        after = self.initial_data.get("after")
        parent = self.initial_data.get("parent")

        self.target_obj = self.Meta.model.objects.get(pk=target)

        self.set_position(before, after, parent)

        attrs["target_obj"] = self.target_obj

        return attrs

    def create(self, validated_data):
        instance = validated_data.get("target_obj")
        return instance

    def reset_position(self, parent):
        model_name = self.Meta.model
        all_obj = model_name.objects.filter(parent=parent).order_by("position")
        for cnt, obj in enumerate(all_obj, 1):
            obj.position = model_name.POSITION_STEP * cnt
            obj.save()

    def set_position(self, before, after, parent):
        app_model = self.Meta.model
        target_obj = self.target_obj

        if before and after:
            before_obj = app_model.objects.filter(pk=before).first()
            after_obj = app_model.objects.filter(pk=after).first()
            parent_obj = before_obj.parent

            # 移到两个之间
            position = (before_obj.position + after_obj.position) / 2

            if position <= 2:
                self.reset_position(parent_obj)

                before_obj = app_model.objects.filter(pk=before).first()
                after_obj = app_model.objects.filter(pk=after).first()

                # 移到两个之间
                position = (before_obj.position + after_obj.position) / 2

        elif before is None and after is not None:
            after_obj = app_model.objects.filter(pk=after).first()
            parent_obj = after_obj.parent

            # 移到最前
            position = after_obj.position / 2

            if position <= 2:
                # 重新编排所有对象的顺序
                self.reset_position(parent=parent_obj)

                # 顺序重置后再次获取新的 position

                after_obj = app_model.objects.filter(pk=after).first()
                # 移到最前
                position = after_obj.position / 2
        elif after is None and before is not None:
            before_obj = app_model.objects.filter(pk=before).first()
            parent_obj = before_obj.parent

            # 移到最后
            position = before_obj.position + app_model.POSITION_STEP
        else:
            # 作为子元素移动到一个元素的最后位置
            parent_obj = app_model.objects.get(pk=parent)
            current_max_position = app_model.get_current_max_position(
                parent_id=parent_obj.id
            )
            if current_max_position:
                position = current_max_position + app_model.POSITION_STEP
            else:
                position = app_model.POSITION_STEP

        target_obj.position = position
        target_obj.parent = parent_obj
        target_obj.save()
