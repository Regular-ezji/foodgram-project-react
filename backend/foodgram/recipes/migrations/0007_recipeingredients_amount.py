# Generated by Django 3.2 on 2023-08-21 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_recipeingredients'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeingredients',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Количество'),
            preserve_default=False,
        ),
    ]
