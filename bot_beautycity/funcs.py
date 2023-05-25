import os
import dotenv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_beautycity.settings')
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
