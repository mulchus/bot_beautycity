import datetime

from django.db import models
# from phonenumber_field import PhoneNumberField


class Owner(models.Model):
    tg_account = models.CharField('owner telegram account', max_length=32, unique=True)
    tg_id = models.IntegerField('owner telegram_id for Bot', null=True, blank=True)

    def __str__(self):
        return f'owner {self.tg_account}'


class Client(models.Model):
    name = models.CharField('client name', max_length=20)
    # phone = PhoneNumberField('client phone ', max_length=20, null=True, blank=True, db_index=True)
    tg_account = models.CharField('client telegram account', max_length=32)
    tg_id = models.IntegerField('client telegram_id for Bot', null=True, blank=True, unique=True)
    
    def __str__(self):
        return f'{self.name} {self.tg_account}'

    def status(self):
        all_orders = Order.objects.filter(client=self)
        return all_orders


class Schedule(models.Model):
    specialist = models.CharField('specialist', max_length=20)
    datetime = models.DateTimeField('reception date and time', db_index=True)

    def __str__(self):
        return f'{self.specialist} {self.datetime}'


class Service(models.Model):
    service_type = models.CharField('service type', max_length=30)
    cost = models.FloatField('cost')


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='client',
                               related_name='client_orders')
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING, verbose_name='service',
                                related_name='service_orders')
    schedule = models.ForeignKey(Schedule, on_delete=models.DO_NOTHING, verbose_name='schedule',
                                 related_name='schedule_orders')
    # incognito_phone = PhoneNumberField('incognito phone ', max_length=20, null=True, blank=True, db_index=True)

    def __str__(self):
        if self.client:
            return f'{self.client.name} {self.client.tg_account}_{self.pk}'
        else:
            return \
                # f'{self.incognito_phone}_{self.pk}'
