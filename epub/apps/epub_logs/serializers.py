from rest_framework.serializers import ModelSerializer

from epub.apps.epub_logs.models import LogEntry


class LogEntrySerializer(ModelSerializer):
    class Meta:
        model = LogEntry
        fields = [
            "action_time",
            "action_ip",
            "action_name",
            "nickname",
            "object_type",
            "object_repr",
            "change_message",
        ]
