# Generated by Django 2.2.3 on 2019-07-19 12:30

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('craftapp', '0003_recipe_max_stack'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='Item Name')),
                ('mod', models.CharField(max_length=200, verbose_name='Mod')),
                ('max_stack', models.IntegerField(default=64, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(64)], verbose_name='Stack Size')),
            ],
        ),
        migrations.AlterModelOptions(
            name='byproducts',
            options={'verbose_name': 'Byproduct', 'verbose_name_plural': 'Byproducts'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'verbose_name': 'Recipe', 'verbose_name_plural': 'Recipes'},
        ),
        migrations.AlterModelOptions(
            name='slotdata',
            options={'verbose_name': 'Slot Data', 'verbose_name_plural': 'Slot Data'},
        ),
        migrations.RemoveField(
            model_name='byproducts',
            name='name',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='has_byproducts',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='max_stack',
        ),
        migrations.RemoveField(
            model_name='slotdata',
            name='slot',
        ),
        migrations.AddField(
            model_name='slotdata',
            name='slots',
            field=models.CharField(default='1', max_length=100, validators=[django.core.validators.int_list_validator], verbose_name='Slots'),
        ),
        migrations.AlterField(
            model_name='byproducts',
            name='quantity',
            field=models.IntegerField(blank=True, default=1, verbose_name='Quantity'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='is_shapeless',
            field=models.BooleanField(default=False, verbose_name='Shapless recipe'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='machine_with',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='craftapp.Machine', verbose_name='Machine'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='makes',
            field=models.IntegerField(default=1, verbose_name='Makes'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='recipe_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='craftapp.Item', verbose_name='Recipe For'),
        ),
        migrations.AlterField(
            model_name='slotdata',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='craftapp.Item', verbose_name='Item'),
        ),
        migrations.AlterField(
            model_name='slotdata',
            name='quantity',
            field=models.IntegerField(default=1, verbose_name='Quantity Per Slot'),
        ),
        migrations.AddField(
            model_name='byproducts',
            name='item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='craftapp.Item', verbose_name='Item'),
        ),
    ]
