from django_filters import FilterSet, filters

from epub.apps.epub_logs.models import LogEntry


class LogFilter(FilterSet):
    type = filters.CharFilter(field_name="object_type")
    after = filters.DateFilter(field_name="action_time", lookup_expr="gte")
    before = filters.DateFilter(field_name="action_time", lookup_expr="lte")

    class Meta:
        model = LogEntry
        fields = [
            "subuser_id",
            "type",
            "after",
            "before",
        ]
