from rest_framework.request import Request
from rest_framework.filters import BaseFilterBackend


class ContentCategoryFilterBackend(BaseFilterBackend):
    def get_filter_params(self, request: Request, view):
        filter_category_id = request.query_params.getlist("category_id")
        return filter_category_id

    def filter_queryset(self, request, queryset, view):
        filter_category_id = self.get_filter_params(request, view)
        if filter_category_id:
            return queryset.filter(categories__in=filter_category_id).distinct()
        return queryset
