import datetime
import os
import dotenv
import requests
from urllib.parse import urlparse


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_beautycity.settings')
import django

django.setup()

from admin_beautycity.models import Client, Schedule, Service


dotenv.load_dotenv()


def get_records_number(tg_account: str):
    try:
        records_number = Client.objects.get(tg_account=tg_account)
        return records_number
    except Client.DoesNotExist:
        return


def registration_client(name, phone, tg_account, tg_id):
    Client.objects.create(name=name, phone=phone, tg_account=tg_account, tg_id=tg_id)


def make_order(schedule_id, tg_account, service, incognito_phone=''):
    client = Client.objects.get(tg_account=tg_account)
    Schedule.objects.filter(schedule_id=schedule_id).update(client=client, service=service,
                                                            incognito_phone=incognito_phone)


def get_client_records(tg_account, id_client=None):
    client = Client.objects.get(tg_account=tg_account)
    records = Schedule.objects.filter(client=client)
    serialized_orders = []
    for record in records:
        serialized_order = dict(client=tg_account, service=record.service, specialist=record.specialist,
                                reception_datetime=record.reception_datetime,
                                incognito_phone=record.incognito_phone)
        serialized_orders.append(serialized_order)
    return serialized_orders


def get_record(record_id):
    record = Schedule.objects.filter(id=record_id)[0]
    serialized_order = dict(client=record.client.tg_account, service=record.service, specialist=record.specialist,
                            reception_datetime=record.reception_datetime,
                            incognito_phone=record.incognito_phone)
    return serialized_order


# def get_service(service):
#     service = Service.objects.filter(id=record_id)[0]
#     serialized_order = dict(client=record.client.tg_account, service=record.service, specialist=record.specialist,
#                             reception_datetime=record.reception_datetime,
#                             incognito_phone=record.incognito_phone)
#     return serialized_order


def delete_order(id):
    tg_id = Schedule.objects.get(id=id).client.tg_id
    Schedule.objects.get(id=id).delete()
    return tg_id


def get_clients():
    clients = Client.objects.all()
    serialized_clients = []
    for client in clients:
        serialized_client = dict(name=client.name, phone=client.phone, client=client.tg_account, chat_id=client.tg_id,
                                 id=client.id)
        serialized_clients.append(serialized_client)
    return serialized_clients
