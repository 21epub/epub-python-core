import logging
import random
import time
from datetime import datetime
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from epub.apps.account.models import CreatorModelMixin

logger = logging.getLogger("django")


def user_directory_path(instance, filename: str):
    prefix = instance.__class__.__name__
    prefix = prefix.lower().replace("material", "")
    dt = datetime.now()
    if instance.user_id is None:
        _user_id = 1
    else:
        _user_id = instance.user_id
    if filename.startswith("trash/"):
        return filename

    # 毫秒级别的时间戳
    timestamp = int(time.time() * 1000)
    randint = random.randint(100, 999)
    suffix = filename.split('.')[-1]
    name = f"materials/{prefix.lower()}/{_user_id}/{dt.year}/{dt.month}/{dt.day}/{timestamp}_{randint}.{suffix}"
    logger.info(name)
    return name


class Remark(CreatorModelMixin, models.Model):
    content = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    content_type = models.ForeignKey(
        ContentType,
        db_constraint=False,
        on_delete=models.CASCADE,
        default=None,
    )
    object_id = models.PositiveIntegerField(null=True)
    action = models.CharField(max_length=50, default=None, null=True, blank=True)
    file = models.FileField(
        upload_to=user_directory_path, blank=True, null=True, default=None
    )
    title = models.CharField(max_length=255, null=True, blank=True, default=None)
    content_object = GenericForeignKey("content_type", "object_id")

    def get_file_url(self):
        media_url = getattr(settings, "OSS_MEDIA_URL", "")

        if self.file:
            return f"{media_url}{self.file.name}"

    class Meta:
        ordering = ("-created",)
