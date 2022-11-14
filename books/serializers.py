from rest_framework import serializers
from books.models import Book


class BookBatchSerializer(serializers.ListSerializer):
    def update(self, instances, validated_data):
        for index, obj in enumerate(instances):
            self.child.update(obj, validated_data[index])
        return instances


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "user", "folder"]

        list_serializer_class = BookBatchSerializer
