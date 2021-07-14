from rest_framework.filters import BaseFilterBackend


class CategoryTypeFilterBackend(BaseFilterBackend):
    def get_filter_params(self, request, view):
        kwargs = view.kwargs
        category_type = kwargs.get("category_type")
        return {"category_type": category_type}

    def filter_queryset(self, request, queryset, view):
        filter_params = self.get_filter_params(request, view)
        return queryset.filter(**filter_params)


class CategoryUserFilterBackend(BaseFilterBackend):
    def get_user_info(self, request):
        user_info = {}
        if request and request.user.is_authenticated:
            user_info["user_id"] = request.user.id
            user_info["subuser_id"] = request.user.subuser_id
        else:
            user_info["user_id"] = None
            user_info["subuser_id"] = None
        return user_info

    def get_filter_params(self, request, view):
        filter_params = {}
        kwargs = view.kwargs
        user_filter = kwargs.get("user_filter")
        user_info = self.get_user_info(request)
        for key in user_filter:
            filter_params[key] = user_info.get(key)
        return filter_params

    def filter_queryset(self, request, queryset, view):
        filter_params = self.get_filter_params(request, view)
        return queryset.filter(**filter_params)
