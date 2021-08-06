"""
Extracted and modified from django-model-logging
It used it's own LogEntry model but since django
has it's own LogEntry maybe someone would want to
register in the same model instead of creating a
new one.
"""
from django.contrib.contenttypes.models import ContentType

from .models import LogEntry
from django.utils.translation import gettext as _

from ..account.mixins import GetUserViewMixin


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class LoggingViewMixin(GetUserViewMixin):
    def log(
        self,
        instance,
        action_type,
        action_name,
        action_level=LogEntry.INFO,
        change_message="",
    ):
        user_id, subuser_id, nickname = self.get_user_subuser()

        object_type = getattr(instance, "object_type", instance.__class__.__name__)

        LogEntry(
            user_id=user_id,
            subuser_id=subuser_id,
            nickname=nickname,
            object_type=object_type,
            object_id=instance.pk,
            object_repr=str(instance),
            action_ip=get_client_ip(self.request),
            action_type=action_type,
            action_name=action_name,
            action_level=action_level,
            change_message=change_message,
        ).save()


class LoggingViewSetMixin(LoggingViewMixin):
    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        if isinstance(instance, list):
            for row in instance:
                self.log(row, action_type=LogEntry.ADDITION, action_name="新增")
        else:
            self.log(instance, action_type=LogEntry.ADDITION, action_name="新增")

    def perform_update(self, serializer):
        super().perform_update(serializer)
        instance = serializer.instance
        if isinstance(instance, list):
            for row in instance:
                self.log(row, action_type=LogEntry.CHANGE, action_name="修改")
        else:
            self.log(instance, action_type=LogEntry.CHANGE, action_name="修改")

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.log(instance, action_type=LogEntry.DELETION, action_name="删除")
