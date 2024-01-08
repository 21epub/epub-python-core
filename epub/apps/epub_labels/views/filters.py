from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

from epub.apps.epub_labels.models import AppLabel, Label

PREFIX_FILTER_CONSTANT = "label"


class LabelFilterMixin:
    def get_filter_params_for_orm(
        self,
        label_linked_app,
        query_params,
        label_field="label",
        label_using_db="default",
        view=None,
    ):
        # 同一个标签支持多选，条件关系是 or
        # 不同标签之间，条件关系是 and

        filter_mappings = self.get_filter_mappings(
            label_linked_app=label_linked_app,
            label_field=label_field,
            label_using_db=label_using_db,
            view=view,
        )
        label_query = Q()
        for label_param, map_lookup_type in filter_mappings.items():
            label_value = query_params.getlist(
                PREFIX_FILTER_CONSTANT + "." + label_param, None
            )
            single_query = Q()
            for _label_value in label_value:
                if _label_value == "null":
                    # 表示查找未设置值过 或 删除值的标签: 没有这个key 或 这个key的值为空值, False除外，因为有布尔类型的标签
                    single_query |= (
                        ~Q(**{f"{PREFIX_FILTER_CONSTANT}__has_key": label_param})
                        | Q(**{f"{PREFIX_FILTER_CONSTANT}__{label_param}__exact": []})
                        | Q(**{f"{PREFIX_FILTER_CONSTANT}__{label_param}__exact": None})
                        | Q(**{f"{PREFIX_FILTER_CONSTANT}__{label_param}__exact": ""})
                    )
                    continue
                lookup_value = map_lookup_type["lookup"]
                value_type = map_lookup_type["value_type"]
                if value_type == Label.VALUE_TYPE_CHOICES.number:
                    try:
                        single_query |= Q(**{lookup_value: float(_label_value)})
                    except ValueError:
                        pass
                elif value_type == Label.VALUE_TYPE_CHOICES.bool:
                    if _label_value == "true":
                        single_query |= Q(**{lookup_value: True})
                    elif _label_value == "false":
                        single_query |= Q(**{lookup_value: False})
                else:
                    single_query |= Q(**{lookup_value: _label_value})
            label_query &= single_query
        return label_query

    def get_filter_mappings(
        self, label_linked_app, label_field="label", label_using_db="default", view=None
    ):
        return AppLabel.get_filter_mappings(
            linked_app=label_linked_app,
            jsonfield_name=label_field,
            label_using_db=label_using_db,
        )


class LabelFilter(LabelFilterMixin, BaseFilterBackend):
    def get_filter_params(self, request, view):
        assert hasattr(
            view, "label_linked_app"
        ), 'Class {serializer_class} missing "label_linked_app" attribute'.format(
            serializer_class=view.__class__.__name__
        )
        label_linked_app = getattr(view, "label_linked_app")
        label_using_db = getattr(view, "label_using_db", "default")
        label_field = getattr(view, "label_field", "label")

        return self.get_filter_params_for_orm(
            label_linked_app, request.query_params, label_field, label_using_db, view
        )

    def filter_queryset(self, request, queryset, view):
        label_filter_params = self.get_filter_params(request, view)
        return queryset.filter(label_filter_params)
