# Generated by Django 4.2.1 on 2023-05-28 21:47

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('admin_beautycity', '0003_schedule_payed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'verbose_name': 'Client', 'verbose_name_plural': 'Clients'},
        ),
        migrations.AlterModelOptions(
            name='schedule',
            options={'verbose_name': 'Schedule', 'verbose_name_plural': 'Schedules'},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'verbose_name': 'Service', 'verbose_name_plural': 'Services'},
        ),
        migrations.AlterModelOptions(
            name='specialist',
            options={'verbose_name': 'Specialist', 'verbose_name_plural': 'Specialists'},
        ),
        migrations.RemoveField(
            model_name='service',
            name='name_english',
        ),
        migrations.AlterField(
            model_name='client',
            name='name',
            field=models.CharField(max_length=20, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, max_length=15, null=True, region=None, verbose_name='Phone'),
        ),
        migrations.AlterField(
            model_name='client',
            name='tg_account',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Telegram account'),
        ),
        migrations.AlterField(
            model_name='client',
            name='tg_id',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='Telegram ID'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_records', to='admin_beautycity.client', verbose_name='Client'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='incognito_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, max_length=20, null=True, region=None, verbose_name='Client phone (registration refusal)'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='payed',
            field=models.BooleanField(default=False, verbose_name='Payed?'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='reception_datetime',
            field=models.DateTimeField(db_index=True, verbose_name='Date and time reception'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_records', to='admin_beautycity.service', verbose_name='Service'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='specialist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='specialist_records', to='admin_beautycity.specialist', verbose_name='Specialist'),
        ),
        migrations.AlterField(
            model_name='service',
            name='cost',
            field=models.FloatField(verbose_name='Cost'),
        ),
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(max_length=30, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='specialist',
            name='name',
            field=models.CharField(max_length=20, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='specialist',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, max_length=20, null=True, region=None, verbose_name='Phone'),
        ),
    ]
