from django.db import models


class CreatorModelMixin(models.Model):

    user_id = models.IntegerField(default=None, null=True, db_index=True)
    subuser_id = models.IntegerField(default=None, null=True, db_index=True)
    nickname = models.CharField(max_length=150, null=True, default="")

    class Meta:
        abstract = True
