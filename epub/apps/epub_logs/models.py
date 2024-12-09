from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from epub.apps.account.models import CreatorModelMixin


class LogEntry(CreatorModelMixin, models.Model):

    DEBUG = 0
    INFO = 1
    WARNING = 2
    KEYFRAME = 3
    ERROR = 10

    ACTION_LEVEL_CHOICES = (
        (DEBUG, _("Debug")),
        (INFO, _("Info")),
        (WARNING, _("Warning")),
        (KEYFRAME, _("KeyFrame")),
        (ERROR, _("Error")),
    )

    ADDITION = 1
    CHANGE = 2
    DELETION = 3
    EDIT = 4
    PUBLISH = 5
    PUSH = 6
    ACTION_TYPE_CHOICES = (
        (ADDITION, _("Addition")),
        (CHANGE, _("Change")),
        (DELETION, _("Deletion")),
        (EDIT, _("Edit")),
        (PUBLISH, _("Publish")),
        (PUSH, _("Push")),
    )
    action_time = models.DateTimeField(
        _("action time"),
        default=timezone.now,
        editable=False,
        db_index=True,
    )
    action_level = models.PositiveSmallIntegerField(
        _("action level"), choices=ACTION_LEVEL_CHOICES, default=INFO
    )
    action_type = models.PositiveSmallIntegerField(_("action type"))
    action_ip = models.GenericIPAddressField()
    action_name = models.TextField(_("action name"), blank=True)

    object_type = models.CharField(max_length=100)
    object_id = models.CharField(_("object id"), max_length=100, blank=True, null=True)
    object_repr = models.CharField(_("object repr"), max_length=200)

    # change_message is either a string or a JSON structure
    change_message = models.TextField(_("change message"), blank=True)

    class Meta:

        indexes = [
            models.Index(fields=["object_type", "object_id"]),
        ]
        ordering = ["-action_time"]
