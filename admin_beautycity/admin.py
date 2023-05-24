from django.contrib import admin
from .models import Client, Schedule, Service
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'tg_account')
    search_fields = ['name', 'phone', 'tg_account']  # надо реализовать поиск без учета регистра!!!

    class Meta:
        ordering = ('name', )

    # разобраться с этим позже - что за функционал?
    def my_unicode(self):
        return 'what ever you want to return'
    Client.__unicode__ = my_unicode


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'cost')
    search_fields = ['service_name', ]


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'reception_datetime', 'client', 'service', 'incognito_phone')
    list_filter = ('specialist', ('reception_datetime', DateRangeFilter))

    class Meta:
        ordering = ('reception_datetime', 'specialist', )  # почему то сортирует по времени, а не дате-времени!!!


admin.site.site_header = 'Панель администратора'
admin.site.site_title = '"Салон BeautyCity"'
admin.site.index_title = 'Доступные разделы:'
