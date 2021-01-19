from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, Http404

from api import Results


class APIViewMixin(object):

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
