from django.contrib import admin
from .models import Owner, Client, Order, Schedule, Service


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('tg_account', 'name',)  # 'phone')
    search_fields = ['tg_account', 'name',]  # 'phone']

    class Meta:
        ordering = ('tg_account', )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'cost')


admin.site.register(Owner)
admin.site.register(Order)
admin.site.register(Schedule)


admin.site.site_header = 'Панель администратора'
admin.site.site_title = '"Салон BeautyCity"'
admin.site.index_title = 'Доступные разделы:'
