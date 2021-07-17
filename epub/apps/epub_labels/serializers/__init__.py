from epub.core.fields import ShowValueChoiceField
from rest_framework.exceptions import ValidationError

from epub.apps.account.mixins import SetCreatorMixin, get_user_and_subuser_id_nickname
from epub.apps.epub_labels.models.db import Label, AppLabel

from rest_framework import serializers


class LabelSerializer(SetCreatorMixin, serializers.ModelSerializer):
    input_type = ShowValueChoiceField(choices=Label.INPUT_TYPE_CHOICES)
    value_type = ShowValueChoiceField(choices=Label.VALUE_TYPE_CHOICES)
    linked = serializers.BooleanField(read_only=True)

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        if self.instance:
            create_only_fields = getattr(self.Meta, "create_only_fields", None)
            for x in create_only_fields:
                ret.pop(x, None)
        return ret

    class Meta:
        model = Label
        exclude = ("is_removed",)
        read_only_fields = (
            "id",
            "user_id",
            "subuser_id",
            "nickname",
            "created",
            "modified",
            "linked",
        )
        create_only_fields = ("cid", "value_type")


class AppLabelSerializers(SetCreatorMixin, serializers.ModelSerializer):

    label = LabelSerializer(read_only=True)
    id = serializers.IntegerField(source="label_id", write_only=True)
    type = serializers.CharField(source="linked_app", write_only=True)

    def validate_id(self, label_id):
        request = self.context.get("request")
        user_id, subuser_id, nickname = get_user_and_subuser_id_nickname(request)
        if Label.objects.filter(id=label_id, user_id=user_id):
            return label_id
        else:
            raise ValidationError("notfound")

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        label = ret.pop("label")
        return {**ret, **label}

    class Meta:
        model = AppLabel
        fields = ["id", "label", "required", "show_in_list", "can_query", "type"]
