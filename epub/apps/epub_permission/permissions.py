from rest_framework.permissions import BasePermission


class CheckUserPermission(BasePermission):
    # short_book_type_mapping = {
    #     "b": "cbt",
    #     "q": "quiz",
    #     "d": "doc",
    #     "ds": "docset",
    #     "h5": "h5",
    # }

    @staticmethod
    def get_verify_code(module_type, verify_perm):
        '''
        verify_perm: view 对某种请求方式定义的一个用来做权限认证的字符串
        返回一个字符串，用来校验权限，
        如果 verify_perm 没有提供关键字 module_type ，不会对 verify_perm 做任何处理
        例如：
            module_type = "cbt", verify_perm = "{module_type}.create" -> "cbt.create"
        或者：
            module_type = "cbt", verify_perm = "admin.label.menu" -> "admin.label.menu"
        '''
        # 根据内容模块类型关键字，拼接当前请求需要校验的权限
        return verify_perm.format(module_type=module_type)

    @staticmethod
    def get_module_type(view):
        '''
        获取内容模块校验权限的关键字：
        例如：cbt、quiz
        '''
        module_type = view.kwargs.get("book_type")
        return module_type

    @staticmethod
    def get_user_perms(request):
        '''
        获取用户权限
        '''
        return [perm.get("code") for perm in request.user.subuser_perms]

    @staticmethod
    def verify_permission(verify_code, user_perms):
        return verify_code in user_perms

    def has_permission(self, request, view):
        # 1. 拿 view 内定义的权限 permissions
        view_defined_permissions = getattr(view, "permissions", {})

        # view 内没有对当前请求方式设置权限验证, 不限制, 直接返回 True
        verify_perm = view_defined_permissions.get(request.method, [])
        if not verify_perm:
            return True

        # view 内对当前请求方式定义了权限验证, 需要走认证逻辑

        # 获取当前用户的所有权限列表
        user_perms = self.get_user_perms(request)

        if not user_perms:
            return False

        # 获取 内容模块的 类型
        module_type = self.get_module_type(view)

        # 获取当前请求需要验证的完整的 code
        verify_code = self.get_verify_code(module_type, verify_perm)

        # 校验权限
        return self.verify_permission(verify_code, user_perms)

    # ---------------- delete ----------------

        # # 管理员不做限制
        # if request.user.subuser_is_superuser:
        #     # 机构管理员，允许查看本机构所有内容
        #     view.kwargs["show_all_user_contents"] = True
        #     # 查看跨机构作品权限
        #     # view.kwargs["show_all_contents"] = True
        #     return True
        #
        # # 用户没有任何权限
        # if not request.user.subuser_perms:
        #     return False
        #
        # user_perm_list = self.get_user_perm_list(request.user.subuser_perms)
        #
        # # url 没有 book_type 参数，view 内定义的 permission 应写完整
        # book_type = view.kwargs.get("book_type")
        # if not book_type:
        #     book_type = self.short_book_type_mapping.get(
        #         view.kwargs.get("short_book_type")
        #     )
        # model_type = view.kwargs.get("model_type")
        # if not book_type or model_type:
        #     return self.check_permission(
        #         view, request, view_permissions, user_perm_list, model_type=model_type
        #     )
        #
        # current_request_view_permissions = self.get_view_allowed_permission(
        #     view_permissions, book_type
        # )
        #
        # return bool(
        #     self.check_permission(
        #         view, request, current_request_view_permissions, user_perm_list
        #     )
        # )
    #
    # @staticmethod
    # def check_permission(
    #     view, request, view_permissions, user_perm_list, model_type=None
    # ):
    #     if not model_type:
    #         for user_perm in user_perm_list:
    #             if view_permissions.get(request.method)[0] == user_perm:
    #
    #                 if (
    #                     ".".join([user_perm, "show_all_user_contents"])
    #                     in user_perm_list
    #                 ):
    #                     view.kwargs["show_all_user_contents"] = True
    #                 view.kwargs["user_perm_list"] = user_perm_list
    #                 return True

    # ---------------- delete ----------------

    def has_object_permission(self, request, view, obj):

        view_permissions = getattr(view, "permissions", None)
        # 视图内没有任何权限限制
        if not view_permissions:
            return True

        # 视图内没有对当前请求方式做限制
        if not view_permissions.get(request.method):
            return True

        if hasattr(obj, "check_action_permission"):

            view_obj_permission = view.permissions.get(request.method, None)
            if not view_obj_permission:
                # view 不对当前请求方式限制
                return True

            user_perm_list = view.kwargs.get("user_perm_list")
            return obj.check_action_permission(
                request, view_obj_permission[0], user_perm_list
            )

        return True
