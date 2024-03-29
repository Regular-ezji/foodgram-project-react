# Generated by Django 3.2 on 2023-08-17 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название ингридиента', max_length=200, verbose_name='Название ингридиента')),
                ('amount', models.SmallIntegerField(blank=True, help_text='Количество конкретного ингридиента на одно блюдо', null=True, verbose_name='Количество конкретного ингридиента на одно блюдо')),
                ('unit', models.CharField(help_text='Единица измерения', max_length=150, verbose_name='Единица измерения')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название рецепта', max_length=200, verbose_name='Название рецепта')),
                ('image', models.ImageField(help_text='Фотография блюда', upload_to='recipes/', verbose_name='Фото блюда')),
                ('text', models.CharField(max_length=1000)),
                ('cooking_time', models.SmallIntegerField(help_text='Время приготовления, мин.', verbose_name='Время приготовления, мин.')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Ключевое слово', max_length=200, verbose_name='Ключевое слово')),
                ('hex', models.CharField(default='#ffffff', help_text='HEX код цвета', max_length=7, verbose_name='HEX код цвета')),
                ('slug', models.SlugField(help_text='Сокращенное название тега для включения в URL-адрес', unique=True, verbose_name='Сокращенное название тега для включения в URL-адрес')),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ShoppingCartRecipe', to='recipes.recipe', verbose_name='Рецепт')),
            ],
        ),
    ]
