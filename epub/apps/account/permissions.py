from rest_framework import permissions

from epub.apps.account.mixins import EpubViewPermMixin
from epub.apps.account.permission_service import EpubPermissionService


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user_id == request.user.id


class CheckUserPermission(EpubViewPermMixin, permissions.BasePermission):
    get_view_perm_class = EpubPermissionService

    def has_permission(self, request, view):
        if request.user.subuser_is_superuser:
            return True
        view_perm = self.get_view_perm(request, view)
        if not view_perm:
            return True

        if view_perm in request.user.subuser_perms:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "check_action_permission"):
            return obj.check_action_permission(request, view)
        return True


class CheckObjectPermissionModelMixin(EpubViewPermMixin):
    get_view_perm_class = EpubPermissionService

    def check_action_permission(self, request, view):
        view_perm = self.get_view_perm(request, view)
        if not view_perm:
            return True

        if hasattr(self, "is_write_allow"):
            if not self.is_write_allow():
                return False

        if self.user_id != request.user.id:
            return False

        if request.user.subuser_is_superuser:
            return True

        if view_perm in request.user.subuser_perms:
            perm_detail = request.user.subuser_perms.get(view_perm)
            if perm_detail.get("show_all"):
                return True

            if perm_detail.get("only_self"):
                if self.subuser_id == request.user.subuser_id:
                    return True
                else:
                    return False

            # 部门权限
            if self.dept_id in perm_detail.get("deps", []):
                return True
            else:
                return False

        else:
            return False


