from rest_framework import serializers
from books.models import Book


class BookBatchSerializer(serializers.ListSerializer):
    def update(self, instances, validated_data):
        return [
            self.child.update(instances[index], attrs)
            for index, attrs in enumerate(validated_data)
        ]


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "user", "folder"]

        list_serializer_class = BookBatchSerializer
