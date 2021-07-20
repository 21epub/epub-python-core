from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.
from books.models import Book
from django.urls import reverse
from epub.apps.epub_folders.models.folder import Folder

User = get_user_model()


class TestBookFolder(TestCase):
    def test_create_book_folders(self):
        data1 = {"title": "book_root"}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, data1)
        f1 = Folder.objects.filter(title="book_root").first()
        data2 = {"title": "book_root_child1", "parent": f1.id}
        self.client.post(url, data2)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("title"), "book_root")
        self.assertEqual(results[0].get("user_id"), 1)
        self.assertEqual(results[0].get("subuser_id"), 1)
        self.assertEqual(results[0].get("children")[0].get("title"), "book_root_child1")

    def test_list_book_folders(self):
        root_folder = Folder.objects.create(
            title="root", user_id=1, subuser_id=1, folder_type="h5"
        )
        Folder.objects.create(title="root2", user_id=1, subuser_id=1, folder_type="h5")
        Folder.objects.create(
            title="user_folder", user_id=1, subuser_id=1, folder_type="user"
        )
        Folder.objects.create(
            parent=root_folder,
            title="child1",
            user_id=1,
            subuser_id=1,
            folder_type="h5",
        )
        Folder.objects.create(
            parent=root_folder,
            title="child2",
            user_id=1,
            subuser_id=1,
            folder_type="h5",
        )
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0].get("children")), 2)

    def test_filter_book_folder(self):
        Folder.objects.create(
            title="h5_root1", user_id=1, subuser_id=1, folder_type="h5"
        )
        Folder.objects.create(
            title="h5_root2", user_id=1, subuser_id=1, folder_type="h5"
        )
        Folder.objects.create(
            title="h5_root3", user_id=1, subuser_id=2, folder_type="h5"
        )
        Folder.objects.create(
            title="h5_root4", user_id=2, subuser_id=1, folder_type="h5"
        )
        Folder.objects.create(
            title="user_root5", user_id=1, subuser_id=1, folder_type="user"
        )
        Folder.objects.create(
            title="user_root6", user_id=1, subuser_id=1, folder_type="user"
        )
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 2)
        for data in results:
            self.assertEqual(data.get("user_id"), 1)
            self.assertEqual(data.get("subuser_id"), 1)
            self.assertEqual(data.get("folder_type"), "h5")

    def test_retrieve_folder(self):
        f1 = Folder.objects.create(
            title="root1", user_id=1, subuser_id=1, folder_type="h5"
        )
        url = reverse(
            "book:epub_folders:folder_retrieve_update_destroy_api",
            kwargs={"book_type": "h5", "pk": f1.id},
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("title"), "root1")

    def test_update_folder(self):
        f1 = Folder.objects.create(
            title="root1", user_id=1, subuser_id=1, folder_type="h5"
        )
        url = reverse(
            "book:epub_folders:folder_retrieve_update_destroy_api",
            kwargs={"book_type": "h5", "pk": f1.id},
        )
        res = self.client.put(
            url, data={"title": "root_update"}, content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("title"), "root_update")

    def test_delete_folder(self):
        f1 = Folder.objects.create(
            title="root1", user_id=1, subuser_id=1, folder_type="h5"
        )
        url = reverse(
            "book:epub_folders:folder_retrieve_update_destroy_api",
            kwargs={"book_type": "h5", "pk": f1.id},
        )
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Folder.objects.count(), 0)

    def test_sort_folder(self):
        data1 = {"title": "root"}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, data1)
        f1 = Folder.objects.get(title="root")
        child_data1 = {"title": "child1", "parent": f1.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data1)
        child_data2 = {"title": "child2", "parent": f1.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data2)
        child_data3 = {"title": "child3", "parent": f1.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data3)
        # 此时顺序为child1, child2, child3
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        children_data = results[0].get("children")
        self.assertEqual(children_data[0].get("title"), "child1")
        self.assertEqual(children_data[1].get("title"), "child2")
        self.assertEqual(children_data[2].get("title"), "child3")
        root = Folder.objects.get(title="root")
        child1 = Folder.objects.get(title="child1")
        child2 = Folder.objects.get(title="child2")
        child3 = Folder.objects.get(title="child3")
        # 执行排序操作  将child3放置child1 child2 之间
        url = reverse("book:epub_folders:folder_sort_api", kwargs={"book_type": "h5"})
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
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        children_data = results[0].get("children")
        self.assertEqual(children_data[0].get("title"), "child1")
        self.assertEqual(children_data[1].get("title"), "child3")
        self.assertEqual(children_data[2].get("title"), "child2")

    def test_batch_folder(self):
        test_user = User.objects.create_user(username="test")
        book1 = Book.objects.create(title="book1", user=test_user)
        book2 = Book.objects.create(title="book2", user=test_user)
        folder1 = Folder.objects.create(
            title="folder1", user_id=1, subuser_id=1, folder_type="h5"
        )
        content_ids = [book1.id, book2.id, 3]
        folder_id = folder1.id
        url = reverse("book:epub_folders:folder_batch_api", kwargs={"book_type": "h5"})
        self.client.post(
            url,
            data={"content_ids": content_ids, "folder_id": folder_id},
            content_type="application/json",
        )
        book1 = Book.objects.get(title="book1", user=test_user)
        book2 = Book.objects.get(title="book2", user=test_user)
        self.assertEqual(book1.folder_id, folder_id)
        self.assertEqual(book2.folder_id, folder_id)

    def test_batch_folder_exception(self):
        test_user = User.objects.create_user(username="test")
        book1 = Book.objects.create(title="book1", user=test_user)
        book2 = Book.objects.create(title="book2", user=test_user)
        folder1 = Folder.objects.create(
            title="folder1", user_id=1, subuser_id=1, folder_type="h5"
        )
        content_ids = [book1.id, book2.id]
        folder_id = folder1.id
        # 检测app或者model不存在的情况
        url = reverse(
            "book:epub_folders_test:folder_batch_api", kwargs={"book_type": "h5"}
        )
        res = self.client.post(
            url,
            data={"content_ids": content_ids, "folder_id": folder_id},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

        # 检测folder_id不存在的情况
        url = reverse("book:epub_folders:folder_batch_api", kwargs={"book_type": "h5"})
        res = self.client.post(
            url,
            data={"content_ids": content_ids, "folder_id": 100},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_filter_book_by_folder(self):
        test = User.objects.create_user(username="test")
        book1 = Book.objects.create(title="book1", user=test)
        book2 = Book.objects.create(title="book2", user=test)
        book3 = Book.objects.create(title="book3", user=test)
        Book.objects.create(title="book4", user=test)
        folder1 = Folder.objects.create(
            title="folder1", user_id=1, subuser_id=1, folder_type="h5"
        )
        folder2 = Folder.objects.create(
            title="folder2", user_id=1, subuser_id=1, folder_type="h5"
        )
        book1.folder_id = folder1
        book2.folder_id = folder1
        book3.folder_id = folder2
        book1.save()
        book2.save()
        book3.save()
        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        res = self.client.get(url, data={"folder_id": folder1.id})
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].get("id"), book1.id)
        self.assertEqual(results[1].get("id"), book2.id)

        res2 = self.client.get(url, data={"folder_id": [folder1.id, folder2.id, 3]})
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

    def test_sort_reset_folder(self):
        data1 = {"title": "root"}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, data1)
        f1 = Folder.objects.get(title="root")
        # 创建3条记录
        child_data1 = {"title": "child1", "parent": f1.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data1)
        child_data2 = {"title": "child2", "parent": f1.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data2)
        child_data3 = {"title": "child3", "parent": f1.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, child_data3)
        root = Folder.objects.get(title="root")
        child1 = Folder.objects.get(title="child1")
        child2 = Folder.objects.get(title="child2")
        child3 = Folder.objects.get(title="child3")
        # 将child3移动到child1与child2之间
        child1.position = 1
        child1.save()
        child2.position = 2
        child2.save()
        # 执行排序操作  将child3放置child1 child2 之间
        url = reverse("book:epub_folders:folder_sort_api", kwargs={"book_type": "h5"})
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
        child1_update = Folder.objects.get(title="child1")
        child2_update = Folder.objects.get(title="child2")
        child3_update = Folder.objects.get(title="child3")
        self.assertEqual(child1_update.position, Folder.POSITION_STEP)
        self.assertEqual(
            child2_update.position, child1_update.position + Folder.POSITION_STEP
        )
        self.assertEqual(
            child3_update.position,
            (child1_update.position + child2_update.position) / 2,
        )
