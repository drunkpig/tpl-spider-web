# Generated by Django 2.1 on 2019-04-04 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='spidertask',
            name='to_framework',
            field=models.CharField(default='utf-8', max_length=16),
        ),
    ]
