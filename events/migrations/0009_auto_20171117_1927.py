# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-17 19:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_auto_20171117_1910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='organizers',
            field=models.ManyToManyField(blank=True, to='names.Name'),
        ),
    ]