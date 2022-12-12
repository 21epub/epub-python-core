from rest_framework import serializers


class CommonBatchCreateSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        model = self.child.Meta.model
        objs = [model(**data) for data in validated_data]
        instances = model.objects.bulk_create(objs)
        return instances


class CommonListCreateSerializers(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(default=[])
    id = serializers.IntegerField(required=False)
    parent = serializers.IntegerField(required=False, write_only=True)
    parent_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        list_serializer_class = CommonBatchCreateSerializer

    def get_user_and_subuser_id(self, request):
        if request and request.user.is_authenticated:
            user_id = request.user.id
            subuser_id = request.user.subuser_id

        else:
            subuser_id = None
            user_id = None

        return user_id, subuser_id

    def set_parent(self, attrs):
        if hasattr(self, "_parent_obj"):
            attrs["parent"] = getattr(self, "_parent_obj", None)
            return

        parent_id = attrs.get("parent", attrs.pop("parent_id", None))
        if parent_id:
            try:
                parent = self.Meta.model.objects.get(id=parent_id)
                attrs["parent"] = parent
            except self.Meta.model.DoesNotExist:
                raise serializers.ValidationError({"parent": f"parent {parent_id} not exists."})
            setattr(self, "_parent_obj", parent)

    def set_position(self, attrs):
        if hasattr(self, "_previous_position"):
            _previous_position = getattr(self, "_previous_position", None)
            position = _previous_position + self.Meta.model.POSITION_STEP
        else:
            if "parent" in attrs:
                filter_params = {"parent": attrs.get("parent", None)}
            else:
                filter_params = self.get_position_filter_params(attrs)
            position = self.Meta.model.get_next_position(**filter_params)

        attrs["position"] = position
        setattr(self, "_previous_position", position)

    def get_position_filter_params(self, attrs):
        """
        return dict for filter model
        """
        raise NotImplementedError("apply a dict for get max position obj when attrs has no attribute 'parent'.")

    def set_extra_attrs(self, attrs):
        """
        add extra value to validated_data:
            eg: attrs["extra_key"] = extra_value
        extra_key must be a field of self.Meta.model
        """
        pass

    def set_user(self, attrs):
        user_id, subuser_id = self.get_user_and_subuser_id(self.context.get("request"))
        attrs["user_id"] = user_id
        attrs["subuser_id"] = subuser_id

    def validate(self, attrs):
        self.set_extra_attrs(attrs)
        self.set_parent(attrs)
        self.set_user(attrs)
        self.set_position(attrs)
        return attrs

    @classmethod
    def get_children(cls, obj, order_by="position"):
        try:
            ser = cls(obj.children.order_by(order_by), many=True)
        except AttributeError:
            return []
        return ser.data

    def create(self, validated_data):
        return super().create(validated_data)


class CommonFolderListCreateSerializers(CommonListCreateSerializers):

    @classmethod
    def get_children(cls, obj, order_by="-position"):
        return super().get_children(obj, order_by=order_by)

    def get_position_filter_params(self, attrs):
        filter_params = {}
        if "user_id" in attrs:
            filter_params["user_id"] = attrs.get("user_id", None)
        return filter_params


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

        if target and any([before, after, parent]):
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
