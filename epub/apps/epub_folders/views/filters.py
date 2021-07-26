from rest_framework.request import Request
from rest_framework.filters import BaseFilterBackend
from epub.apps.epub_folders.models.folder import Folder


class ContentFolderFilterBackend(BaseFilterBackend):
    def get_filter_params(self, request: Request, view):
        folder_filter_kwarg = getattr(view, "folder_filter_kwarg", "folder_id")
        filter_folder_ids = request.query_params.getlist(folder_filter_kwarg)
        return filter_folder_ids

    def filter_queryset(self, request, queryset, view):
        # 获取所有需要查询的folder_id
        filter_folder_ids = self.get_filter_params(request, view)
        # 初始化查询list
        filter_list = []
        for folder_id in filter_folder_ids:
            # 遍历 获取查询folder_id的所有后代(包括本身)
            try:
                folder = Folder.objects.get(id=folder_id)
                descendants = folder.get_descendants(include_self=True)
            except (Folder.DoesNotExist, ValueError):
                continue
            filter_list.extend([descendant_info.id for descendant_info in descendants])
        # 去重
        filter_list = list(set(filter_list))
        if filter_list:
            return queryset.filter(folder_id__in=filter_list)
        return queryset
