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

    @patch("books.authentication.MockUserAuthentication.authenticate")
    def test_book_detail_permission(self, mock_authenticate_user):
        book = Book.objects.create(title="test", user_id=self.user_id, subuser_id=self.subuser_id)
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        url = reverse("book:book_single_api", kwargs={"book_type": "h5", "pk": book.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)

        self.add_perms.append({"code": "h5.detail"})
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        result = res.json()
        self.assertEqual(result["title"], book.title)
        self.assertEqual(result["user_id"], book.user_id)
        self.assertEqual(result["subuser_id"], book.subuser_id)

        book.subuser_id = 2
        book.save()
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)

        self.add_perms.append({"code": "h5.detail.show_all_user_contents"})
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @patch("books.authentication.MockUserAuthentication.authenticate")
    def test_book_update_permission(self, mock_authenticate_user):
        book = Book.objects.create(title="test", user_id=self.user_id, subuser_id=self.subuser_id)
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        data = {
            "title": "new_title"
        }

        url = reverse("book:book_single_api", kwargs={"book_type": "h5", "pk": book.id})
        res = self.client.patch(url, data=data, content_type="application/json")
        self.assertEqual(res.status_code, 403)

        self.add_perms.append({"code": "h5.update"})
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        res = self.client.patch(url, data=data, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        result = res.json()
        self.assertEqual(result["title"], "new_title")

        book.subuser_id = 2
        book.save()

        res = self.client.patch(url, data=data, content_type="application/json")
        self.assertEqual(res.status_code, 403)

        self.add_perms.append({"code": "h5.update.show_all_user_contents"})
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        res = self.client.patch(url, data=data, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        result = res.json()
        self.assertEqual(result["title"], "new_title")

