# Generated by Django 3.2 on 2023-08-17 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='hex',
            new_name='color',
        ),
    ]
