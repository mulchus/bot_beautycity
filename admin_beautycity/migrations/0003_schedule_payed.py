# Generated by Django 4.2.1 on 2023-05-27 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_beautycity', '0002_alter_schedule_incognito_phone_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='payed',
            field=models.BooleanField(default=False, verbose_name='Оплачено?'),
        ),
    ]
