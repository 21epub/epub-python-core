from django_filters import FilterSet, filters

from epub.apps.epub_logs.models import LogEntry


class LogFilter(FilterSet):
    start_time = filters.DateTimeFilter(field_name="action_time", lookup_expr="gte")
    end_time = filters.DateTimeFilter(field_name="action_time", lookup_expr="lte")

    class Meta:
        model = LogEntry
        fields = [
            "subuser_id",
            "object_type",
            "start_time",
            "end_time",
        ]
