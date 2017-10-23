#coding: utf8
from django.db import models
from pygments.lexers import get_all_lexers         # 一个实现代码高亮的模块
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS]) # 得到所有编程语言的选项
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())     # 列出所有配色风格

#  Create your models here.
class Man(models.Model):
    name = models.CharField(u'姓名', max_length=200)
    age = models.IntegerField(u'年龄')

    class Meta:
        abstract = True

GRADE_CHOICE = (
    (u"1", u'一年级'),
    (u"2", u'二年级'),
)

class Student(Man):
    grade = models.CharField(u'年级', choices=GRADE_CHOICE, max_length=2, default=u"1")

class Teacher(Man):
    students = models.ManyToManyField(Student, blank=True, related_name='myteacher')