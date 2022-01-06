
class ModulePermissionMixin(object):

    def check_action_permission(self, request, object_verify_code, user_perms):
        if self.module_content_can_changed():
            if request.user.id == self.user_id:
                if request.user.subuser_id == self.subuser_id:
                    return True
                elif object_verify_code in user_perms:
                    return True
                else:
                    return False
            return False
        return False

    def module_content_can_changed(self):
        return True
