import datetime
import os
import dotenv
import requests
from urllib.parse import urlparse


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_beautycity.settings')
import django

django.setup()

from admin_beautycity.models import Client, Order


dotenv.load_dotenv()


def get_records_number(tg_account: str):
    try:
        records_number = Client.objects.get(tg_account=tg_account)
        return records_number
    except Client.DoesNotExist:
        return


def registration_client(name, phone, tg_account, tg_id):
    Client.objects.create(name=name, phone=phone, tg_account=tg_account, tg_id=tg_id)


def make_order(tg_account, service, schedule, incognito_phone=''):
    client = Client.objects.get(tg_account=tg_account)
    Order.objects.create(client=client, service=service, schedule=schedule, incognito_phone=incognito_phone)


def get_client_orders(tg_account, id_client=None):
    client = Client.objects.get(tg_account=tg_account)
    orders = Order.objects.filter(client=client)
    serialized_orders = []
    for order in orders:
        serialized_order = dict(client=tg_account, service=service, schedule=schedule,
                                incognito_phone=incognito_phone)
        serialized_orders.append(serialized_order)
    return serialized_orders


def get_order(id_order):
    order = Order.objects.filter(id=id_order)[0]
    serialized_order = dict(client=order.client.tg_account, area=order.area, mass=order.mass,
                            amount=order.amount, date_opened=order.date_opened, date_closed=order.date_closed,
                            id=order.id)
    return serialized_order


def delete_order(id):
    tg_id = Order.objects.get(id=id).client.tg_id
    Order.objects.get(id=id).delete()
    return tg_id


def get_clients():
    clients = Client.objects.all()
    serialized_clients = []
    for client in clients:
        serialized_client = dict(name=client.name, phone=client.phone, client=client.tg_account, chat_id=client.tg_id,
                                 id=client.id)
        serialized_clients.append(serialized_client)
    return serialized_clients
