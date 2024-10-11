import json
import random

from django.test import TestCase
from django.urls import reverse

from epub.apps.epub_labels.models import Label, AppLabel
from epub.apps.epub_labels.serializers import AppLabelSerializers


class TestLabelList(TestCase):
    def test_expression_label(self):
        url = reverse("label_api_url:label_list_api")
        res = self.client.post(
            url,
            data={
                "title": "计算项",
                "cid": "expression",
                "value_type": "bool",
                "input_type": "expression",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["results"][0]["title"], "计算项")
        self.assertEqual(res.json()["data"]["results"][0]["cid"], "expression")
        self.assertEqual(res.json()["data"]["results"][0]["value_type"], "bool")
        self.assertEqual(res.json()["data"]["results"][0]["input_type"], "expression")
        self.assertEqual(res.json()["data"]["results"][0]["expression"], None)

        res = self.client.patch(reverse("label_api_url:label_detail_api", kwargs={"pk": res.json()["data"]["results"][0]["id"]}), data=json.dumps({"expression": "1+1"}), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["results"][0]["expression"], "1+1")

    def test_create_label(self):
        url = reverse("label_api_url:label_list_api")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json(),
            {
                "msg": "success",
                "code": 200,
                "data": {"sum": 0, "page": 1, "numpages": 1, "results": []},
            },
        )

        # res = self.client.post(url)
        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(len(res.json()), 4)

        res = self.client.post(
            url,
            data={
                "title": "标签",
                "cid": "tags",
                "value_type": "text",
                "input_type": "multiple",
            },
        )
        self.assertEqual(res.status_code, 200)
        # self.assertEqual(res.json()["data"]["results"][0]["id"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["title"], "标签")
        self.assertEqual(res.json()["data"]["results"][0]["cid"], "tags")
        self.assertEqual(res.json()["data"]["results"][0]["value_type"], "text")
        self.assertEqual(res.json()["data"]["results"][0]["input_type"], "multiple")

        self.assertEqual(res.json()["data"]["results"][0]["subuser_id"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["user_id"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["nickname"], "test1")

        self.assertEqual(res.json()["data"]["results"][0]["maximum_depth"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["enabled"], False)
        self.assertEqual(res.json()["data"]["results"][0]["linked"], False)
        self.assertEqual(res.json()["data"]["results"][0]["items"], None)
        return res.json()["data"]["results"][0]["id"]
        # self.assertEqual(len(res.json()), )

    def test_get_label_detail(self):
        label_id = self.test_create_label()
        url = reverse("label_api_url:label_detail_api", kwargs={"pk": label_id})

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        # self.assertEqual(res.json()["data"]["results"][0]["id"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["title"], "标签")
        self.assertEqual(res.json()["data"]["results"][0]["cid"], "tags")
        self.assertEqual(res.json()["data"]["results"][0]["value_type"], "text")
        self.assertEqual(res.json()["data"]["results"][0]["input_type"], "multiple")

        self.assertEqual(res.json()["data"]["results"][0]["subuser_id"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["user_id"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["nickname"], "test1")

        self.assertEqual(res.json()["data"]["results"][0]["maximum_depth"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["enabled"], False)
        self.assertEqual(res.json()["data"]["results"][0]["linked"], False)
        self.assertEqual(res.json()["data"]["results"][0]["items"], None)

    def test_patch_one_label(self):
        label_id = self.test_create_label()
        url = reverse("label_api_url:label_detail_api", kwargs={"pk": label_id})
        res = self.client.patch(
            url,
            data={
                "title": "标签2",
                "cid": "tags2",
                "value_type": "number",
                "input_type": "single",
                "user_id": 2,
                "subuser_id": 3,
                "nickname": "test2",
                "maximum_depth": 2,
                "enabled": False,
            },
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["results"][0]["title"], "标签2")
        self.assertEqual(res.json()["data"]["results"][0]["input_type"], "single")
        self.assertEqual(res.json()["data"]["results"][0]["maximum_depth"], 2)
        self.assertEqual(res.json()["data"]["results"][0]["enabled"], False)

        # cannot modify
        self.assertEqual(res.json()["data"]["results"][0]["cid"], "tags")
        self.assertEqual(res.json()["data"]["results"][0]["value_type"], "text")
        self.assertEqual(res.json()["data"]["results"][0]["subuser_id"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["user_id"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["nickname"], "test1")

    def test_change_lable_items(self):
        label_id = self.test_create_label()
        url = reverse("label_api_url:label_detail_api", kwargs={"pk": label_id})
        change_items = [
            {"value": "091", "title": "test1"},
            {"value": "090", "title": "test2"},
        ]

        res = self.client.patch(
            url, data={"items": change_items}, content_type="application/json"
        )

        self.assertEqual(res.status_code, 200)

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["results"][0]["items"], change_items)

    def test_patch_others_label(self):
        label = Label(
            title="test",
            cid="test",
            user_id=2,
            subuser_id=2,
            nickname="test",
            value_type=0,
            input_type=0,
        )
        label.save()

        url = reverse("label_api_url:label_detail_api", kwargs={"pk": label.id})
        res = self.client.patch(
            url,
            data={
                "title": "标签2",
                "cid": "tags2",
                "value_type": "number",
                "input_type": "single",
                "user_id": 2,
                "subuser_id": 3,
                "nickname": "test2",
            },
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 404)

    def test_delete(self):
        label_id = self.test_create_label()
        url = reverse("label_api_url:label_detail_api", kwargs={"pk": label_id})
        res = self.client.delete(url, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["code"], 200)

    def test_label_page(self):
        for row in range(0, 200):
            label = Label(
                cid="system{}".format(row),
                title="系统{}".format(row),
                description="test",
                value_type=row % 2,
                input_type=row % 3,
                user_id=1,
            )
            label.save()

        url = reverse("label_api_url:label_list_api")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["numpages"], 1)

    def test_create_bool_label(self):
        url = reverse("label_api_url:label_list_api")

        data = {
                "title": "布尔类型",
                "cid": "correct",
                "value_type": "bool",
                "input_type": "bool",
            "enabled": True
            }
        res = self.client.post(
            url,
            data=data,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["results"][0]["title"], data["title"])
        self.assertEqual(res.json()["data"]["results"][0]["cid"], data["cid"])
        self.assertEqual(res.json()["data"]["results"][0]["value_type"], data["value_type"])
        self.assertEqual(res.json()["data"]["results"][0]["input_type"], data["input_type"])

        self.assertEqual(res.json()["data"]["results"][0]["subuser_id"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["user_id"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["nickname"], "test1")

        self.assertEqual(res.json()["data"]["results"][0]["maximum_depth"], 1)
        self.assertEqual(res.json()["data"]["results"][0]["enabled"], data["enabled"])
        self.assertEqual(res.json()["data"]["results"][0]["linked"], False)
        self.assertEqual(res.json()["data"]["results"][0]["items"], None)


class TestAppLabel(TestCase):
    def test_create_label(self):
        url = reverse("label_api_url:label_list_api")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json(),
            {
                "msg": "success",
                "code": 200,
                "data": {"sum": 0, "page": 1, "numpages": 1, "results": []},
            },
        )

        # res = self.client.post(url)
        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(len(res.json()), 4)

        res = self.client.post(
            url,
            data={
                "title": "标签",
                "cid": "tags",
                "value_type": "text",
                "input_type": "multiple",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["results"][0]["linked"], False)
        return res.json()["data"]["results"][0]["id"]

    def test_create_label_failure(self):
        url = reverse("label_api_url:label_list_api")
        res = self.client.post(
            url,
            data={
                "title": "标签",
                "cid": "tags",
                "value_type": "list",
                "input_type": "multiple",
            },
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {"value_type": ["“list” 不是合法选项。"]})

    def test_applabel_serializer(self):
        _id = self.test_create_label()
        app_label = AppLabel(linked_app="cbt", label_id=_id)
        app_label.save()
        s = AppLabelSerializers(app_label)
        self.assertEqual(s.data.get("id"), _id)
        self.assertEqual(s.data.get("id"), _id)
        self.assertEqual(s.data.get("required"), False)
        self.assertEqual(s.data.get("show_in_list"), False)
        self.assertEqual(s.data.get("can_query"), False)

        label = Label(
            cid="system", title="系统", description="test", value_type=1, input_type=0
        )
        label.save()

        s = AppLabelSerializers(
            data={
                "id": label.id,
                "required": True,
                "show_in_list": True,
                "can_query": True,
                "type": "cbt",
            }
        )
        s.is_valid()
        app_label = s.save()
        self.assertEqual(app_label.label_id, label.id)
        self.assertEqual(app_label.required, True)
        self.assertEqual(app_label.show_in_list, True)
        self.assertEqual(app_label.can_query, True)
        self.assertEqual(app_label.linked_app, "cbt")

    def test_post_applabels_failure(self):
        data = []
        for row in range(0, 10):
            label = Label(
                cid="system{}".format(row),
                title="系统{}".format(row),
                description="test",
                value_type=row % 2,
                input_type=row % 3,
                # user_id=2
            )
            label.save()
            data.append(
                {
                    "id": label.id,
                    "required": True,
                    "show_in_list": True,
                    "can_query": True,
                }
            )

        url = reverse("label_api_url:app_label_list_api", kwargs={"type": "cbt"})
        res = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(res.status_code, 400)

        url = reverse("label_api_url:app_label_list_api", kwargs={"type": "cbt"})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["data"]["results"]), 0)

    def test_post_applabels(self):
        data = []
        for row in range(0, 10):
            label = Label(
                cid="system{}".format(row),
                title="系统{}".format(row),
                description="test",
                value_type=row % 2,
                input_type=row % 3,
                user_id=1,
            )
            label.save()
            data.append(
                {
                    "id": label.id,
                    "required": True,
                    "show_in_list": True,
                    "can_query": True,
                }
            )

        url = reverse("label_api_url:app_label_list_api", kwargs={"type": "cbt"})
        res = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["data"]["results"]), 10)

        url = reverse("label_api_url:app_label_list_api", kwargs={"type": "cbt"})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["data"]["results"]), 10)
        self.assertEqual(res.json()["data"]["results"][0]["linked"], True)

        url = reverse("label_api_url:app_label_list_api", kwargs={"type": "cbt"})
        res = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["data"]["results"]), 10)

    def test_delete_linked_lable(self):
        self.test_post_applabels()
        for row in Label.objects.filter(user_id=1):
            url = reverse("label_api_url:label_detail_api", kwargs={"pk": row.id})
            res = self.client.delete(url)
            self.assertEqual(res.status_code, 400)

    def test_filter_mappings(self):
        self.test_post_applabels()
        mappings = AppLabel.get_filter_mappings(
            linked_app="cbt", jsonfield_name="label"
        )
        self.assertEqual(
            list(mappings.keys()),
            [
                "system0",
                "system1",
                "system2",
                "system3",
                "system4",
                "system5",
                "system6",
                "system7",
                "system8",
                "system9",
            ],
        )

        # text single
        self.assertEqual(
            mappings["system0"],
            {"lookup": "label__system0__contains", "value_type": 0},
        )
        # number mulitple
        self.assertEqual(
            mappings["system1"], {"lookup": "label__system1__contains", "value_type": 1}
        )
        # text input
        self.assertEqual(
            mappings["system2"],
            {"lookup": "label__system2__icontains", "value_type": 0},
        )

        # number single
        self.assertEqual(
            mappings["system3"], {"lookup": "label__system3__contains", "value_type": 1}
        )

        # text mulitple
        self.assertEqual(
            mappings["system4"], {"lookup": "label__system4__contains", "value_type": 0}
        )

        # number input
        self.assertEqual(
            mappings["system5"], {"lookup": "label__system5", "value_type": 1}
        )
