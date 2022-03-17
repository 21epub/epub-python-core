from django.db import models

from epub.core.models import BaseCommonModel

# Create your models here.


class Category(BaseCommonModel):

    category_type = models.CharField(max_length=32)
