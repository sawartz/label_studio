# Generated by Django 3.2.20 on 2023-10-30 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0041_alter_task_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='id',
            field=models.AutoField(auto_created=True, db_index=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]