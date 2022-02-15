## 功能介绍
epub_permission 是一套基于 RESTful 的权限认证，提供了：
1. 一个由 Django REST framework 的 BasePermission 扩展的权限类，提供一套内容模块的自定义权限认证方式;
2. 一个内容模块相关的 ModelMixin ，为内容模块提供 object 级别的权限认证方式。

## 使用方式
1. 在 settings 中注册：
    ```python
   REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "epub.apps.epub_permission.permissions.ModulePermission"
    ]}
    ```

2. 相关 Model 继承 ModulePermissionMixin:
    ```python
   from epub.apps.epub_permission.mixins import ModulePermissionMixin
   from django.db import models

   class Book(ModulePermissionMixin, models.Model):
       title = models.CharField(max_length=255, blank=False, db_index=True)
    ```
   
3. 相关 view 内定义权限
    ```python
   from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

   class BookListCreateAPIView(ListCreateAPIView):

       permissions = {
            "GET": "{module_type}.list",
            "POST": "{module_type}.create"
        }
   
   class BookRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

       permissions = {
            "GET": "{module_type}.detail",
            "PATCH": "{module_type}.update"
            "DELETE": "{module_type}.delete"
        }
   
    ```