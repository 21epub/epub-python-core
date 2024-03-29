import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.
from rest_framework import serializers

from books.models import Book
from django.urls import reverse
from epub.apps.epub_folders.models.folder import Folder
from epub.apps.epub_folders.serializers.folder import FolderSerializer

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

        data3 = {"title": "book_root_child2", "parent_id": f1.id}
        self.client.post(url, data3)
        res = self.client.get(url)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("title"), "book_root")
        self.assertEqual(results[0].get("user_id"), 1)
        self.assertEqual(results[0].get("subuser_id"), 1)
        self.assertEqual(results[0].get("children")[0].get("title"), data3["title"])
        self.assertEqual(results[0].get("children")[1].get("title"), data2["title"])

    def test_create_folder_with_parent_not_exists(self):
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        data = {"title": "book_root", "parent_id": 1000000}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res.json(), {"parent": [f"parent {data['parent_id']} not exists."]}
        )

    def test_bulk_create_folder(self):
        folder = Folder.objects.create(
            title="root_folder", user_id=1, subuser_id=1, folder_type="folder_type"
        )
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        data = [
            {"title": "branch_1", "parent": folder.id},
            {"title": "branch_2", "parent": folder.id},
        ]
        res = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        results = res.json()["data"]["results"]
        self.assertEqual(results[0]["position"], Folder.POSITION_STEP)
        self.assertEqual(results[0]["title"], data[0]["title"])
        self.assertEqual(results[1]["position"], Folder.POSITION_STEP * 2)
        self.assertEqual(results[1]["title"], data[1]["title"])

        max_position_with_no_parent = Folder.get_current_max_position()

        data = [{"title": "branch_3"}, {"title": "branch_4"}]
        res = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        results = res.json()["data"]["results"]
        self.assertEqual(results[0]["id"], None)
        self.assertEqual(
            results[0]["position"], max_position_with_no_parent + Folder.POSITION_STEP
        )
        self.assertEqual(results[0]["title"], data[0]["title"])
        self.assertEqual(
            results[1]["position"],
            max_position_with_no_parent + Folder.POSITION_STEP * 2,
        )
        self.assertEqual(results[1]["title"], data[1]["title"])
        self.assertEqual(results[1]["id"], None)

    @patch("epub.apps.epub_folders.serializers.folder.FolderSerializer.set_extra_attrs")
    def test_common_list_create_serializers(self, mock_set_extra_attrs):
        mock_set_extra_attrs.return_value = None
        ser = FolderSerializer(data={"title": "folder_title"})
        ser.is_valid(raise_exception=True)
        instance = ser.save()
        self.assertIsNone(instance.subuser_id)
        self.assertIsNone(instance.user_id)
        self.assertEqual(instance.title, "folder_title")
        self.assertEqual(instance.folder_type, "")
        self.assertEqual(instance.position, Folder.POSITION_STEP)

    def test_common_list_create_serializers_with_folder_type_error(self):
        ser = FolderSerializer(data={"title": "folder_title"})
        try:
            ser.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            self.assertTrue("folder_type" in e.detail)

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
        self.assertEqual(children_data[0].get("title"), "child3")
        self.assertEqual(children_data[1].get("title"), "child2")
        self.assertEqual(children_data[2].get("title"), "child1")
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
        self.assertEqual(children_data[0].get("title"), "child2")
        self.assertEqual(children_data[1].get("title"), "child3")
        self.assertEqual(children_data[2].get("title"), "child1")

        self.client.post(
            reverse("book:epub_folders:folder_sort_api", kwargs={"book_type": "h5"}),
            data={
                "target": child3.id,
                "parent": child1.id,
            },
            content_type="application/json",
        )
        child3.refresh_from_db()
        self.assertEqual(child3.parent, child1)
        self.assertEqual(child3.position, Folder.POSITION_STEP)

        self.client.post(
            reverse("book:epub_folders:folder_sort_api", kwargs={"book_type": "h5"}),
            data={
                "target": child3.id,
                "parent": "unknown",
            },
            content_type="application/json",
        )
        child3.refresh_from_db()
        self.assertEqual(child3.parent, None)
        self.assertEqual(child3.position, root.POSITION_STEP + Folder.POSITION_STEP)

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
        book1 = Book.objects.get(title="book1")
        book2 = Book.objects.get(title="book2")
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
        book4 = Book.objects.create(title="book4", user=test)
        Book.objects.create(title="book4", user=test)
        folder1 = Folder.objects.create(
            title="folder1", user_id=1, subuser_id=1, folder_type="h5"
        )
        folder2 = Folder.objects.create(
            title="folder2", user_id=1, subuser_id=1, folder_type="h5"
        )
        folder1_1 = Folder.objects.create(
            title="folder1_1", user_id=1, subuser_id=1, folder_type="h5", parent=folder1
        )
        folder1_1_1 = Folder.objects.create(
            title="folder1_1_1",
            user_id=1,
            subuser_id=1,
            folder_type="h5",
            parent=folder1_1,
        )
        book1.folder_id = folder1
        book2.folder_id = folder1
        book3.folder_id = folder2
        book4.folder_id = folder1_1_1
        book1.save()
        book2.save()
        book3.save()
        book4.save()
        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        res = self.client.get(url, data={"folder_id": folder1.id})
        self.assertEqual(res.status_code, 200)
        results = res.data.get("data").get("results")
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].get("id"), book1.id)
        self.assertEqual(results[1].get("id"), book2.id)
        self.assertEqual(results[2].get("id"), book4.id)

        res2 = self.client.get(url, data={"folder_id": [folder1.id, folder2.id, 3]})
        self.assertEqual(res2.status_code, 200)
        results2 = res2.data.get("data").get("results")
        self.assertEqual(len(results2), 4)
        self.assertEqual(results2[0].get("id"), book1.id)
        self.assertEqual(results2[1].get("id"), book2.id)
        self.assertEqual(results2[2].get("id"), book3.id)
        self.assertEqual(results2[3].get("id"), book4.id)

        url = reverse("book:book_list_api", kwargs={"book_type": "h5"})
        res3 = self.client.get(url)
        self.assertEqual(res3.status_code, 200)
        results2 = res3.data.get("data").get("results")
        self.assertEqual(len(results2), 5)

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

    def test_folder_sort_only_target(self):
        data1 = {"title": "root"}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        self.client.post(url, data1)
        f1 = Folder.objects.get(title="root")

        url = reverse("book:epub_folders:folder_sort_api", kwargs={"book_type": "h5"})

        res = self.client.post(
            url,
            data={
                "target": f1.id,
            },
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 200)
        result = res.json()["data"]["results"][0]
        self.assertEqual(result["position"], f1.position)


