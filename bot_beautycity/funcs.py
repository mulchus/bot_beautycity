import os
import dotenv
import django
from datetime import datetime, timedelta

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
        client = Client.objects.create(name=name, phone=phone, tg_account=tg_account, tg_id=tg_id)
        return client
    except django.db.utils.IntegrityError:
        pass


def make_order(schedule_id, client_id, service_id, incognito_phone=''):
    Schedule.objects.filter(id=schedule_id).update(client=client_id, service=service_id,
                                                   incognito_phone=incognito_phone)

def get_datetime(date):
    schedule = Schedule.objects.filter(reception_datetime__date=datetime(date.year, date.month, date.day))
    start_hour = 8
    start_time = datetime(date.year, date.month, date.day, start_hour, 0, 0)
    k = []
    delta = timedelta(minutes=30)
    for i in range(24):
        z = start_time + i * delta
        k.append(z)
    for sc in schedule:
        slot = 2 * (sc.reception_datetime.hour - start_time.hour) + (sc.reception_datetime.minute)//30
        k[slot] = 0
    return k


def pay_order(schedule_id):
    Schedule.objects.filter(id=schedule_id).update(payed=True)
