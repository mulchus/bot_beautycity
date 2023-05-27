from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Client(models.Model):
    name = models.CharField('Имя', max_length=20)
    phone = PhoneNumberField('Телефон', max_length=15, null=True, blank=True, db_index=True)
    tg_account = models.CharField('Телеграм-Аккаунт', null=True, blank=True, max_length=32)
    tg_id = models.IntegerField('Телеграм-ID', null=True, blank=True, unique=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'{self.name} {self.phone}'

    def status(self):
        all_records = Schedule.objects.filter(client=self)
        return all_records


class Service(models.Model):
    name = models.CharField('Название', max_length=30)
    name_english = models.CharField('По_английски_через "_"', max_length=30, default=None)
    cost = models.FloatField('Стоимость')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return f'{self.name} {self.cost}'


class Specialist(models.Model):
    name = models.CharField('Имя специалиста', max_length=20)
    phone = PhoneNumberField('Телефон специалиста', max_length=20, null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = 'Специалист'
        verbose_name_plural = 'Специалисты'

    def __str__(self):
        return f'{self.name} {self.phone}'


class Schedule(models.Model):
    specialist = models.ForeignKey(Specialist, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Специалист', related_name='specialist_records')
    reception_datetime = models.DateTimeField('Дата и время приема', db_index=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Клиент',
                               related_name='client_records')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Услуга',
                                related_name='service_records')
    incognito_phone = PhoneNumberField('Телефон клиента (отказ регистрации)', max_length=20, null=True, blank=True,
                                       db_index=True)

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'

    def __str__(self):
        return f'{self.specialist} {self.reception_datetime}'
