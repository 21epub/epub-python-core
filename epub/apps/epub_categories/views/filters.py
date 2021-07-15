from rest_framework.request import Request
from rest_framework.filters import BaseFilterBackend


class CategoryTypeFilterBackend(BaseFilterBackend):
    def get_filter_params(self, request: Request, view):
        kwargs = view.kwargs
        category_type = kwargs.get("category_type")
        return {"category_type": category_type}

    def filter_queryset(self, request: Request, queryset, view):
        filter_params = self.get_filter_params(request, view)
        return queryset.filter(**filter_params)


class CategoryUserFilterBackend(BaseFilterBackend):
    def get_user_info(self, request: Request):
        user_info = {}
        if request and request.user.is_authenticated:
            user_info["user_id"] = request.user.id
            user_info["subuser_id"] = request.user.subuser_id
        else:
            user_info["user_id"] = None
            user_info["subuser_id"] = None
        return user_info

    def get_filter_params(self, request: Request, view):
        filter_params = {}
        kwargs = view.kwargs
        user_filter = kwargs.get("user_filter")
        user_info = self.get_user_info(request)
        for key in user_filter:
            filter_params[key] = user_info.get(key)
        return filter_params

    def filter_queryset(self, request: Request, queryset, view):
        filter_params = self.get_filter_params(request, view)
        return queryset.filter(**filter_params)


class ContentCategoryFilterBackend(BaseFilterBackend):
    def get_filter_params(self, request: Request, view):
        filter_category_id = request.query_params.getlist("category_id")
        return filter_category_id

    def filter_queryset(self, request, queryset, view):
        filter_category_id = self.get_filter_params(request, view)
        if filter_category_id:
            return queryset.filter(categories__in=filter_category_id).distinct()
        return queryset
