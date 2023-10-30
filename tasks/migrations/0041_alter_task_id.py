# Generated by Django 3.2.20 on 2023-10-30 11:17

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0040_auto_20230628_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]