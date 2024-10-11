import datetime
import random

from django.db import models
from django.db.models import RestrictedError
from django.utils.translation import ugettext as _

from epub.core.models import BasicContentModel
from model_utils import Choices


def gen_serial_number():
    now = datetime.datetime.now().strftime("%Y%m%d")
    random_int = random.randint(1000, 9999)
    return int("%s%s" % (now, random_int))


class LabelMixin(models.Model):

    label = models.JSONField(null=True)

    class Meta:
        abstract = True


class LabelBase(BasicContentModel):
    VALUE_TYPE_CHOICES = Choices(
        (0, "text", _("text")), (1, "number", _("number")), (3, "bool", _("bool"))
    )
    INPUT_TYPE_CHOICES = Choices(
        (0, "single", _("single")),
        (1, "multiple", _("multiple")),
        (2, "input", _("input")),
        (3, "bool", _("bool")),
        (5, "expression", _("expression")),
    )

    user_id = models.IntegerField(default=None, null=True)
    subuser_id = models.IntegerField(default=None, null=True)
    nickname = models.CharField(max_length=150, null=True, default="")

    cid = models.CharField(max_length=63)
    serial_number = models.BigIntegerField(editable=False, default=gen_serial_number)
    title = models.CharField(max_length=63)
    description = models.CharField(max_length=511, default="", null=True, blank=True)
    value_type = models.IntegerField(choices=VALUE_TYPE_CHOICES)
    input_type = models.IntegerField(choices=INPUT_TYPE_CHOICES)
    maximum_depth = models.IntegerField(default=1)  # 最大层级
    enabled = models.BooleanField(default=True)
    allow_check_parent = models.BooleanField(default=False, null=True)  # 父节点可选
    allow_add_items = models.BooleanField(default=False, null=True)  # 可自由添加标签项
    items = models.JSONField(blank=True, null=True)
    expression = models.TextField(null=True, blank=True, help_text="计算项表达式")

    class Meta:
        abstract = True

    @property
    def filter_lookup(self):
        if self.input_type in [
            self.INPUT_TYPE_CHOICES.single,
            self.INPUT_TYPE_CHOICES.multiple,
        ]:
            # list search
            return "{}__contains".format(self.cid)

        elif self.value_type == self.VALUE_TYPE_CHOICES.text:
            # input text
            return "{}__icontains".format(self.cid)
        else:
            # input number or bool
            return self.cid


class Label(LabelBase):
    pass

    @property
    def linked(self):
        if self.labels.count() > 0:
            return True
        else:
            return False

    def delete(self, *args, **kwargs):
        if self.linked:
            raise RestrictedError("linked", self.labels)
        else:
            super().delete(*args, **kwargs)

    class Meta:
        ordering = ["created"]


class AppLabel(models.Model):

    user_id = models.IntegerField(default=None, null=True)
    subuser_id = models.IntegerField(default=None, null=True)
    nickname = models.CharField(max_length=150, null=True, default="")

    label = models.ForeignKey(Label, related_name="labels", on_delete=models.CASCADE)
    required = models.BooleanField(default=False)
    show_in_list = models.BooleanField(default=False)
    can_query = models.BooleanField(default=False)
    linked_app = models.CharField(max_length=32, db_index=True)

    @classmethod
    def get_filter_mappings(
        cls, linked_app: str, jsonfield_name=None, label_using_db="default"
    ) -> dict:
        mapppings = {}
        applabels = (
            cls.objects.using(label_using_db)
            .prefetch_related("label")
            .filter(linked_app=linked_app)
        )
        for row in applabels:
            if jsonfield_name:
                mapppings[row.label.cid] = {
                    "lookup": "{}__{}".format(jsonfield_name, row.label.filter_lookup),
                    "value_type": row.label.value_type,
                }
            else:
                mapppings[row.label.cid] = {
                    "lookup": row.label.filter_lookup,
                    "value_type": row.label.value_type,
                }

        return mapppings

    class Meta:
        unique_together = ["label", "linked_app"]
