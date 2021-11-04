from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book
from django.urls import reverse
from epub.apps.epub_remarks.models import Remark

User = get_user_model()


class TestBookRemarks(TestCase):

    def setUp(self) -> None:
        self.test_user = User.objects.create_user(username="test")
        self.book = Book.objects.create(title="book1", user=self.test_user)

    def test_create_book_remarks(self):
        data1 = {"content": "test book remark"}
        url = reverse(
            "book:book_remark_list_create_api", kwargs={"pk": self.book.id, "book_type": "cbt"}
        )
        self.client.post(url, data1)
        r1 = Remark.objects.filter(content="test book remark").first()
        self.assertEqual(r1.content_object, self.book)

    def test_list_book_remarks(self):
        self.book.remarks.create(content="test content")
        self.book.remarks.create(content="test content")
        url = reverse(
            "book:book_remark_list_create_api", kwargs={"pk": self.book.id, "book_type": "cbt"}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.json()["data"]["results"]
        self.assertEqual(len(results), 2)

    def test_retrieve_book_remark(self):
        r1 = self.book.remarks.create(content="test content")
        url = reverse(
            "book:book_remarks:remarks_single_api", kwargs={"pk": self.book.id, "book_type": "cbt", "remark_id": r1.id}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        result = res.json()["data"]["results"][0]
        self.assertEqual(result["content"], r1.content)

    def test_delete_book_remark(self):
        r1 = self.book.remarks.create(content="test content", user_id=self.book.user_id, subuser_id=1)
        url = reverse(
            "book:book_remarks:remarks_single_api", kwargs={"pk": self.book.id, "book_type": "cbt", "remark_id": r1.id}
        )
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["results"], [])

    def test_delete_book_remark_403(self):
        r1 = self.book.remarks.create(content="test content", user_id=self.book.user_id, subuser_id=2)
        url = reverse(
            "book:book_remarks:remarks_single_api", kwargs={"pk": self.book.id, "book_type": "cbt", "remark_id": r1.id}
        )
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 403)


