from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.manager import BaseManager
from django.db.models.query import QuerySet
from django.utils.translation import ugettext as _

from model_utils import Choices
from model_utils.fields import StatusField, MonitorField
from model_utils.managers import QueryManagerMixin, SoftDeletableQuerySetMixin
from model_utils.models import TimeStampedModel, _field_exists


class BasicContentQuerySet(SoftDeletableQuerySetMixin, QuerySet):
    pass


class BasicContentManager(
    QueryManagerMixin, BaseManager.from_queryset(BasicContentQuerySet)
):
    """
    初始化时支持传入过滤参数
    https://django-model-utils.readthedocs.io/en/stable/managers.html#querymanager
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_removed=False)


class BasicContentModel(TimeStampedModel):
    """
    内容基类，包含功能：
        created, modified
        status 默认：draft, published
        is_removed: 软删除标记
    注意：
        1. 子类如果需要替换objects，自定义的Manager需要继承BasicContentManager

        2. FieldTracker 不能在基类中定义，需要在子类中实现时定义：
        https://django-model-utils.readthedocs.io/en/latest/utilities.html#field-tracker
    """

    STATUS = Choices("draft", "published")

    status = StatusField(_("status"))
    status_changed = MonitorField(_("status changed"), monitor="status")
    is_removed = models.BooleanField(default=False)

    def delete(self, using=None, soft=True, *args, **kwargs):
        """
        Soft delete object (set its ``is_removed`` field to True).
        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.save(using=using)
        else:
            return super().delete(using=using, *args, **kwargs)

    objects = BasicContentManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        """
        Overriding the save method in order to make sure that
        status_changed field is updated even if it is not given as
        a parameter to the update field argument.
        """
        update_fields = kwargs.get("update_fields", None)
        if update_fields and "status" in update_fields:
            kwargs["update_fields"] = set(update_fields).union({"status_changed"})

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


def add_status_query_managers(sender, **kwargs):
    """
    Add a Querymanager for each status item dynamically.

    """
    if not issubclass(sender, BasicContentModel):
        return

    default_manager = sender._meta.default_manager

    for value, display in getattr(sender, "STATUS", ()):
        if _field_exists(sender, value):
            raise ImproperlyConfigured(
                "StatusModel: Model '%s' has a field named '%s' which "
                "conflicts with a status of the same name." % (sender.__name__, value)
            )
        sender.add_to_class(value, BasicContentManager(status=value))

    sender._meta.default_manager_name = default_manager.name


models.signals.class_prepared.connect(add_status_query_managers)
