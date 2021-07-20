from rest_framework.request import Request
from rest_framework.filters import BaseFilterBackend


class CommonTypeFilterBackend(BaseFilterBackend):
    def get_filter_params(self, request: Request, view):
        filter_kwargs = {}
        kwargs = view.kwargs
        category_type = kwargs.get("category_type")
        if category_type:
            filter_kwargs["category_type"] = category_type
        folder_type = kwargs.get("folder_type")
        if folder_type:
            filter_kwargs["folder_type"] = folder_type
        return filter_kwargs

    def filter_queryset(self, request: Request, queryset, view):
        filter_params = self.get_filter_params(request, view)
        return queryset.filter(**filter_params)


class CommonUserFilterBackend(BaseFilterBackend):
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
