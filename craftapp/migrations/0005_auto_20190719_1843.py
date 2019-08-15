# Generated by Django 2.2.3 on 2019-07-19 23:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('craftapp', '0004_auto_20190719_0730'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mod_id', models.CharField(max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='item',
            name='mod',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='craftapp.Mod'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='aliases',
            field=models.ManyToManyField(blank=True, related_name='_machine_aliases_+', to='craftapp.Machine'),
        ),
    ]