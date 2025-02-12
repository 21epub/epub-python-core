### 功能介绍

实现部门级别的数据权限验证

### 权限结构解释

以 `book` 为例，`book` 有 列表、编辑、删除 权限，分别用 `book.list` 、`book.edit` 、 `book.delete` 来表示
用户所在部门以 `dept_id` 表示,
假设用户权限如下：

```json
{
  "perms": [
    {
      "code": "book.list",
      "show_all": true,
      "deps": [
        1
      ]
    },
    {
      "code": "book.edit",
      "deps": [
        1
      ]
    },
    {
      "code": "book.delete",
      "only_self": true,
      "deps": [
        1
      ]
    }
  ]
}
```

1. `show_all` 表示 `book` 的 `list` 权限下可以访问所有部门数据，即不按照部门过滤
2. `only_self` 表示 `book` 的 `delete` 操作 只能删除自己的数据
3. 当没有 `show_all` 或 `only_self` 时，`deps` 表示当前仅可以操作指定部门的数据，deps 为部门 id 列表

### view 验证逻辑

1. 从 view 中获取权限，并验证用户是否有权限
2. 如果用户有权限，返回 `True`
3. 如果用户没有权限，返回 `False`

### 对象级别 验证逻辑

1. 从 view 中获取权限 和 对象
2. 依赖 DRF view 的 `get_object` 中调用的 `check_object_permission` 方法验证对象级别权限
3. 如果用户有权限，返回 `True`
4. 如果用户没有权限，返回 `False`

**注意：`check_object_permission` 方法会自动调用 `CheckObjectPermissionModelMixin.check_action_permission`
，所以如果在view中重写了 `get_object` 方法，请确保调用`check_object_permission`**

### 使用步骤

1.在 view 中 添加

```python
from epub.apps.account.permissions import CheckUserPermission

permission_classes = [CheckUserPermission]
``` 

或全局配置

```python
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["epub.apps.account.permissions.CheckUserPermission"]
}
```

2.在 view 中 添加 权限字典

```python
permissions = {
    "POST": "book.create",
    "GET": "book.list",
    "PATCH": "book.update",
}
```

3. 在对应的 model 中继承 `CheckObjectPermissionModelMixin`

```python
from django.db import models
from epub.apps.account.permissions import CheckObjectPermissionModelMixin


class Book(CheckObjectPermissionModelMixin, models.Model):
    pass
```

4. 如果默认的从 view 中获取权限的方法不能满足使用，可以继承对应的类，提供自定义的 get_view_perm_class 类, 例如

```python
from epub.apps.account.permissions import CheckUserPermission


class CustomPermissionService:
    def get_view_perm(self, request, view):
        pass


class CustomCheckUserPermission(CheckUserPermission):
    get_view_perm_class = CustomPermissionService

```

    


