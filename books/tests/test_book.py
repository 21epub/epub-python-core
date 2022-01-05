from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

# Create your tests here.
from books.models import Book
from books.views import JSView

User = get_user_model()


class BookTestCase(TestCase):
    def setUp(self):
        test = User.objects.create_user(username="test")
        Book.objects.create(title="yunwen", user_id=test.id)
        Book.objects.create(title="shuxue", user_id=test.id)

    def test_book_delete(self):
        """Animals that can speak are correctly identified"""
        self.assertEqual(Book.objects.all().count(), 2)
        yunwen = Book.objects.get(title="yunwen")
        yunwen.delete()
        self.assertEqual(yunwen.is_removed, True)
        self.assertEqual(Book.objects.all().count(), 1)
        self.assertEqual(Book.all_objects.all().count(), 2)

    def test_status_change(self):
        yunwen = Book.objects.get(title="yunwen")
        self.assertEqual(yunwen.is_removed, False)
        self.assertEqual(yunwen.status, Book.STATUS_CHOICES.draft)
        self.assertEqual(Book.draft.all().count(), 2)
        self.assertEqual(Book.published.all().count(), 0)
        yunwen.status = Book.STATUS_CHOICES.published
        yunwen.save()
        self.assertEqual(yunwen.status, Book.STATUS_CHOICES.published)
        self.assertEqual(Book.draft.all().count(), 1)
        self.assertEqual(Book.published.all().count(), 1)


class ViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_js_res(self):
        request = self.factory.get("/test.js")
        res = JSView.as_view()(request)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "application/javascript")
        self.assertEqual(res.rendered_content, b"var js=1;")
