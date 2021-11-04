from django.apps import apps
from epub.apps.epub_logs.mixins import LoggingViewMixin
from epub.apps.epub_logs.models import LogEntry
from epub.core.http.mixins import CreateResponseMixin, RetrieveUpdateDeleteResponseMixin
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from epub.apps.epub_remarks.models import Remark, ContentType
from epub.apps.epub_remarks.serializers.serializers import RemarkSerializer
from epub.apps.epub_remarks.views.mixins import RemarkDeleteMixin


class RemarkListCreateAPIView(
    LoggingViewMixin, CreateResponseMixin, generics.ListCreateAPIView
):
    serializer_class = RemarkSerializer
    queryset = Remark.objects.all()

    def get_queryset(self):
        id_list = self.get_belonged_to_obj_ids()

        app_name = getattr(self, "app_name")
        model_name = getattr(self, "model_name")

        if app_name and model_name:
            try:
                app_model = apps.get_model(app_name, model_name)
            except LookupError:
                raise ValidationError({"detail": ["数据类型不存在."]})

            ct = ContentType.objects.get(model=model_name, app_label=app_name)
            remarks = Remark.objects.filter(content_type=ct, object_id__in=id_list)
        else:
            raise NotImplementedError(
                " View 内必须指定 model_name:创建备注对象的 Model; app_name:创建备注对象 Model 的 app_label "
            )

        return remarks

    def get_belonged_to_obj_ids(self):
        raise NotImplementedError(
            " 必须实现 get_belonged_to_obj_ids() 方法，以 return [id1 ,id2, ...] 的形式提供要查询备注的 instance 的 ID ，"
        )

    def get_belonged_obj(self):
        raise NotImplementedError(
            " 必须实现 get_belonged_obj() 方法，以 return instance 的形式提供要创建备注的 instance ，"
        )

    def create(self, request, *args, **kwargs):
        instance = self.get_belonged_obj()
        self.kwargs["belonged_obj"] = instance

        return super(RemarkListCreateAPIView, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.log(
            serializer.instance.content_object,
            action_type=LogEntry.ADDITION,
            action_name="添加备注",
        )


class RemarkRetrieveDestroyAPIView(
    LoggingViewMixin,
    RetrieveUpdateDeleteResponseMixin,
    RemarkDeleteMixin,
    generics.RetrieveDestroyAPIView,
):
    serializer_class = RemarkSerializer
    queryset = Remark.objects.all()
    lookup_url_kwarg = "remark_id"

    def perform_destroy(self, instance):
        self.log(
            instance.content_object, action_type=LogEntry.DELETION, action_name="删除备注"
        )
        super().perform_destroy(instance)
