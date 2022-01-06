from unittest.mock import patch

from django.test import TestCase

from books.authentication import User
from books.models import Book
from django.urls import reverse


class TestPermission(TestCase):

    default_perms = []
    add_perms = []

    is_superuser = False
    user_id = 1
    subuser_id = 1

    def get_mock_user(self):
        return User(
            id=self.user_id,
            username="test_permission_user",
            subuser={
                "id": self.subuser_id,
                "perms": self.default_perms + self.add_perms,
                "is_superuser": self.is_superuser,
            },
        )

    @patch("books.authentication.MockUserAuthentication.authenticate")
    def test_book_create_permission(self, mock_authenticate_user):
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        self.assertEqual(Book.objects.count(), 0)
        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        res = self.client.post(url)
        self.assertEqual(res.status_code, 403)

        self.add_perms.append({"code": "h5.create"})
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        res = self.client.post(url)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Book.objects.count(), 1)

    @patch("books.authentication.MockUserAuthentication.authenticate")
    def test_book_list_permission(self, mock_authenticate_user):
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)

        self.add_perms.append({"code": "h5.list"})
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
