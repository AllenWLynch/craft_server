# Generated by Django 2.2.3 on 2019-07-21 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('craftapp', '0006_auto_20190719_2306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='mod',
        ),
        migrations.DeleteModel(
            name='Mod',
        ),
    ]
