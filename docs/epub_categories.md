### 功能介绍

```
本应用为公共应用， 提供一组api接口，可以为内容模块(如Book、Knowledge等)添加公共分类信息

models定义：
class Category(MPTTModel):
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
    category_type = models.CharField(max_length=32)
    position = models.PositiveIntegerField(default=POSITION_STEP)
    user_id = models.IntegerField(db_index=True, null=True)
    subuser_id = models.IntegerField(db_index=True, null=True)
    
    class MPTTMeta:
        order_insertion_by = ["position"]
```



### 使用介绍

```
1：将epub_categories 注册到settings文件的INSTALLED_APPS列表内
2：将公共分类路由添加到需要使用分类功能的内容模块的路由中
urlpatterns = [
    re_path(
        "categories/",
        include(
            ("epub.apps.epub_categories.urls", "epub_categories"),
            namespace="epub_categories",
        ),
        {
            "category_type": "h5",
            "app_name": "books",
            "model_name": "Book",
            "user_filter": ["user_id", "subuser_id"],
            "order_by": "position",
        },
    ),
]
参数说明：
	category_type： 用于指定分类的类型
	app_name：应用名，如：epub_books
	model_name: 模型名， 如：Book
	user_filter: 筛选列表， 如果传user_id或subuser_id 则获取分类列表信息的时候会根据当前请求的user_id或subuser_id进行筛选
    order_by: 排序字段， 默认按照 position 排序，可配置 "-position" 倒序排列

3：为内容模块的models添加字段
例：
models.py

from epub.apps.epub_categories.models.category import Category

class Book(models.Model):
	categories = models.ManyToManyField(
        Category, related_name="book_set", default=models.CASCADE
    )

4：添加筛选信息(可选)
本模块提供根据category_id 筛选内容信息功能，可自行引用
将ContentCategoryFilterBackend添加到filter_backends中即可。
例：
views.py
from epub.apps.epub_categories.views.filters import ContentCategoryFilterBackend

class BookListAPIView(generics.ListAPIView):
	filter_backends = [ContentCategoryFilterBackend]





```



### API介绍

```
API介绍：
'categories/'	创建公共分类、获取分类列表
创建分类：
	入参：parent	  父节点id
		 title		标题

'categories/<pk>/'	获取分类详情、修改分类、删除分类
修改分类：
	入参：title	  标题
	
'categories/sort/'	修改分类排序
排序分类：
	入参：target	  目标节点id
		 before     排序后目标节点前id
		 after      排序后目标节点后id
		 parent     父节点id
		 
'categories/batch/'	批量给内容添加分类
	入参：content_ids    内容id
	     category_ids   分类id
	功能：批量将content_ids中的内容分类信息修改为category_ids
```

