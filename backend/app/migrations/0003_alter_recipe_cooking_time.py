# Generated by Django 4.1.5 on 2023-01-24 20:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(help_text='Укажите время в минутах', validators=[django.core.validators.MinValueValidator(1, message='Время должно быть больше/равно 1')], verbose_name='Время приготовления'),
        ),
    ]
