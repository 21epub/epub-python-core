from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext as _
# Create your models here.


class Category(MPTTModel):
    POSITION_STEP = 2 ** 16

    title = models.CharField(max_length=255)
    category_type = models.CharField(max_length=32)
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

    @staticmethod
    def get_current_max_position(parent_id=None):
        if parent_id:
            queryset = Category.objects.filter(parent=parent_id).order_by("position")
        else:
            queryset = Category.objects.filter(parent=None).order_by("position")
        if not queryset:
            return
        position = queryset.last().position
        return position

    class MPTTMeta:
        order_insertion_by = ['position']
