# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-07 04:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avs', '0002_auto_20160923_0953'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questions',
            name='Statement',
        ),
        migrations.AddField(
            model_name='questions',
            name='Constraints',
            field=models.CharField(default=10, max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='questions',
            name='InputFormat',
            field=models.CharField(default=1, max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='questions',
            name='OutputFormat',
            field=models.CharField(default=1, max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='questions',
            name='ProblemStatement',
            field=models.CharField(default=1, max_length=3500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='questions',
            name='SampleInput',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='questions',
            name='SampleOutput',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submission',
            name='Code',
            field=models.FileField(default=1, upload_to=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='questions',
            name='Name',
            field=models.CharField(max_length=50),
        ),
    ]