import os
from datetime import datetime, timedelta

import dotenv
import django
from aiogram import types

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_beautycity.settings')
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from admin_beautycity.models import Client, Schedule

dotenv.load_dotenv()


def get_records_count(tg_account):
    try:
        client = Client.objects.get(tg_account=tg_account)
        records = client.client_records.count()
        return records
    except Client.DoesNotExist:
        return


def get_client_id(tg_account):
    try:
        client = Client.objects.get(tg_account=tg_account)
        return client.pk
    except Client.DoesNotExist:
        return


def registration_client(name, phone, tg_account, tg_id):
    try:
        client = Client.objects.create(
            name=name,
            phone=phone,
            tg_account=tg_account,
            tg_id=tg_id
        )
        return client
    except django.db.utils.IntegrityError:
        pass


def make_order(full_schedule_date, specialist_id, client_id,
               service_id,
               incognito_phone=''):
    sc = Schedule.objects.filter(
        reception_datetime=full_schedule_date,
        specialist=specialist_id
    )
    sc.update(
        client=client_id,
        service=service_id,
        incognito_phone=incognito_phone
    )
    return sc[0].pk


def get_datetime(date, specialist):
    schedule = Schedule.objects.filter(
        reception_datetime__date=datetime(date.year, date.month, date.day),
        specialist=specialist,
        service__isnull=False
    )

    start_hour = 8
    start_time = datetime(date.year, date.month, date.day, start_hour, 0, 0)
    order_dates = []
    dates = []
    delta = timedelta(minutes=30)
    for i in range(24):
        z = start_time + i * delta
        order_dates.append(z)
    for sc in schedule:
        slot = (2
                * (sc.reception_datetime.hour - start_time.hour)
                + (sc.reception_datetime.minute)//30)
        order_dates[slot] = 0
    markup = types.InlineKeyboardMarkup(row_width=4)
    possible_time = []
    index = 0
    for i, order in enumerate(order_dates):
        if order != 0:
            if i % 2:
                minutes = '30'
            else:
                minutes = '00'
            time_window = f'{8 + i // 2} : {minutes}'
            dates.append(order)

            possible_time.append(types.InlineKeyboardButton(
                time_window,
                callback_data=f'Possible time windows {index}'
            ))
            index += 1
    test_filled_schedule = Schedule.objects.filter(
        reception_datetime__date=datetime(date.year, date.month, date.day),
        specialist=specialist)
    if not test_filled_schedule:
        dates = []
    markup.add(*possible_time)
    return markup, dates


def pay_order(schedule_id):
    Schedule.objects.filter(id=schedule_id).update(payed=True)
