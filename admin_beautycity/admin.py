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
    search_fields = ['name', 'phone', 'tg_account']  # надо реализовать поиск без учета регистра!!!

    class Meta:
        ordering = ('name', )

    # разобраться с этим позже - что за функционал?
    @staticmethod
    def my_unicode():
        return 'what ever you want to return'
    Client.__unicode__ = my_unicode


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')
    search_fields = ['name', ]


def schedule_set_day(set_day):
    specialists = Specialist.objects.all()
    for specialist in specialists:
        next_datetime = datetime.combine(set_day, EIGHT_HOURS, tzinfo=pytz.timezone('Europe/Moscow'))
        for reception in range(24):
            Schedule.objects.get_or_create(specialist=specialist, reception_datetime=next_datetime)
            next_datetime += THIRTY_MINUTES


@admin.register(Schedule)
class ScheduleAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('specialist', 'reception_datetime', 'client', 'service', 'incognito_phone')
    list_filter = ('specialist', 'service', ('reception_datetime', DateTimeRangeFilter))
    ordering = ('reception_datetime', )

    @action(label='Расписать последующий день', description='По всем специалистам, начиная со следующей '
                                                          'после последней даты')
    def schedule_next_day(self, request, obj):
        last_shedule = Schedule.objects.all().order_by('-reception_datetime', 'pk')[0]
        schedule_set_day(last_shedule.reception_datetime + timedelta(1))

    @action(label='Расписать завтрашний день', description='По всем специалистам, завтрашней датой')
    def schedule_tomorrow(self, request, obj):
        schedule_set_day(date.today() + timedelta(1))

    @action(label='Расписать сегодняшний день', description='По всем специалистам, сегодняшней датой')
    def schedule_today(self, request, obj):
        schedule_set_day(date.today())

    changelist_actions = ('schedule_next_day', 'schedule_tomorrow', 'schedule_today', )


admin.site.site_header = 'Панель администратора'
admin.site.site_title = '"Салон BeautyCity"'
admin.site.index_title = 'Доступные разделы:'
