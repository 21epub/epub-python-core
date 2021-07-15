from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from epub.core.http.response import Results


class APIViewMixin(object):
    """
    对常见异常的统一处理，使用于所有APIView，统一错误格式。
    注意：
        这个Mixin 使用是需要靠左边。
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ValueError as e:
            return Results.error_info(str(e), 400)
        except TypeError as e:
            return Results.error_info(str(e), 400)
        except PermissionDenied:
            return Results.error_info(u"无访问权限", 403)
        except Http404 as e:
            return Results.error_info(str(e), 404)
        except Exception as e:
            return Results.error_info(e, 500)


class CsrfExemptMixin(object):
    """
    去除检测CSRF检测
    注意:
        这个Mixin 需要放在最左侧
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CreateResponseMixin(Results):
    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        if str(res.status_code).startswith("2"):
            return self.succss_result(res.data)
        else:
            return self.error_info(res.data, res.status_code)


class RetrieveResponseMixin(Results):
    def retrieve(self, request, *args, **kwargs):
        res = super().retrieve(request, *args, **kwargs)
        if str(res.status_code).startswith("2"):
            return self.succss_result(res.data)
        else:
            return self.error_info(res.data, res.status_code)


class DeleteResponseMixin(Results):
    def delete(self, request, *args, **kwargs):
        res = super().delete(request, *args, **kwargs)
        if str(res.status_code).startswith("2"):
            return self.succss_result(res.data)
        else:
            return self.error_info(res.data, res.status_code)


class UpdateResponseMixin(Results):
    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)
        if str(res.status_code).startswith("2"):
            return self.succss_result(res.data)
        else:
            return self.error_info(res.data, res.status_code)


class RetrieveUpdateDeleteResponseMixin(
    RetrieveResponseMixin,
    UpdateResponseMixin,
    DeleteResponseMixin,
):
    pass


class CreateDeleteResponseMixin(CreateResponseMixin, DeleteResponseMixin):
    pass
