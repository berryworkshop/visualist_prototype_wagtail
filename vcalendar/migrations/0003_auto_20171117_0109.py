# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-17 01:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vcalendar', '0002_auto_20171117_0106'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EventIndexPage',
            new_name='EventIndex',
        ),
    ]