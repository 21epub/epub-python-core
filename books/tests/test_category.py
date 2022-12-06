from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.
from rest_framework import serializers

from books.models import Book
from django.urls import reverse
from epub.apps.epub_categories.models.category import Category
from epub.apps.epub_categories.serializers.category import CategorySerializer

User = get_user_model()


class TestBookCategory(TestCase):
    def test_create_book_categories(self):
        data1 = {"title": "book_root"}
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, data1)
        c1 = Category.objects.filter(title="book_root").first()
        data2 = {"title": "book_root_child1", "parent": c1.id}
        self.client.post(url, data2)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("title"), "book_root")
        self.assertEqual(results[0].get("user_id"), 1)
        self.assertEqual(results[0].get("subuser_id"), 1)
        self.assertEqual(results[0].get("children")[0].get("title"), "book_root_child1")

    @patch("epub.apps.epub_categories.serializers.category.CategorySerializer.set_extra_attrs")
    def test_common_list_create_serializers(self, mock_set_extra_attrs):
        mock_set_extra_attrs.return_value = None
        ser = CategorySerializer(data={"title": "category_title"})
        ser.is_valid(raise_exception=True)
        instance = ser.save()
        self.assertIsNone(instance.subuser_id)
        self.assertIsNone(instance.user_id)
        self.assertEqual(instance.title, "category_title")
        self.assertEqual(instance.category_type, "")
        self.assertEqual(instance.position, Category.POSITION_STEP)

    def test_common_list_create_serializers_with_category_type_error(self):
        ser = CategorySerializer(data={"title": "category_title"})
        try:
            ser.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            self.assertTrue("category_type" in e.detail)

    def test_list_book_categories(self):
        root_category = Category.objects.create(
            title="root", user_id=1, subuser_id=1, category_type="h5"
        )
        Category.objects.create(
            title="root2", user_id=1, subuser_id=1, category_type="h5"
        )
        Category.objects.create(
            title="user_category", user_id=1, subuser_id=1, category_type="user"
        )
        Category.objects.create(
            parent=root_category,
            title="child1",
            user_id=1,
            subuser_id=1,
            category_type="h5",
        )
        Category.objects.create(
            parent=root_category,
            title="child2",
            user_id=1,
            subuser_id=1,
            category_type="h5",
        )
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0].get("children")), 2)

    def test_filter_book_category(self):
        Category.objects.create(
            title="h5_root1", user_id=1, subuser_id=1, category_type="h5"
        )
        Category.objects.create(
            title="h5_root2", user_id=1, subuser_id=1, category_type="h5"
        )
        Category.objects.create(
            title="h5_root3", user_id=1, subuser_id=2, category_type="h5"
        )
        Category.objects.create(
            title="h5_root4", user_id=2, subuser_id=1, category_type="h5"
        )
        Category.objects.create(
            title="user_root5", user_id=1, subuser_id=1, category_type="user"
        )
        Category.objects.create(
            title="user_root6", user_id=1, subuser_id=1, category_type="user"
        )
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 2)
        for data in results:
            self.assertEqual(data.get("user_id"), 1)
            self.assertEqual(data.get("subuser_id"), 1)
            self.assertEqual(data.get("category_type"), "h5")

    def test_retrieve_category(self):
        c1 = Category.objects.create(
            title="root1", user_id=1, subuser_id=1, category_type="h5"
        )
        url = reverse(
            "book:epub_categories:category_retrieve_update_destroy_api",
            kwargs={"book_type": "h5", "pk": c1.id},
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("title"), "root1")

    def test_update_category(self):
        c1 = Category.objects.create(
            title="root1", user_id=1, subuser_id=1, category_type="h5"
        )
        url = reverse(
            "book:epub_categories:category_retrieve_update_destroy_api",
            kwargs={"book_type": "h5", "pk": c1.id},
        )
        res = self.client.put(
            url, data={"title": "root_update"}, content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("title"), "root_update")

    def test_delete_category(self):
        c1 = Category.objects.create(
            title="root1", user_id=1, subuser_id=1, category_type="h5"
        )
        url = reverse(
            "book:epub_categories:category_retrieve_update_destroy_api",
            kwargs={"book_type": "h5", "pk": c1.id},
        )
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Category.objects.count(), 0)

    def test_sort_category(self):
        data1 = {"title": "root"}
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, data1)
        c1 = Category.objects.get(title="root")
        child_data1 = {"title": "child1", "parent": c1.id}
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data1)
        child_data2 = {"title": "child2", "parent": c1.id}
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data2)
        child_data3 = {"title": "child3", "parent": c1.id}
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data3)
        # 此时顺序为child1, child2, child3
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        children_data = results[0].get("children")
        self.assertEqual(children_data[0].get("title"), "child3")
        self.assertEqual(children_data[1].get("title"), "child2")
        self.assertEqual(children_data[2].get("title"), "child1")
        root = Category.objects.get(title="root")
        child1 = Category.objects.get(title="child1")
        child2 = Category.objects.get(title="child2")
        child3 = Category.objects.get(title="child3")
        # 执行排序操作  将child3放置child1 child2 之间
        url = reverse(
            "book:epub_categories:category_sort_api", kwargs={"book_type": "h5"}
        )
        self.client.post(
            url,
            data={
                "target": child3.id,
                "before": child1.id,
                "after": child2.id,
                "parent": root.id,
            },
            content_type="application/json",
        )
        # 此时顺序为child1, child3, child2
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        children_data = results[0].get("children")
        self.assertEqual(children_data[0].get("title"), "child2")
        self.assertEqual(children_data[1].get("title"), "child3")
        self.assertEqual(children_data[2].get("title"), "child1")

    def test_batch_category(self):
        test_user = User.objects.create_user(username="test")
        book1 = Book.objects.create(title="book1", user=test_user)
        book2 = Book.objects.create(title="book2", user=test_user)
        category1 = Category.objects.create(
            title="category1", user_id=1, subuser_id=1, category_type="h5"
        )
        category2 = Category.objects.create(
            title="category2", user_id=1, subuser_id=1, category_type="h5"
        )
        category3 = Category.objects.create(
            title="category3", user_id=1, subuser_id=1, category_type="h5"
        )
        content_ids = [book1.id, book2.id]
        category_ids = [category1.id, category2.id, category3.id]
        url = reverse(
            "book:epub_categories:category_batch_api", kwargs={"book_type": "h5"}
        )
        self.client.post(
            url,
            data={"content_ids": content_ids, "category_ids": category_ids},
            content_type="application/json",
        )
        book1_category_ids = sorted(
            list(book1.categories.all().values_list("id", flat=True))
        )
        book2_category_ids = sorted(
            list(book2.categories.all().values_list("id", flat=True))
        )
        self.assertEqual(category_ids, book1_category_ids)
        self.assertEqual(category_ids, book2_category_ids)

    def test_filter_book_by_category(self):
        test = User.objects.create_user(username="test")
        book1 = Book.objects.create(title="book1", user=test)
        book2 = Book.objects.create(title="book2", user=test)
        book3 = Book.objects.create(title="book3", user=test)
        Book.objects.create(title="book4", user=test)
        category1 = Category.objects.create(
            title="category1", user_id=1, subuser_id=1, category_type="h5"
        )
        category2 = Category.objects.create(
            title="category2", user_id=1, subuser_id=1, category_type="h5"
        )
        book1.categories.add(category1)
        book2.categories.add(*[category1, category2])
        book3.categories.add(category2)
        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        res = self.client.get(url, data={"category_id": category1.id})
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].get("id"), book1.id)
        self.assertEqual(results[1].get("id"), book2.id)

        res2 = self.client.get(url, data={"category_id": [category1.id, category2.id]})
        self.assertEqual(res2.status_code, 200)
        results2 = res2.data.get("data").get("results")
        self.assertEqual(len(results2), 3)
        self.assertEqual(results2[0].get("id"), book1.id)
        self.assertEqual(results2[1].get("id"), book2.id)
        self.assertEqual(results2[2].get("id"), book3.id)

        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        res3 = self.client.get(url)
        self.assertEqual(res3.status_code, 200)
        results2 = res3.data.get("data").get("results")
        self.assertEqual(len(results2), 4)

    def test_sort_reset_category(self):
        data1 = {"title": "root"}
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, data1)
        c1 = Category.objects.get(title="root")
        # 创建3条记录
        child_data1 = {"title": "child1", "parent": c1.id}
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data1)
        child_data2 = {"title": "child2", "parent": c1.id}
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data2)
        child_data3 = {"title": "child3", "parent": c1.id}
        url = reverse(
            "book:epub_categories:category_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data3)
        root = Category.objects.get(title="root")
        child1 = Category.objects.get(title="child1")
        child2 = Category.objects.get(title="child2")
        child3 = Category.objects.get(title="child3")
        # 将child3移动到child1与child2之间
        child1.position = 1
        child1.save()
        child2.position = 2
        child2.save()
        # 执行排序操作  将child3放置child1 child2 之间
        url = reverse(
            "book:epub_categories:category_sort_api", kwargs={"book_type": "h5"}
        )
        self.client.post(
            url,
            data={
                "target": child3.id,
                "before": child1.id,
                "after": child2.id,
                "parent": root.id,
            },
            content_type="application/json",
        )
        child1_update = Category.objects.get(title="child1")
        child2_update = Category.objects.get(title="child2")
        child3_update = Category.objects.get(title="child3")
        self.assertEqual(child1_update.position, Category.POSITION_STEP)
        self.assertEqual(
            child2_update.position, child1_update.position + Category.POSITION_STEP
        )
        self.assertEqual(
            child3_update.position,
            (child1_update.position + child2_update.position) / 2,
        )
