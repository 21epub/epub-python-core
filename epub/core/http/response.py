import json

from django.http import JsonResponse
from rest_framework.response import Response
from epub.core.log import logger


class Results(object):

    def __init__(self, page=1, nums=1, total=1):
        self.page = page
        self.nums = nums
        self.total = total

    @classmethod
    def error_info(cls, msg, code, status=None):
        if isinstance(msg, Exception):
            logger.exception('Results.error_info.exception')
            msg = u'服务器异常，等稍后再试！'
        if 500 <= code < 600:
            logger.exception("Results.error_info")
            msg = u'服务繁忙，等稍后...'

        _info = {
            "msg": msg,
            "code": code
        }
        if status is None:
            status = code
        _info = json.dumps(_info)
        return JsonResponse(data=_info, status=status)

    def succss_result(self, data=None):
        if data is None:
            data = []
        elif not isinstance(data, list):
            data = [data]
        _info = {'msg': u'success', 'code': 200, 'data': {
            'page': self.page,
            'numpages': self.nums,
            'sum': self.total,
            'results': data,
        }}
        _info = json.dumps(_info)
        return JsonResponse(data=_info, status=200)

class CreateResponseMixin(Results):
    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        if str(res.status_code).startswith("2"):
            res_data = self.succss_result(res.data)
        else:
            res_data = self.error_info(res.data, res.status_code)
        return Response(res_data)


class RetrieveResponseMixin(Results):
    def retrieve(self, request, *args, **kwargs):
        res = super().retrieve(request, *args, **kwargs)
        if str(res.status_code).startswith("2"):
            res_data = self.succss_result(res.data)
        else:
            res_data = self.error_info(res.data, res.status_code)
        return Response(res_data)


class DeleteResponseMixin(Results):
    def delete(self, request, *args, **kwargs):
        res = super().delete(request, *args, **kwargs)
        if str(res.status_code).startswith("2"):
            res_data = self.succss_result(res.data)
        else:
            res_data = self.error_info(res.data, res.status_code)
        return Response(res_data)


class UpdateResponseMixin(Results):
    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)
        if str(res.status_code).startswith("2"):
            res_data = self.succss_result(res.data)
        else:
            res_data = self.error_info(res.data, res.status_code)
        return Response(res_data)


class RetrieveUpdateDeleteResponseMixin(
    RetrieveResponseMixin,
    UpdateResponseMixin,
    DeleteResponseMixin,
):
    pass


class CreateDeleteResponseMixin(CreateResponseMixin, DeleteResponseMixin):
    pass
