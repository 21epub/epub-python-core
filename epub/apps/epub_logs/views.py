from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from epub.apps.epub_logs.filters import LogFilter
from epub.apps.epub_logs.models import LogEntry
from epub.apps.epub_logs.serializers import LogEntrySerializer


class LogAdminView(generics.ListAPIView):
    serializer_class = LogEntrySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LogFilter

    def get_queryset(self):
        return LogEntry.objects.filter(
            user_id=self.request.user.id, action_level__gt=LogEntry.DEBUG
        )


class LogObjectView(LogAdminView):
    def get_queryset(self):
        object_type = self.kwargs.get("object_type")
        pk = self.kwargs.get("pk")
        return LogEntry.objects.filter(
            user_id=self.request.user.id,
            object_type=object_type,
            object_id=pk,
            action_level__gt=LogEntry.DEBUG,
        )
