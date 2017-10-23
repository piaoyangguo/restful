利用Django实现RESTful API(一)
　　RESTful API现在很流行，这里是它的介绍 理解RESTful架构和 RESTful API设计指南.按照Django的常规方法当然也可以实现REST，但有一种更快捷、强大的方法，那就是 Django REST framework.它是python的一个模块，通过在Django里面配置就可以把app的models中的各个表实现RESTful API。下面是实现方法：

一、安装配置

pip install djangorestframework
pip install markdown       # Markdown support for the browsable API.
pip install django-filter  # Filtering support
再到Django的 settings.py 中的INSTALLED_APPS添加 rest_framework，如下：

1
2
3
4
INSTALLED_APPS = (
    ...
    'rest_framework',
)
 在根目录的 url.py 文件中为rest_framework框架的 login 和 logout 视图添加url：

1
2
3
4
urlpatterns = [
    ...
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]


二、创建model和Serializer

创建app，名为 snippets.。在视图 models.py 中添加一张表如下：

复制代码
from django.db import models
from pygments.lexers import get_all_lexers         # 一个实现代码高亮的模块
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS]) # 得到所有编程语言的选项
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())     # 列出所有配色风格


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

    class Meta:
        ordering = ('created',)
复制代码
然后开始同步到数据库中：

./manage.py makemigrations snippets
./manage.py migrate
接下来需要做的就是创建 Serializer 类，类似于 Form。它的作用就是从你传入的参数中提取出你需要的数据，并把它转化为 json 格式(注意，已经是字节码了),同时支持反序列化到model对象。在 snippets 文件夹中添加 serializers.py 并在其添加如下：

按 Ctrl+C 复制代码

from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES


class SnippetSerializer(serializers.Serializer):                # 它序列化的方式很类似于Django的forms
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={'base_template': 'textarea.html'})      # style的设置等同于Django的widget=widgets.Textarea
    linenos = serializers.BooleanField(required=False)                          # 用于对浏览器的上的显示
    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
    style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Snippet.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.code = validated_data.get('code', instance.code)
        instance.linenos = validated_data.get('linenos', instance.linenos)
        instance.language = validated_data.get('language', instance.language)
        instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance
按 Ctrl+C 复制代码


三、使用Serializer

先使用 ./manage.py shell 进入Django的shell中。操作如下：



可以看到 Serializer 的使用如同 Django 的 forms.它的反序列化如下：

from django.utils.six import BytesIO

stream = BytesIO(content)
data = JSONParser().parse(stream)
这是再把得到的数据转化为实例：

复制代码
serializer = SnippetSerializer(data=data)
serializer.is_valid()    # 开始验证
# True
serializer.validated_data
# OrderedDict([('title', ''), ('code', 'print "hello, world"\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')])
serializer.save()
# <Snippet: Snippet object>
复制代码
同时，我们还可以对 querysets 进行序列化，只需简单地在设置参数 many=True，如下：

serializer = SnippetSerializer(Snippet.objects.all(), many=True)
serializer.data
# [OrderedDict([('id', 1), ('title', u''), ('code', u'foo = "bar"\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')]), OrderedDict([('id', 2), ('title', u''), ('code', u'print "hello, world"\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')]), OrderedDict([('id', 3), ('title', u''), ('code', u'print "hello, world"'), ('linenos', False), ('language', 'python'), ('style', 'friendly')])


四、使用 ModelSerializer

ModelSerializer类似于Django的 modelform， 可以直接关联到models中的表。如下：

class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ('id', 'title', 'code', 'linenos', 'language', 'style')


五、在Django的视图中使用Serializer

首先，可以像常规Django视图的写法一样写，返回序列化的输出数据。

复制代码
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer


@csrf_exempt
def snippet_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
复制代码
也可以写一个视图对应其models中的表，实现对它的删、改、查。

复制代码
@csrf_exempt
def snippet_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = Snippet.objects.get(pk=pk)
    except Snippet.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = SnippetSerializer(snippet)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        snippet.delete()
        return HttpResponse(status=204)
复制代码
添加对应的url, snippets/urls.py 中设置如下：

复制代码
from django.conf.urls import url
from snippets import views

urlpatterns = [
    url(r'^snippets/$', views.snippet_list),
    url(r'^snippets/(?P<pk>[0-9]+)/$', views.snippet_detail),
]
复制代码
最后还要在根目录的 url.py 中添加对应的映射。

urlpatterns = [　　
　　...
    url(r'^', include('snippets.urls')),
]
这时，所有的配置已经完成了。接下来就是测试我们的API

六、测试API

为了方便我们可以使用 httpie 模块来测试，启动Django，再在客户端输入 http://127.0.0.1:8000/snippets/,操作如下：



 还可以进行 put 操作，修改对应的内容



如此简单。。。。。。。
http://www.cnblogs.com/zhouyang123200/p/6606405.html