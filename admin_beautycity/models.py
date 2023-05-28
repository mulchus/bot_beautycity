from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Client(models.Model):
    name = models.CharField('Name', max_length=20)
    phone = PhoneNumberField('Phone', max_length=15, null=True, blank=True, db_index=True)
    tg_account = models.CharField('Telegram account', null=True, blank=True, max_length=32)
    tg_id = models.IntegerField('Telegram ID', null=True, blank=True, unique=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f'{self.name} {self.phone}'

    def status(self):
        all_records = Schedule.objects.filter(client=self)
        return all_records


class Service(models.Model):
    name = models.CharField('Name', max_length=30)
    cost = models.FloatField('Cost')

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return f'{self.name} {self.cost}'


class Specialist(models.Model):
    name = models.CharField('Name', max_length=20)
    phone = PhoneNumberField('Phone', max_length=20, null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = 'Specialist'
        verbose_name_plural = 'Specialists'

    def __str__(self):
        return f'{self.name} {self.phone}'


class Schedule(models.Model):
    specialist = models.ForeignKey(Specialist, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Specialist', related_name='specialist_records')
    reception_datetime = models.DateTimeField('Date and time reception', db_index=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Client',
                               related_name='client_records')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Service',
                                related_name='service_records')
    incognito_phone = PhoneNumberField('Client phone (registration refusal)', max_length=20, null=True, blank=True,
                                       db_index=True)
    payed = models.BooleanField('Payed?', default=False)

    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'

    def __str__(self):
        return f'{self.specialist} {self.reception_datetime}'
