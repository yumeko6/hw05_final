# Generated by Django 2.2.16 on 2022-03-12 08:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0015_auto_20220310_1652'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='follow_unique',
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set(),
        ),
    ]
