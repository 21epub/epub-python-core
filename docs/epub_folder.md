### 功能介绍

```
本应用为公共应用， 提供一组api接口，可以为内容模块(如Book、Knowledge等)添加公共文件夹信息

models定义：
class Folder(MPTTModel):
    POSITION_STEP = 2 ** 16
    title = models.CharField(max_length=255)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("parent"),
    )
    folder_type = models.CharField(max_length=32)
    position = models.PositiveIntegerField(default=POSITION_STEP)
    user_id = models.IntegerField(db_index=True, null=True)
    subuser_id = models.IntegerField(db_index=True, null=True)
    
    class MPTTMeta:
        order_insertion_by = ["position"]
```

### 使用介绍

```
1：epub_folders 注册到settings文件的INSTALLED_APPS列表内
2：将公共文件夹路由添加到需要使用文件夹功能的内容模块的路由中
urlpatterns = [
    re_path(
        "folders/",
        include(
            ("epub.apps.epub_folders.urls", "epub_folders"),
            namespace="epub_folders",
        ),
        {
            "folder_type": "h5",
            "app_name": "books",
            "model_name": "Book",
            "user_filter": ["user_id", "subuser_id"],
            "order_by": "position",
        },
    ),
]
参数说明：
	folder_type： 用于指定文件夹的类型
	app_name：应用名，如：epub_books
	model_name: 模型名， 如：Book
	user_filter: 筛选列表， 如果传user_id或subuser_id 则获取文件夹列表信息的时候会根据当前请求的user_id或subuser_id进行筛选
	order_by: 排序字段， 默认按照 position 排序，可配置 "-position" 倒序排列

3：为内容模块的models添加字段
例：
models.py

from epub.apps.epub_folders.models.folder import Folder

class Book(models.Model):
	folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True)

4：添加筛选信息(可选)
本模块提供根据folder_id 筛选内容信息功能，可自行引用
将ContentFolderFilterBackend添加到filter_backends中即可。
例：
views.py
from epub.apps.epub_folders.views.filters import ContentFolderFilterBackend

class BookListAPIView(generics.ListAPIView):
	filter_backends = [ContentFolderFilterBackend]






```



### API介绍

```
API介绍：
'folders/'	创建公共文件夹、获取文件夹列表
创建文件夹：
	入参：parent	  父节点id
		 title		标题

'folders/<pk>/'	获取文件夹详情、修改文件夹、删除文件夹
修改文件夹：
	入参：title	  标题
	
'folders/sort/'	修改文件夹排序
排序文件夹：
	入参：target	  目标节点id
		 before     排序后目标节点前id
		 after      排序后目标节点后id
		 parent     父节点id
		 
'folders/batch/'	批量给内容添加文件夹信息
	入参：content_ids    内容id
	     folder_id      文件夹id
	功能：批量将content_ids中的内容文件夹信息修改为folder_id
```

