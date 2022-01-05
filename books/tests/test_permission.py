from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book
from django.urls import reverse


User = get_user_model()


class TestPermission(TestCase):

    def test_get_book_permission(self):
        # test_user = User.objects.create_user(username="test")
        # book = Book.objects.create(title="book", user=test_user)
        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        res = self.client.post(url)
        self.assertEqual(res.status_code, 201)
