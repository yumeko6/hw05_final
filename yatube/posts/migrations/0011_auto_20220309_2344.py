# Generated by Django 2.2.16 on 2022-03-09 20:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20220309_2343'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='follow_unique',
        ),
    ]
