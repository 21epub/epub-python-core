from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.
from books.models import Book

User = get_user_model()


class BookTestCase(TestCase):
    def setUp(self):
        test = User.objects.create_user(username="test")
        Book.objects.create(title="yunwen", user=test)
        Book.objects.create(title="shuxue", user=test)

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
        self.assertEqual(yunwen.status, Book.STATUS.draft)
        self.assertEqual(Book.draft.all().count(), 2)
        self.assertEqual(Book.published.all().count(), 0)
        yunwen.status = Book.STATUS.published
        yunwen.save()
        self.assertEqual(yunwen.status, Book.STATUS.published)
        self.assertEqual(Book.draft.all().count(), 1)
        self.assertEqual(Book.published.all().count(), 1)
