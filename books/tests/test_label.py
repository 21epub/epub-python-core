from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from epub.apps.epub_labels.models import Label, AppLabel


class LabelContentDB(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user1 = User.objects.create_user(username="test")

        label = {
            "height": 100,
            "tags": ["one", "two", "three"],
            "module": "engine",
            "correct": True,
        }
        book = Book(
            title="test",
            label=label,
            user_id=self.user1.id,
        )
        book.save()

        label = {
            "height": 102,
            "tags": ["one", "threee"],
            "module": "engine2",
            "correct": True,
        }
        book = Book(
            title="test2",
            label=label,
            user_id=self.user1.id,
        )
        book.save()

        label = {"height": 103, "tags": ["two"], "module": "engine3", "correct": False}
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

        label = {"height": "", "tags": [], "module": ""}
        book = Book(
            title="test5",
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
        # 子集
        # 1. {'tags': ['four', 'three']}
        # 2. {'tags': ['two']}
        # 3. {'tags': []}
        self.assertEqual(bs.count(), 3)

        bs = Book.objects.filter(label__height=103)
        self.assertEqual(bs.count(), 1)

        bs = Book.objects.filter(label__height__lte=102)
        self.assertEqual(bs.count(), 2)

        bs = Book.objects.filter(label__height__gte=102)
        self.assertEqual(bs.count(), 4)

        bs = Book.objects.filter(label__module="engine2")
        self.assertEqual(bs.count(), 1)

        bs = Book.objects.filter(label__module__regex="engine")
        self.assertEqual(bs.count(), 4)

        bs = Book.objects.filter(label__module__icontains="engine")
        self.assertEqual(bs.count(), 4)

        bs = Book.objects.filter(label__module__contains="engine")
        self.assertEqual(bs.count(), 1)

        bs = Book.objects.filter(label__correct=True)
        self.assertEqual(bs.count(), 2)

        bs = Book.objects.filter(label__correct=False)
        self.assertEqual(bs.count(), 1)

        # 同一个标签支持多选，条件关系是 or
        # 不同标签之间，条件关系是 and
        bs = Book.objects.filter(Q(label__height=103) | Q(label__height=104))
        self.assertEqual(bs.count(), 2)

        bs = Book.objects.filter(
            Q(label__tags__contains="one") | Q(label__tags__contains="three")
        )
        self.assertEqual(bs.count(), 3)

        bs = Book.objects.filter(
            Q(label__module__contains="engine2") | Q(label__module__contains="engine3")
        )
        self.assertEqual(bs.count(), 2)

        bs = Book.objects.filter(Q(label__correct=True) | Q(label__correct=False))
        self.assertEqual(bs.count(), 3)

        bs = Book.objects.filter(
            Q(label__correct=True) | Q(label__correct=False),
            Q(label__module__contains="engine2") | Q(label__module__contains="engine3"),
        )
        self.assertEqual(bs.count(), 2)

        bs = Book.objects.filter(
            Q(label__correct=True) | Q(label__correct=False),
            Q(label__module__contains="engine") | Q(label__module__contains="engine4"),
        )
        self.assertEqual(bs.count(), 1)

        bs = Book.objects.filter(
            Q(label__module__contains="engine") | Q(label__module__contains="engine4"),
            label__correct=True,
        )
        self.assertEqual(bs.count(), 1)

        bs = Book.objects.filter(
            Q(label__module__contains="engine") | Q(label__module__contains="engine4"),
            label__correct=False,
        )
        self.assertEqual(bs.count(), 0)

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

        label_correct = Label(
            cid="correct",
            title="正确",
            value_type=Label.VALUE_TYPE_CHOICES.bool,
            input_type=Label.INPUT_TYPE_CHOICES.bool,
        )
        label_correct.save()

        AppLabel(linked_app="cbt", label=label_height).save()
        AppLabel(linked_app="cbt", label=label_tags).save()
        AppLabel(linked_app="cbt", label=label_module).save()
        AppLabel(linked_app="cbt", label=label_correct).save()

    def test_label_filter_view(self):
        self.create_label()

        url = reverse("book:book_list_api", kwargs={"book_type": "cbt"})
        query_params = {"label.height": 102}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 1)

        url = reverse("book:book_list_api", kwargs={"book_type": "cbt"})
        query_params = {"label.height": "error type"}
        res = self.client.get(url, data=query_params)
        # 给错误的类型，从报错修改为忽略这个条件
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get("data").get("sum"), 5)

        query_params = {"label.module": "engine4"}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 1)

        query_params = {"label.module": "engine"}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 1)

        query_params = {"label.module": "engine4", "label.height": 103}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 0)

        query_params = {"label.tags": "one"}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 2)

        query_params = {"label.correct": "true"}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 2)

        query_params = {"label.correct": "false"}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 1)

        query_params = {"label.correct": "null"}
        res = self.client.get(url, data=query_params)
        self.assertEqual(res.data.get("data").get("sum"), 2)

        query = "label.height=103&label.height=104"
        url = url + "?" + query
        res = self.client.get(url)
        self.assertEqual(res.data.get("data").get("sum"), 2)

        _query = "label.tags=one&label.tags=three"
        url = url.replace(query, _query)
        res = self.client.get(url)
        self.assertEqual(res.data.get("data").get("sum"), 3)
        query = _query

        _query = "label.module=engine2&label.module=engine3"
        url = url.replace(query, _query)
        res = self.client.get(url)
        self.assertEqual(res.data.get("data").get("sum"), 2)
        query = _query

        _query = "label.correct=true&label.correct=false"
        url = url.replace(query, _query)
        res = self.client.get(url)
        self.assertEqual(res.data.get("data").get("sum"), 3)
        query = _query

        _query = "label.correct=true&label.correct=false&label.module=engine2&label.module=engine3"
        url = url.replace(query, _query)
        res = self.client.get(url)
        self.assertEqual(res.data.get("data").get("sum"), 2)
        query = _query

        _query = "label.correct=true&label.correct=false&label.module=engine&label.module=engine4"
        url = url.replace(query, _query)
        res = self.client.get(url)
        self.assertEqual(res.data.get("data").get("sum"), 1)
        query = _query

        _query = "label.correct=true&label.module=engine&label.module=engine4"
        url = url.replace(query, _query)
        res = self.client.get(url)
        self.assertEqual(res.data.get("data").get("sum"), 1)
        query = _query

        _query = "label.correct=false&label.module=engine&label.module=engine4"
        url = url.replace(query, _query)
        res = self.client.get(url)
        self.assertEqual(res.data.get("data").get("sum"), 0)
        query = _query

        _query = "label.correct=null&label.module=engine4"
        url = url.replace(query, _query)
        res = self.client.get(url)
        self.assertEqual(res.data.get("data").get("sum"), 1)
        query = _query

        _query = "label.correct=null&label.module=engine"
        url = url.replace(query, _query)
        res = self.client.get(url)
        self.assertEqual(res.data.get("data").get("sum"), 0)
