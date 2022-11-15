import json

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from books.models import Book
from epub.apps.epub_folders.models import Folder
from epub.apps.epub_logs.models import LogEntry

User = get_user_model()


class LogTestCase(TestCase):
    def setUp(self) -> None:
        self.test = User.objects.create_user(username="test")
        self.book_yuwen = Book.objects.create(title="yuwen", user=self.test)
        self.book_shuxue = Book.objects.create(title="shuxue", user=self.test)
        self.folder = Folder.objects.create(title="folder")

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

    def test_batch_set_book_folder(self):
        url = reverse("book:book_list_api", kwargs={"book_type": "cbt"})
        data = [
            {"title": self.book_yuwen.title, "folder": self.folder.id},
            {"title": self.book_shuxue.title, "folder": self.folder.id}
        ]

        res = self.client.patch(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        results = res.json()
        self.assertEqual(results[0]["folder"], self.folder.id)
        self.assertEqual(results[1]["folder"], self.folder.id)

    def test_batch_create_book(self):
        url = reverse("book:book_list_api", kwargs={"book_type": "cbt"})
        data = [
            {"title": "title1", "user": self.test.id},
            {"title": "title2", "user": self.test.id},
        ]

        res = self.client.post(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(res.json()), 2)
        self.assertEqual(res.json()[0]["title"], data[0]["title"])
        self.assertEqual(res.json()[1]["title"], data[1]["title"])

