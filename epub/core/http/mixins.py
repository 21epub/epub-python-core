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
            return Results.error_info(str(e), code=400)
        except TypeError as e:
            return Results.error_info(str(e), code=400)
        except PermissionDenied:
            return Results.error_info(u'无访问权限', code=403)
        except Http404 as e:
            return Results.error_info(str(e), 404)
        except Exception as e:
            return Results.error_info(e, code=500)


class CsrfExemptMixin(object):
    """
    去除检测CSRF检测
    注意:
        这个Mixin 需要放在最左侧
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)