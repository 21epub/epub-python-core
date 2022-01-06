from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from epub.apps.epub_permission.mixins import ModulePermissionMixin
from epub.apps.epub_remarks.models import Remark
from epub.core.models import BasicContentModel
from epub.apps.epub_categories.models.category import Category
from epub.apps.epub_folders.models.folder import Folder
from epub.apps.epub_labels.models import LabelMixin

from model_utils import FieldTracker


class Book(LabelMixin, ModulePermissionMixin, BasicContentModel):
    title = models.CharField(max_length=255, blank=False, db_index=True)
    cover = models.FileField()
    # user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tracker = FieldTracker()
    categories = models.ManyToManyField(
        Category, related_name="book_set", default=models.CASCADE
    )
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True)
    remarks = GenericRelation(Remark)
    subuser_id = models.IntegerField(default=None, null=True)
    user_id = models.IntegerField(default=None, null=True)

    def __str__(self):
        return self.title
