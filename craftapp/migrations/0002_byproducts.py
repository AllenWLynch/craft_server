# Generated by Django 2.2.3 on 2019-07-16 05:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('craftapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ByProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('quantity', models.IntegerField(default=1)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='craftapp.Recipe')),
            ],
        ),
    ]
