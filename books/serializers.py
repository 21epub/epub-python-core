from rest_framework import serializers
from books.models import Book


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "user_id", "subuser_id"]
        extra_kwargs = {
            "user_id": {"read_only": True},
            "title": {"required": False},
            "subuser_id": {"read_only": True},
        }

    def create(self, validated_data):
        request = self.context.get("request")

        if not validated_data.get("title", None):
            validated_data["title"] = "未命名"

        validated_data["user_id"] = request.user.id
        validated_data["subuser_id"] = request.user.subuser_id
        obj = super().create(validated_data)
        return obj
