from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model

from epub.apps.epub_remarks.models import Remark
from epub.core.models import BasicContentModel
from epub.apps.epub_categories.models.category import Category
from epub.apps.epub_folders.models.folder import Folder
from epub.apps.epub_labels.models import LabelMixin
from django.utils.translation import ugettext as _
from model_utils import FieldTracker, Choices

# Create your models here.
from epub.core.models._content import BasicContentManager
from epub.core.models.cache import CacheModelMixin, CacheQuerySet


class Book(CacheModelMixin, LabelMixin, BasicContentModel):
    UNIQUE_KEYS = ["pk", "title"]
    STATUS_CHOICES = Choices(
        (0, "draft", _("草稿")),
        (1, "published", _("已发布")),
    )

    title = models.CharField(max_length=255, blank=False, db_index=True)
    cover = models.FileField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tracker = FieldTracker()
    categories = models.ManyToManyField(
        Category, related_name="book_set", default=models.CASCADE
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_CHOICES.draft)
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True)
    remarks = GenericRelation(Remark)

    objects = BasicContentManager.from_queryset(CacheQuerySet)()

    def __str__(self):
        return self.title

    def wf_publish(self):
        self.status = self.STATUS_CHOICES.published
        self.save()
