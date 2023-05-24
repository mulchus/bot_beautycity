import os
import sys
import time

import dotenv
import asyncio
from bot_beautycity import funcs
from bot_beautycity import markups as m
import logging
import django.db.utils
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from asgiref.sync import sync_to_async
from pathlib import Path
from textwrap import dedent
from admin_beautycity.models import Client, Schedule, Service


BASE_DIR = Path(__file__).resolve().parent
dotenv.load_dotenv(Path(BASE_DIR, '.env'))
token = os.environ['BOT_TOKEN']

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
client_id = {}
qr_dic = {}


class UserState(StatesGroup):
    standby = State()
    service = State()
    datetime = State()
    registration = State()
    name = State()
    phone = State()
    record_save = State()


@dp.message_handler()
async def start_conversation(msg: types.Message, state: FSMContext):
    messages_responses = []
    message = dedent("""  Добро пожаловать! 
    Салон красоты BeautyCity – это не только высокопрофессиональные услуги, но и уютный салон, \
     в котором всегда рады гостям. 
    Безупречность в работе и творческий подход, внимательные мастера учтут и воплотят все Ваши пожелания!""")
    messages_responses.append(await msg.answer(dedent(message)))
    records_count = await sync_to_async(funcs.get_records_count)(msg.from_user.username)
    if records_count:
        message = await msg.answer(f'С возвращением, {msg.from_user.first_name}. '
                                    f'У Вас уже было записей: {records_count}.')
    else:
        message = await msg.answer(f'Здравствуйте, {msg.from_user.first_name}.')
    messages_responses.append(message)
    await msg.answer('Главное меню', reply_markup=m.client_start_markup)
    await state.update_data(messages_responses=messages_responses)


@dp.callback_query_handler(text="exit", state=[UserState, None])
async def exit_client_proceeding(cb: types.CallbackQuery):
    await cb.message.delete()
    await cb.message.answer('Главное меню', reply_markup=m.client_start_markup)
    await cb.answer()


@dp.callback_query_handler(Text('get_service'), state=[UserState, None])
async def service_choosing(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    try:
        messages_responses = await state.get_data('messages_responses')
        await sync_to_async(print)(messages_responses)
        for message in messages_responses['messages_responses']:
            await message.delete()
        await state.update_data(messages_responses=[])
        await sync_to_async(print)(messages_responses)
    except TypeError:
        pass
    await cb.message.answer('Выбор сервиса', reply_markup=m.get_service)
    await UserState.datetime.set()
    await cb.answer()


@dp.callback_query_handler(Text([service for service in Service.objects.all().values_list('service_english', flat=True)]),
                           state=UserState.datetime)
async def set_service(cb: types.CallbackQuery, state: FSMContext):
    await state.update_data(user_id=cb.from_user.id)  # сохраняем ID кто кликнул
    # await sync_to_async(print)(f'Выбор сделал {cb.from_user.username} {cb.from_user.id}')
    async for service in Service.objects.filter(service_english=cb.data):  # результат - одно значение!
        # await sync_to_async(print)(service.pk)
        await state.update_data(service_id=service.pk)
    await cb.message.delete()
    messages_responses = await state.get_data('messages_responses')
    # await sync_to_async(print)(f'НОВОЕ {messages_responses}')
    # messages_responses = data['messages_responses']
    messages_responses['messages_responses'].append(await cb.message.answer(f'Услуга "{service.service_name}" стоит {service.cost} руб.'))

                                        # ЗДЕСЬ НАДО ВСТАВИТЬ ВЫБОР ИЗ КАЛЕНДАРЯ!
    await cb.message.answer('Выбор даты и времени', reply_markup=m.choose_datetime)
    await UserState.registration.set()
    await cb.answer()

# ЗДЕСЬ НАДО ВСТАВИТЬ ВЫБОР ИЗ КАЛЕНДАРЯ!
@dp.callback_query_handler(Text(['today', 'tomorrow']), state=UserState.registration)
async def set_datetime(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    payloads = await state.get_data()
    for message in payloads['messages_responses']:
        await message.delete()
    if not sync_to_async(funcs.get_client_id)(payloads['user_id']):
    # Client.objects.filter(tg_id=payloads['user_id']):
        # await sync_to_async(print)(f'Клиент {client}')
        # клиент зарегистрирован? проверка и далее - флаг и запрос номера телефона
        # если не зарегистрирован
        await state.update_data(client_registered=False)
        # chat_id = cb.from_user.id
        # messages_responses = data['messages_responses']

        payloads['messages_responses'].append(await cb.message.answer('Предлагаем Вам зарегистрироваться в нашей базе. '
                                                                  'Получите скидку 5%.'))

        await cb.message.answer('Для регистрации ознакомьтесь с согласием на обработку персональных данных.')
        await bot.send_document(chat_id=chat_id, document=open(Path(BASE_DIR, 'permitted.pdf'), 'rb'),
                                reply_markup=m.accept_personal_data)
    await UserState.name.set()
    await cb.answer()


@dp.callback_query_handler(Text(['personal_yes', 'personal_no']), state=UserState.name)
async def accepting_permission(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    payloads = await state.get_data()
    for message in payloads['messages_responses']:
        await message.delete()

    if cb.data == 'personal_no':
        registration_consent = False
        await cb.message.answer('Жаль. Но для связи с Вами нам необходимы Ваши имя и телефон.')
    else:
        registration_consent = True
    await state.update_data(registration_consent=registration_consent)
    await cb.message.answer('Введите свое имя:')
    await UserState.phone.set()
    await cb.answer()


@dp.message_handler(lambda msg: msg.text, state=UserState.phone)
async def set_phone(msg: types.Message, state: FSMContext):
    # сохранение имени в памяти
    await state.update_data(name=msg.text)
    await msg.answer('Введите свой телефон. Номер телефона необходимо ввести в формате: "+99999999999". '
                     'Допускается до 15 цифр.')
    await UserState.record_save.set()


@dp.message_handler(lambda msg: msg.text, state=UserState.record_save)
async def incorrect_phone(msg: types.Message, state: FSMContext):
    if not msg.text:  # .is_valid():
        await msg.answer('Некорректно введен телефон! Попробуйте еще раз.')
        await set_phone()

    payloads = await state.get_data()
    if payloads['registration_consent']:
        # сохранение юзера в БД
        name = payloads['name']
        phone = msg.text  # СДЕЛАТЬ ПРОВЕРКУ ТЕЛЕФОНА и перевод в формат 164
        await sync_to_async(funcs.registration_client)(name, phone, msg.from_user.username, msg.from_user.id)
    # сохранение записи о визите в БД ...

    await msg.answer(f'Спасибо, Вы записаны! До встречи ДД.ММ ЧЧ:ММ по адресу: МО, Балашиха, штабс DEVMAN”')
    await msg.answer('Главное меню', reply_markup=m.client_start_markup)
    # await UserState.cls()


@dp.message_handler(state=[UserState.standby])
async def incorrect_input_proceeding(msg: types.Message):
    await msg.answer('Главное меню', reply_markup=m.client_start_markup)


@dp.callback_query_handler(text="call_to_us", state=['*'])
async def call_to_us_message(cb: types.CallbackQuery):
    await cb.message.answer('Рады Вашему звонку в любое время – 88005553535')


async def sentinel():
    while 1:
        # print(sys.path)
        logging.info('Какая то проверка в течении какого то периода')
        await asyncio.sleep(86400)


async def on_startup(_):
    asyncio.create_task(sentinel())

executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
