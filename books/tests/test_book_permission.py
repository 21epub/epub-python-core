import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse

from books.authentication import User as MockUser
from books.models import Book

User = get_user_model()


class TestBookPermission(TestCase):
    subuser_id = 1
    nickname = "subuser1"
    perms = []
    is_superuser = False
    dept_id = 1

    def setUp(self):
        self.user = User.objects.create_user(username="test")

        self.subuser1_dept_1_book = Book.objects.create(title="subuser1_dept_1_book", user=self.user, subuser_id=1,
                                                        dept_id=1)
        self.subuser2_dept_1_book = Book.objects.create(title="subuser2_dept_1_book", user=self.user, subuser_id=2,
                                                        dept_id=1)
        self.subuser3_dept_2_book = Book.objects.create(title="subuser3_dept_2_book", user=self.user, subuser_id=3,
                                                        dept_id=2)

    def get_mock_user(self):
        return MockUser(
            id=self.user.id,
            username="test_permission_user",
            subuser={
                "id": self.subuser_id,
                "nickname": self.nickname,
                "perms": self.perms,
                "is_superuser": self.is_superuser,
                "dept_id": self.dept_id,
            },
        )

    @patch("books.authentication.MockUserAuthentication.authenticate")
    def test_get_book_list(self, mock_authenticate_user):
        self.perms = [{"code": "h5.list", "deps": [1]}]
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]["results"]), 2)

    @patch("books.authentication.MockUserAuthentication.authenticate")
    def test_get_all_book_list(self, mock_authenticate_user):
        self.perms = [{"code": "h5.list", "show_all": True, "deps": []}]
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]["results"]), 3)

    @patch("books.authentication.MockUserAuthentication.authenticate")
    def test_get_self_book_list(self, mock_authenticate_user):
        self.perms = [{"code": "h5.list", "only_self": True, "deps": []}]
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]["results"]), 1)

    @patch("books.authentication.MockUserAuthentication.authenticate")
    def test_edit_book(self, mock_authenticate_user):
        self.perms = [{"code": "h5.update", "deps": [1]}]
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")
        url = reverse("book:book_single_api", kwargs={"book_type": "h5", "pk": self.subuser1_dept_1_book.pk})
        data = {
            "title": "update_title",
        }
        response = self.client.patch(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["results"][0]["title"], "update_title")

    def test_edit_other_dept_book_403(self):
        url = reverse("book:book_single_api", kwargs={"book_type": "h5", "pk": self.subuser3_dept_2_book.pk})
        data = {
            "title": "update_title",
        }
        response = self.client.patch(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 403)

    @patch("books.authentication.MockUserAuthentication.authenticate")
    def test_edit_other_dept_book(self, mock_authenticate_user):
        self.perms = [{"code": "h5.update", "show_all": True, "deps": []}]
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        url = reverse("book:book_single_api", kwargs={"book_type": "h5", "pk": self.subuser3_dept_2_book.pk})
        data = {
            "title": "update_title",
        }
        response = self.client.patch(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["results"][0]["title"], "update_title")

    @patch("books.authentication.MockUserAuthentication.authenticate")
    def test_edit_only_self_book(self, mock_authenticate_user):
        self.perms = [{"code": "h5.update", "only_self": True, "deps": [1]}]
        mock_authenticate_user.return_value = (self.get_mock_user(), "token_xxxx")

        url = reverse("book:book_single_api", kwargs={"book_type": "h5", "pk": self.subuser2_dept_1_book.pk})
        data = {
            "title": "update_title",
        }
        response = self.client.patch(url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 403)
