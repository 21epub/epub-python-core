from rest_framework.filters import BaseFilterBackend

from epub.apps.epub_labels.models import AppLabel
from epub.apps.epub_labels.models import Label


class LabelFilter(BaseFilterBackend):
    def get_filter_params(self, request, view):
        assert hasattr(
            view, "label_linked_app"
        ), 'Class {serializer_class} missing "label_linked_app" attribute'.format(
            serializer_class=view.__class__.__name__
        )
        label_linked_app = getattr(view, "label_linked_app")

        label_using_db = getattr(view, "label_using_db", "default")
        label_field = getattr(view, "label_field", "label")
        filter_mappings = AppLabel.get_filter_mappings(
            linked_app=label_linked_app,
            jsonfield_name=label_field,
            label_using_db=label_using_db,
        )

        label_filter = {}
        for label_param, map_lookup_type in filter_mappings.items():
            label_value = request.query_params.get(label_param, None)
            if label_value:
                lookup_value = map_lookup_type["lookup"]
                value_type = map_lookup_type["value_type"]
                if value_type == Label.VALUE_TYPE_CHOICES.number:
                    label_filter[lookup_value] = float(label_value)
                else:
                    label_filter[lookup_value] = label_value
        return label_filter

    def filter_queryset(self, request, queryset, view):
        label_filter_params = self.get_filter_params(request, view)
        return queryset.filter(**label_filter_params)
