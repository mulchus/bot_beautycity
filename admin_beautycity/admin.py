import pytz

from django.contrib import admin
from django_object_actions import DjangoObjectActions, action
from rangefilter.filters import DateTimeRangeFilter
from datetime import datetime, date, time, timedelta
from .models import Client, Schedule, Service, Specialist


EIGHT_HOURS = time(8, 0, 0)
THIRTY_MINUTES = timedelta(0, 1800)


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ['name', 'phone']  # надо реализовать поиск без учета регистра!!!


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'tg_account')
    search_fields = ['name', 'phone', 'tg_account']

    class Meta:
        ordering = ('name', )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')
    search_fields = ['name', ]


def schedule_set_day(set_day):
    specialists = Specialist.objects.all()
    for specialist in specialists:
        next_datetime = datetime.combine(set_day, EIGHT_HOURS)
        for reception in range(24):
            Schedule.objects.get_or_create(specialist=specialist, reception_datetime=next_datetime)
            next_datetime += THIRTY_MINUTES


@admin.register(Schedule)
class ScheduleAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('specialist', 'reception_datetime', 'client', 'service', 'incognito_phone', 'payed')
    list_filter = ('specialist', 'service', ('reception_datetime', DateTimeRangeFilter))
    ordering = ('reception_datetime', )

    @action(label='Schedule next day', description='For all specialists, starting with the following '
                                                   'after the last date')
    def schedule_next_day(self, request, obj):
        last_shedule = Schedule.objects.all().order_by('-reception_datetime', 'pk')[0]
        schedule_set_day(last_shedule.reception_datetime + timedelta(1))

    @action(label='Paint tomorrow', description='According to all experts, tomorrows date')
    def schedule_tomorrow(self, request, obj):
        schedule_set_day(date.today() + timedelta(1))

    @action(label='Paint today', description='According to all experts, todays date')
    def schedule_today(self, request, obj):
        schedule_set_day(date.today())

    changelist_actions = ('schedule_next_day', 'schedule_tomorrow', 'schedule_today', )


admin.site.site_header = 'Admin panel'
admin.site.site_title = '"Saloon BeautyCity"'
admin.site.index_title = 'Available sections:'
