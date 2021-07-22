from rest_framework.request import Request
from rest_framework.filters import BaseFilterBackend


class ContentCategoryFilterBackend(BaseFilterBackend):
    def get_filter_params(self, request: Request, view):
        category_filter_kwarg = getattr(view, "category_filter_kwarg", "category_id")
        filter_category_ids = request.query_params.getlist(category_filter_kwarg)
        return filter_category_ids

    def filter_queryset(self, request, queryset, view):
        filter_category_ids = self.get_filter_params(request, view)
        if filter_category_ids:
            return queryset.filter(categories__in=filter_category_ids).distinct()
        return queryset
