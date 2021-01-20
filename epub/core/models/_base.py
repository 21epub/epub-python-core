from django.db import models
from django.utils.translation import ugettext as _

from model_utils import Choices, FieldTracker
from model_utils.models import StatusModel, SoftDeletableModel, TimeStampedModel


class BasicContentModel(StatusModel, SoftDeletableModel, TimeStampedModel):
    """
    内容基类，包含功能：
        created, modified
        status 默认：draft, published
        is_removed: 软删除标记

    """
    STATUS = Choices('draft', 'published')

    class Meta:
        abstract = True



class BaiscTrackModel(BasicContentModel):
    tracker = FieldTracker()

    class Meta:
        abstract = True
