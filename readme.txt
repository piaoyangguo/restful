����Djangoʵ��RESTful API(һ)
����RESTful API���ں����У����������Ľ��� ���RESTful�ܹ��� RESTful API���ָ��.����Django�ĳ��淽����ȻҲ����ʵ��REST������һ�ָ���ݡ�ǿ��ķ������Ǿ��� Django REST framework.����python��һ��ģ�飬ͨ����Django�������þͿ��԰�app��models�еĸ�����ʵ��RESTful API��������ʵ�ַ�����

һ����װ����

pip install djangorestframework
pip install markdown       # Markdown support for the browsable API.
pip install django-filter  # Filtering support
�ٵ�Django�� settings.py �е�INSTALLED_APPS��� rest_framework�����£�

1
2
3
4
INSTALLED_APPS = (
    ...
    'rest_framework',
)
 �ڸ�Ŀ¼�� url.py �ļ���Ϊrest_framework��ܵ� login �� logout ��ͼ���url��

1
2
3
4
urlpatterns = [
    ...
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]


��������model��Serializer

����app����Ϊ snippets.������ͼ models.py �����һ�ű����£�

���ƴ���
from django.db import models
from pygments.lexers import get_all_lexers         # һ��ʵ�ִ��������ģ��
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS]) # �õ����б�����Ե�ѡ��
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())     # �г�������ɫ���


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

    class Meta:
        ordering = ('created',)
���ƴ���
Ȼ��ʼͬ�������ݿ��У�

./manage.py makemigrations snippets
./manage.py migrate
��������Ҫ���ľ��Ǵ��� Serializer �࣬������ Form���������þ��Ǵ��㴫��Ĳ�������ȡ������Ҫ�����ݣ�������ת��Ϊ json ��ʽ(ע�⣬�Ѿ����ֽ�����),ͬʱ֧�ַ����л���model������ snippets �ļ�������� serializers.py ������������£�

�� Ctrl+C ���ƴ���

from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES


class SnippetSerializer(serializers.Serializer):                # �����л��ķ�ʽ��������Django��forms
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={'base_template': 'textarea.html'})      # style�����õ�ͬ��Django��widget=widgets.Textarea
    linenos = serializers.BooleanField(required=False)                          # ���ڶ���������ϵ���ʾ
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
�� Ctrl+C ���ƴ���


����ʹ��Serializer

��ʹ�� ./manage.py shell ����Django��shell�С��������£�



���Կ��� Serializer ��ʹ����ͬ Django �� forms.���ķ����л����£�

from django.utils.six import BytesIO

stream = BytesIO(content)
data = JSONParser().parse(stream)
�����ٰѵõ�������ת��Ϊʵ����

���ƴ���
serializer = SnippetSerializer(data=data)
serializer.is_valid()    # ��ʼ��֤
# True
serializer.validated_data
# OrderedDict([('title', ''), ('code', 'print "hello, world"\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')])
serializer.save()
# <Snippet: Snippet object>
���ƴ���
ͬʱ�����ǻ����Զ� querysets �������л���ֻ��򵥵������ò��� many=True�����£�

serializer = SnippetSerializer(Snippet.objects.all(), many=True)
serializer.data
# [OrderedDict([('id', 1), ('title', u''), ('code', u'foo = "bar"\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')]), OrderedDict([('id', 2), ('title', u''), ('code', u'print "hello, world"\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')]), OrderedDict([('id', 3), ('title', u''), ('code', u'print "hello, world"'), ('linenos', False), ('language', 'python'), ('style', 'friendly')])


�ġ�ʹ�� ModelSerializer

ModelSerializer������Django�� modelform�� ����ֱ�ӹ�����models�еı����£�

class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ('id', 'title', 'code', 'linenos', 'language', 'style')


�塢��Django����ͼ��ʹ��Serializer

���ȣ������񳣹�Django��ͼ��д��һ��д���������л���������ݡ�

���ƴ���
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
���ƴ���
Ҳ����дһ����ͼ��Ӧ��models�еı�ʵ�ֶ�����ɾ���ġ��顣

���ƴ���
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
���ƴ���
��Ӷ�Ӧ��url, snippets/urls.py ���������£�

���ƴ���
from django.conf.urls import url
from snippets import views

urlpatterns = [
    url(r'^snippets/$', views.snippet_list),
    url(r'^snippets/(?P<pk>[0-9]+)/$', views.snippet_detail),
]
���ƴ���
���Ҫ�ڸ�Ŀ¼�� url.py ����Ӷ�Ӧ��ӳ�䡣

urlpatterns = [����
����...
    url(r'^', include('snippets.urls')),
]
��ʱ�����е������Ѿ�����ˡ����������ǲ������ǵ�API

��������API

Ϊ�˷������ǿ���ʹ�� httpie ģ�������ԣ�����Django�����ڿͻ������� http://127.0.0.1:8000/snippets/,�������£�



 �����Խ��� put �������޸Ķ�Ӧ������



��˼򵥡�������������
http://www.cnblogs.com/zhouyang123200/p/6606405.html