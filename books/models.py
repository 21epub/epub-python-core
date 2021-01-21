from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
from epub.core.models import BasicContentModel

from model_utils import FieldTracker

# Create your models here.


class Book(BasicContentModel):
    title = models.CharField(max_length=255, blank=False, db_index=True)
    cover = models.FileField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tracker = FieldTracker()
