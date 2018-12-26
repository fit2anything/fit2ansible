# Generated by Django 2.1.2 on 2018-12-25 02:36

import common.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ansible_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adhocexecution',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Create time'),
        ),
        migrations.AlterField(
            model_name='adhocexecution',
            name='result_raw',
            field=common.models.JsonDictTextField(blank=True, default={}, null=True, verbose_name='Result raw'),
        ),
        migrations.AlterField(
            model_name='adhocexecution',
            name='result_summary',
            field=common.models.JsonDictTextField(blank=True, default={}, null=True, verbose_name='Result summary'),
        ),
        migrations.AlterField(
            model_name='playbookexecution',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Create time'),
        ),
        migrations.AlterField(
            model_name='playbookexecution',
            name='result_raw',
            field=common.models.JsonDictTextField(blank=True, default={}, null=True, verbose_name='Result raw'),
        ),
        migrations.AlterField(
            model_name='playbookexecution',
            name='result_summary',
            field=common.models.JsonDictTextField(blank=True, default={}, null=True, verbose_name='Result summary'),
        ),
    ]