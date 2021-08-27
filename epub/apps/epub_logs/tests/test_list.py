from django.test import TestCase
from django.urls import reverse

from epub.apps.epub_logs.models import LogEntry


class LogTestCase(TestCase):
    def setUp(self) -> None:
        LogEntry(
            user_id=1,
            subuser_id=1,
            nickname="test1",
            object_type="h5",
            object_id=1,
            object_repr="test_h5_title",
            action_ip="127.0.0.1",
            action_type=LogEntry.ADDITION,
            action_name="新增",
            action_level=LogEntry.INFO,
            change_message="",
        ).save()

        LogEntry(
            user_id=1,
            subuser_id=1,
            nickname="test1",
            object_type="h5",
            object_id=1,
            object_repr="test_h5_title",
            action_ip="127.0.0.1",
            action_type=LogEntry.EDIT,
            action_name="编辑",
            action_level=LogEntry.DEBUG,
            change_message="添加图片",
        ).save()

        LogEntry(
            user_id=1,
            subuser_id=1,
            nickname="test1",
            object_type="h5",
            object_id=1,
            object_repr="test_h5_title",
            action_ip="127.0.0.1",
            action_type=LogEntry.EDIT,
            action_name="编辑",
            action_level=LogEntry.DEBUG,
            change_message="添加文字",
        ).save()

        LogEntry(
            user_id=1,
            subuser_id=1,
            nickname="test1",
            object_type="h5",
            object_id=2,
            object_repr="test_h5_title2",
            action_ip="127.0.0.1",
            action_type=LogEntry.ADDITION,
            action_name="新增",
            action_level=LogEntry.INFO,
            change_message="",
        ).save()

        LogEntry(
            user_id=1,
            subuser_id=2,
            nickname="test2",
            object_type="h5",
            object_id=3,
            object_repr="test_h5_title3",
            action_ip="127.0.0.1",
            action_type=LogEntry.ADDITION,
            action_name="新增",
            action_level=LogEntry.INFO,
            change_message="",
        ).save()

        LogEntry(
            user_id=1,
            subuser_id=2,
            nickname="test2",
            object_type="cbt",
            object_id=4,
            object_repr="test_cbt_title4",
            action_ip="127.0.0.1",
            action_type=LogEntry.ADDITION,
            action_name="新增",
            action_level=LogEntry.INFO,
            change_message="",
        ).save()

    def test_all_view(self):
        url = reverse("log_api_url:log-admin-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.json()["data"]["results"]
        self.assertEqual(len(results), 4)
        one_log = results[0]
        self.assertIn("action_ip", one_log)
        self.assertIn("action_name", one_log)
        self.assertIn("nickname", one_log)
        self.assertIn("object_repr", one_log)
        self.assertIn("change_message", one_log)
        self.assertIn("action_time", one_log)

    def test_object_filter(self):
        url = reverse("log_api_url:log-admin-list")
        res = self.client.get(url, data={"subuser_id": 1})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["sum"], 2)

        url = reverse("log_api_url:log-admin-list")
        res = self.client.get(url, data={"end_time": "2020-01-01"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["sum"], 0)

        url = reverse("log_api_url:log-admin-list")
        res = self.client.get(url, data={"object_type": "h5"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["sum"], 3)

        url = reverse("log_api_url:log-admin-list")
        res = self.client.get(url, data={"object_type": "cbt"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["sum"], 1)

    def test_object_log(self):
        url = reverse(
            "log_api_url:log-object-list", kwargs={"object_type": "h5", "pk": 1}
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        results = res.json()["data"]["results"]
        self.assertEqual(len(results), 1)
