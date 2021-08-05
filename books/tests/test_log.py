from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from books.models import Book
from epub.apps.epub_logs.models import LogEntry

User = get_user_model()


class LogTestCase(TestCase):
    def setUp(self) -> None:
        self.test = User.objects.create_user(username="test")
        Book.objects.create(title="yunwen", user=self.test)
        Book.objects.create(title="shuxue", user=self.test)

    def test_log(self):

        url = reverse("book:book_list_api", kwargs={"book_type": "cbt"})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["data"]["results"]), 2)

        url = reverse("book:book_list_api", kwargs={"book_type": "cbt"})

        data = {"title": "title", "user": self.test.id}

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, 201)

        self.assertEqual(LogEntry.objects.count(), 1)
