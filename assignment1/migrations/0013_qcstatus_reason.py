
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment1', '0012_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='qcstatus',
            name='reason',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
