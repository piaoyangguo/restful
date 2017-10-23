from django.shortcuts import render
from .models import Teacher
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from snippets.models import Snippet
from snippets.Serializer import SnippetSerializer

# Create your views here.

def index(request):
    teachers = Snippet.objects.all()
    serializer = SnippetSerializer(teachers, many=True)
    return JsonResponse(serializer.data, safe=False)


def indexhtml(request):
    return render(request, 'index.html')