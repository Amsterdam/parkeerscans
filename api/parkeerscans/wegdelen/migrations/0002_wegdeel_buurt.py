# Generated by Django 2.1.7 on 2019-06-25 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wegdelen', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='wegdeel',
            name='buurt',
            field=models.CharField(db_index=True, max_length=4, null=True),
        ),
    ]
