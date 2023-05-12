from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend

from epub.apps.epub_labels.models import AppLabel
from epub.apps.epub_labels.models import Label

PREFIX_FILTER_CONSTANT = "label."


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

        return AppLabel.get_filter_params_for_orm(label_linked_app, request.query_params, label_field, label_using_db)

    def filter_queryset(self, request, queryset, view):
        label_filter_params = self.get_filter_params(request, view)
        return queryset.filter(**label_filter_params)
