from collections import OrderedDict
from rest_framework.pagination import (
    PageNumberPagination as drf_PageNumberPagination,
)
from rest_framework.settings import api_settings
from rest_framework import status
from rest_framework.response import Response

def _positive_int(integer_string, strict=False, cutoff=None):
    ret = int(integer_string)
    if ret == 0 and strict:
        raise ValueError()
    if ret < 0:
        return 1000
    if cutoff:
        return min(ret, cutoff)
    return ret

class PageNumberPagination(drf_PageNumberPagination):
    page_size = api_settings.PAGE_SIZE
    page_size_query_param = "size"
    max_page_size = 1000

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size,
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_paginated_response(self, data):
        ret = OrderedDict(
            [
                ("msg", "success"),
                ("code", status.HTTP_200_OK),
                (
                    "data",
                    OrderedDict(
                        [
                            ("sum", self.page.paginator.count),
                            ("page", self.page.number),
                            # ("numpages", self.page.number),
                            ("numpages", self.page.paginator.num_pages),
                            ("results", data),
                        ]
                    ),
                ),
            ]
        )
        return Response(data=ret)