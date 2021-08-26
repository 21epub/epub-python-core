from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.manager import BaseManager
from django.db.models.query import QuerySet
from django.utils.translation import ugettext as _

from model_utils import Choices
from model_utils.fields import MonitorField
from model_utils.managers import SoftDeletableQuerySetMixin, QueryManager
from model_utils.models import TimeStampedModel, _field_exists
from mptt.models import MPTTModel, TreeForeignKey


class BasicContentQuerySet(SoftDeletableQuerySetMixin, QuerySet):
    pass


class BasicContentManager(
    QueryManager, BaseManager.from_queryset(BasicContentQuerySet)
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
        status 默认：0 draft, 1 published
        is_removed: 软删除标记
    Demo1: find list
       draft_books = Book.draft.all()
       published_books = Book.published.all()
       not_deleted_books = Book.objects.all()
       all_books = Book.all_objects.all()
    Demo2: status change
       book.status = Book.STATUS_CHOICES.draft
       book.status = Book.STATUS_CHOICES.published
    Demo3: status_display
        status_display = Article.STATUS_CHOICES[article.status]
    注意：
        1. 子类如果需要替换objects，自定义的Manager需要继承BasicContentManager
        2. track=FieldTracker 不能在基类中定义，需要在子类中实现时定义：
        https://django-model-utils.readthedocs.io/en/latest/utilities.html#field-tracker
    """

    STATUS_CHOICES = Choices((0, "draft", _("草稿")), (1, "published", _("已发布")))

    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_CHOICES.draft)
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
    _status = getattr(sender, "STATUS_CHOICES")
    if _status:
        for value, key, display in _status._triples:
            if _field_exists(sender, key):
                raise ImproperlyConfigured(
                    "StatusModel: Model '%s' has a field named '%s' which "
                    "conflicts with a status of the same name." % (sender.__name__, key)
                )
            sender.add_to_class(key, BasicContentManager(status=value))

    sender._meta.default_manager_name = default_manager.name


models.signals.class_prepared.connect(add_status_query_managers)


class BaseCommonModel(MPTTModel):
    """
    此公共模型用于封装Category和Folder的公共属性和方法
    """

    POSITION_STEP = 2 ** 16

    title = models.CharField(max_length=255)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("parent"),
    )
    position = models.PositiveIntegerField(default=POSITION_STEP)
    user_id = models.IntegerField(db_index=True, null=True)
    subuser_id = models.IntegerField(db_index=True, null=True)

    @classmethod
    def get_current_max_position(cls, parent_id=None):
        if parent_id:
            queryset = cls.objects.filter(parent=parent_id).order_by("position")
        else:
            queryset = cls.objects.filter(parent=None).order_by("position")
        if not queryset:
            return
        position = queryset.last().position
        return position

    class Meta:
        abstract = True