class TestFolderInsert(TestCase):
    def setUp(self) -> None:
        for i in range(3):
            Folder.objects.create(
                title=f"folder{i+1}",
                user_id=1,
                subuser_id=1,
                folder_type="folder_type",
                position=Folder.POSITION_STEP * (i + 1),
            )

    def test_insert_folder_with_before_position(self):
        folder2 = Folder.objects.get(title="folder2")
        folder3 = Folder.objects.get(title="folder3")

        data1 = {"title": "folder4", "before": folder2.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        res = self.client.post(url, data1)
        self.assertEqual(
            res.json()["data"]["results"][0]["position"],
            (folder2.position + folder3.position) / 2,
        )

    def test_insert_folder_to_last_with_before(self):
        folder3 = Folder.objects.get(title="folder3")

        data1 = {"title": "folder4", "before": folder3.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )

        res = self.client.post(url, data1)
        self.assertEqual(
            res.json()["data"]["results"][0]["position"],
            folder3.position + Folder.POSITION_STEP,
        )

    def test_insert_folder_to_first_with_after(self):

        folder1 = Folder.objects.get(title="folder1")

        data1 = {"title": "folder4", "after": folder1.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )
        res = self.client.post(url, data1)
        self.assertEqual(
            res.json()["data"]["results"][0]["position"], folder1.position / 2
        )

    def test_insert_folder_with_after(self):
        folder2 = Folder.objects.get(title="folder2")
        folder3 = Folder.objects.get(title="folder3")

        data1 = {"title": "folder4", "after": folder3.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )

        res = self.client.post(url, data1)
        self.assertEqual(
            res.json()["data"]["results"][0]["position"],
            (folder2.position + folder3.position) / 2,
        )

    def test_insert_reset(self):
        Folder.objects.filter(title="folder1").update(position=1)
        Folder.objects.filter(title="folder2").update(position=2)
        Folder.objects.filter(title="folder3").update(position=3)

        folder2 = Folder.objects.get(title="folder2")
        folder1 = Folder.objects.get(title="folder1")

        data1 = {"title": "folder4", "after": folder2.id}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )

        res = self.client.post(url, data1)

        folder1.refresh_from_db()
        folder2.refresh_from_db()
        self.assertEqual(
            res.json()["data"]["results"][0]["position"],
            (folder2.position + folder1.position) / 2,
        )

    def test_insert_with_before_not_exists(self):
        data1 = {"title": "folder4", "before": 1000}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )

        res = self.client.post(url, json.dumps(data1), content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {"before": ["insert before not exists."]})

    def test_insert_with_after_not_exists(self):
        data1 = {"title": "folder4", "after": 1000}
        url = reverse(
            "book:epub_folders:folder_list_create_api", kwargs={"book_type": "h5"}
        )

        res = self.client.post(url, json.dumps(data1), content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {"after": ["insert after not exists."]})
