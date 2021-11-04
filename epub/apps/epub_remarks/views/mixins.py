from rest_framework.response import Response

from epub.apps.account.mixins import get_user_and_subuser_id_nickname


class RemarkDeleteMixin(object):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        user_id, subuser_id, nickname = get_user_and_subuser_id_nickname(request)
        if obj.subuser_id != subuser_id:
            return Response(data="没有删除此备注的权限", status=403)
        super().delete(request, *args, **kwargs)
        return Response()
