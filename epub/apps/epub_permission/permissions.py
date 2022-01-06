from rest_framework.permissions import BasePermission


class ModulePermission(BasePermission):

    def has_permission(self, request, view):
        # 拿 view 内定义的权限 permissions
        view_defined_permissions = getattr(view, "permissions", {})

        verify_perm = view_defined_permissions.get(request.method, "")

        if not verify_perm:
            # view 内没有对当前请求方式设置权限验证, 不限制, 直接返回 True
            return True

        # 获取当前用户的所有权限列表
        user_perms = self.get_user_perms(request)

        if not user_perms:
            return False

        # 获取当前请求需要验证的完整的 code
        verify_code = self.get_verify_code(view, verify_perm)

        # 校验权限
        flag = self.verify_permission(verify_code, user_perms)
        if flag:
            self.verify_permission_success(request, view, verify_code, user_perms)

        return flag

    def has_object_permission(self, request, view, obj):
        view_verify_code = view.kwargs.get("verify_code", None)

        if not view_verify_code:
            # 没有 view_verify_code ,说明没有 view 没有权限限制
            return True

        object_verify_code = self.get_object_verify_code(view)

        user_perms = view.kwargs.get("user_perms")

        if hasattr(obj, "check_action_permission"):
            return obj.check_action_permission(request, object_verify_code, user_perms)

        return True

    @staticmethod
    def get_user_perms(request):
        '''
        获取用户权限
        '''
        return [perm.get("code") for perm in request.user.subuser_perms]

    def get_verify_code(self, view, verify_perm):
        '''
        返回一个字符串，用来校验权限

        verify_perm: view 对某种请求方式定义的一个用来做权限认证的字符串, 如 {module_type}.create
        如果 verify_perm 没有提供关键字 module_type ，不会对 verify_perm 做任何处理
        例如：
            module_type = "cbt", verify_perm = "{module_type}.create" -> "cbt.create"
        或者：
            module_type = "cbt", verify_perm = "admin.label.menu" -> "admin.label.menu"
        '''
        # 获取 内容模块的 类型关键字
        module_type = self.get_module_type(view)

        # 根据内容模块类型关键字，拼接当前请求需要校验的权限
        verify_code = verify_perm.format(module_type=module_type)
        return verify_code

    @staticmethod
    def get_module_type(view):
        '''
        获取内容模块校验权限的关键字：
        例如：cbt、quiz
        '''
        module_type = view.kwargs.get("book_type")
        return module_type

    @staticmethod
    def verify_permission(verify_code, user_perms):
        return verify_code in user_perms

    @staticmethod
    def verify_permission_success(request, view, verify_code, user_perms):
        view.kwargs["verify_code"] = verify_code
        view.kwargs["user_perms"] = user_perms

    @staticmethod
    def get_object_verify_code(view):
        verify_code = view.kwargs.get("verify_code")
        return ".".join([verify_code, "show_all_user_contents"])
