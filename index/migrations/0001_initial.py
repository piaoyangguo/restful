# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u59d3\u540d')),
                ('age', models.IntegerField(verbose_name='\u5e74\u9f84')),
                ('grade', models.CharField(default='1', max_length=2, verbose_name='\u5e74\u7ea7', choices=[('1', '\u4e00\u5e74\u7ea7'), ('2', '\u4e8c\u5e74\u7ea7')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u59d3\u540d')),
                ('age', models.IntegerField(verbose_name='\u5e74\u9f84')),
                ('students', models.ManyToManyField(related_name='myteacher', to='index.Student', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
