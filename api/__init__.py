
from django.http import JsonResponse

from log import logger


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
        return JsonResponse(data=_info, status=200)


