# Generated by Django 3.2.19 on 2023-07-22 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment1', '0002_auto_20230721_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='assigned_to',
            field=models.IntegerField(),
        ),
    ]
