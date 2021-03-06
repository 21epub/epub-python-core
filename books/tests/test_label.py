from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from epub.apps.epub_labels.models import Label, AppLabel


class LabelContentDB(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user1 = User.objects.create_user(username="test")

        label = {"height": 100, "tags": ["one", "two", "three"], "module": "engine"}
        book = Book(
            title="test",
            label=label,
            user_id=self.user1.id,
        )
        book.save()

        label = {"height": 102, "tags": ["one", "threee"], "module": "engine2"}
        book = Book(
            title="test2",
            label=label,
            user_id=self.user1.id,
        )
        book.save()

        label = {"height": 103, "tags": ["two"], "module": "engine3"}
        book = Book(
            title="test3",
            label=label,
            user_id=self.user1.id,
        )
        book.save()

        label = {"height": 104, "tags": ["four", "three"], "module": "engine4"}
        book = Book(
            title="test4",
            label=label,
            user_id=self.user1.id,
        )
        book.save()

    def test_search(self):
        bs = Book.objects.filter(label__tags__contains="one")
        self.assertEqual(bs.count(), 2)

        bs = Book.objects.filter(label__tags__contains=["one", "two"])
        self.assertEqual(bs.count(), 1)

        bs = Book.objects.filter(label__tags__contained_by=["four", "two", "three"])
        # 1. {'tags': ['four', 'three']}
        # 2. {'tags': ['two']}
        self.assertEqual(bs.count(), 2)

        bs = Book.objects.filter(label__height=103)
        self.assertEqual(bs.count(), 1)

        bs = Book.objects.filter(label__height__gte=102)
        self.assertEqual(bs.count(), 3)

        bs = Book.objects.filter(label__module="engine2")
        self.assertEqual(bs.count(), 1)

        bs = Book.objects.filter(label__module__regex="engine")
        self.assertEqual(bs.count(), 4)

        bs = Book.objects.filter(label__module__icontains="engine")
        self.assertEqual(bs.count(), 4)

        bs = Book.objects.filter(label__module__contains="engine")
        self.assertEqual(bs.count(), 1)

    def create_label(self):

        label_height = Label(
            cid="height",
            title="高度",
            value_type=Label.VALUE_TYPE_CHOICES.number,
            input_type=Label.INPUT_TYPE_CHOICES.input,
        )
        label_height.save()
        label_tags = Label(
            cid="tags",
            title="TAG",
            value_type=Label.VALUE_TYPE_CHOICES.text,
            input_type=Label.INPUT_TYPE_CHOICES.multiple,
        )
        label_tags.save()
        label_module = Label(
            cid="module",
            title="模块",
            value_type=Label.VALUE_TYPE_CHOICES.text,
            input_type=Label.INPUT_TYPE_CHOICES.single,
        )
        label_module.save()

        AppLabel(linked_app="cbt", label=label_height).save()
        AppLabel(linked_app="cbt", label=label_tags).save()
        AppLabel(linked_app="cbt", label=label_module).save()

    def test_label_filter_view(self):
        self.create_label()

        url = reverse("book:book_list_api", kwargs={"book_type": "cbt"})
        query_params = {"height": 102}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 1)

        query_params = {"module": "engine4"}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 1)

        query_params = {"module": "engine"}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 1)

        query_params = {"module": "engine4", "height": 103}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 0)

        query_params = {"tags": "one"}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 2)
