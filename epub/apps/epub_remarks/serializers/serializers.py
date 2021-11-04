from rest_framework import serializers

from epub.apps.account.mixins import get_user_and_subuser_id_nickname
from epub.apps.epub_remarks.models import Remark


class RemarkSerializer(serializers.ModelSerializer):
    usernickname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Remark
        fields = ["id", "content", "user_id", "usernickname", "created"]
        extra_kwargs = {
            "user_id": {"read_only": True},
            "created": {"read_only": True},
        }

    def get_usernickname(self, obj):
        return obj.nickname

    def create(self, validated_data):
        request = self.context.get("request")
        user_id, subuser_id, nickname = get_user_and_subuser_id_nickname(request)
        validated_data["user_id"] = user_id
        validated_data["subuser_id"] = subuser_id
        validated_data["nickname"] = nickname

        obj = self.context.get("view").create_remark_for_obj()

        remark = obj.remarks.create(**validated_data)
        return remark
