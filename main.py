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
async def start_conversation(msg: types.Message):
    message = dedent("""  Добро пожаловать! 
    Салон красоты BeautyCity – это не только высокопрофессиональные услуги, но и уютный салон, \
     в котором всегда рады гостям. 
    Безупречность в работе и творческий подход, внимательные мастера учтут и воплотят все Ваши пожелания!""")
    await msg.answer(dedent(message))
    records_number = await sync_to_async(funcs.get_records_number)(msg.from_user.username)
    if records_number:
        await msg.answer(f'С возвращением, {msg.from_user.first_name}. У Вас уже было {records_number} записей.')
    else:
        await msg.answer(f'Здравствуйте, {msg.from_user.first_name}')
    await msg.answer('Главное меню', reply_markup=m.client_start_markup)


@dp.callback_query_handler(text="exit", state=[UserState, None])
async def exit_client_proceeding(cb: types.CallbackQuery):
    await cb.message.delete()
    await cb.message.answer('Главное меню', reply_markup=m.client_start_markup)
    await cb.answer()


@dp.callback_query_handler(Text('get_service'), state=[UserState, None])
async def service_choosing(cb: types.CallbackQuery):
    await cb.message.delete()
    await cb.message.answer('Выбор сервиса', reply_markup=m.get_service)
    await UserState.datetime.set()
    await cb.answer()


# надо реализовать автоматическую выборку вторых значений сюда в Text из Service.objects.all()
# [service for service in Service.objects.all()]
# ['meikap', 'hair_coloring', 'manicure']
@dp.callback_query_handler(Text(['meikap', 'hair_coloring', 'manicure']),
                           state=UserState.datetime)
async def set_service(cb: types.CallbackQuery, state: FSMContext):
    # await sync_to_async(print)(cb.data)
    # service = await sync_to_async(Service.objects.filter)(service_english=cb.data)
    # service_id = await sync_to_async(print)(service[0].service_english)
    # service_id_id = await sync_to_async(print)(service_id[0])
    # await sync_to_async(print)(service_id)
    # await state.update_data(service_id=service)
    await cb.message.delete()
    await cb.message.answer('Выбор даты и времени', reply_markup=m.choose_datetime)

    await UserState.registration.set()
    await cb.answer()


@dp.callback_query_handler(Text(['today', 'tomorrow']), state=UserState.registration)
async def set_datetime(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()

    # клиент зарегистрирован? проверка и далее - флаг и запрос номера телефона

    # если не зарегистрирован
    chat_id = cb.from_user.id
    await cb.message.answer('Предлагаем Вам зарегистрироваться в нашей базе. Получите скидку 5%.')
    await cb.message.answer('Для регистрации ознакомьтесь с согласием на обработку персональных данных.')
    await bot.send_document(chat_id=chat_id, document=open(Path(BASE_DIR, 'permitted.pdf'), 'rb'),
                            reply_markup=m.accept_personal_data)
    await UserState.name.set()
    await cb.answer()


@dp.callback_query_handler(Text(['personal_yes', 'personal_no']), state=UserState.name)
async def accepting_permission(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    if cb.data == 'personal_no':
        registration_consent = False
        await cb.message.answer('Жаль. Но для связи с Вами нам необходимы Ваши имя и телефон.')
    else:
        registration_consent = True
    await cb.message.answer('Введите свое имя:')
    await UserState.phone.set()
    await state.update_data(registration_consent=registration_consent)
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

    data = await state.get_data()
    if data['registration_consent']:
        # сохранение юзера в БД
        name = data['name']
        phone = msg.text  # СДЕЛАТЬ ПРОВЕРКУ ТЕЛЕФОНА и перевод в формат 164
        await sync_to_async(funcs.registration_client)(name, phone, msg.from_user.username, msg.from_user.id)
    # сохранение записи о визите в БД ...

    await msg.answer(f'Спасибо, Вы записаны! До встречи ДД.ММ ЧЧ:ММ по адресу: МО, Балашиха, штабс DEVMAN”')
    await msg.answer('Главное меню', reply_markup=m.client_start_markup)
    # await UserState.cls()


@dp.message_handler(state=[UserState.standby])
async def incorrect_input_proceeding(msg: types.Message):
    await msg.answer('Главное меню', reply_markup=m.client_start_markup)


# ======= CLIENT BLOCK (END) ============================================================================


async def sentinel():
    while 1:
        # print(sys.path)
        logging.info('Какая то проверка в течении какого то периода')
        await asyncio.sleep(86400)


async def on_startup(_):
    asyncio.create_task(sentinel())

executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
