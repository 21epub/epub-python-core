from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from books.models import Book
from epub.apps.epub_logs.models import LogEntry

User = get_user_model()


class LogTestCase(TestCase):
    def setUp(self) -> None:
        self.test = User.objects.create_user(username="test")
        Book.objects.create(title="yunwen", user_id=self.test.id)
        Book.objects.create(title="shuxue", user_id=self.test.id)

    def test_log(self):

        url = reverse("book:book_list_api", kwargs={"book_type": "cbt"})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["data"]["results"]), 2)

        url = reverse("book:book_list_api", kwargs={"book_type": "cbt"})

        title = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
        data = {"title": title, "user": self.test.id}

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, 201)

        self.assertEqual(LogEntry.objects.count(), 1)
        self.assertEqual(len(LogEntry.objects.first().object_repr), 200)
        self.assertEqual(len(title), 210)
