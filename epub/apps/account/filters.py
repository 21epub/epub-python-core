from rest_framework.filters import BaseFilterBackend

from epub.apps.account.mixins import EpubViewPermMixin
from epub.apps.account.permission_service import EpubPermissionService


class DataDeptFilterBackend(EpubViewPermMixin, BaseFilterBackend):
    get_view_perm_class = EpubPermissionService

    def get_filter_params(self, request, view):
        if request.user.subuser_is_superuser:
            return {"user_id": request.user.id}
        view_perm = self.get_view_perm(request, view)
        data_scope = request.user.subuser_perms.get(view_perm, {})
        if data_scope.get("show_all"):
            return {"user_id": request.user.id}

        if data_scope.get("only_self"):
            return {
                "subuser_id": request.user.subuser_id,
                "user_id": request.user.id,
            }

        deps = data_scope.get("deps", [])
        return {"dept_id__in": deps, "user_id": request.user.id}

    def filter_queryset(self, request, queryset, view):
        filter_params = self.get_filter_params(request, view)
        return queryset.filter(**filter_params)
