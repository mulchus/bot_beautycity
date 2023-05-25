import os

import dotenv
import asyncio
from bot_beautycity import funcs
from bot_beautycity import markups as m
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from asgiref.sync import sync_to_async
from pathlib import Path
from textwrap import dedent
from admin_beautycity.models import Client, Schedule, Service, Specialist
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException


BASE_DIR = Path(__file__).resolve().parent
dotenv.load_dotenv(Path(BASE_DIR, '.env'))
token = os.environ['BOT_TOKEN']

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)


class UserState(StatesGroup):
    standby = State()
    service = State()
    specialist = State()
    datetime = State()
    registration = State()
    name = State()
    phone = State()
    phone_verification = State()
    registration_completion = State()
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
async def exit_client_proceeding(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await cb.message.answer('Главное меню', reply_markup=m.client_start_markup)
    await state.reset_state(with_data=False)
    await cb.answer()


@dp.callback_query_handler(Text('get_service'), state=[UserState, None])
async def service_choosing(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    try:
        messages_responses = await state.get_data('messages_responses')
        for message in messages_responses['messages_responses']:
            await message.delete()
        await state.update_data(messages_responses=[])
    except TypeError:
        pass
    await cb.message.answer('Выбор сервиса:', reply_markup=m.get_service)
    await UserState.specialist.set()
    await cb.answer()


@dp.callback_query_handler(Text([service for service in
                                 Service.objects.all().values_list('name_english', flat=True)]),
                           state=UserState.specialist)
async def set_service(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await state.update_data(tg_id=cb.from_user.id)  # сохраняем tg_id кто кликнул

    async for service in Service.objects.filter(name_english=cb.data):  # результат - одно значение!
        await state.update_data(service_id=service.pk)
        await state.update_data(service_name=service.name)
    messages_responses = await state.get_data('messages_responses')
    messages_responses['messages_responses'].append(await cb.message.answer(f'Услуга "{service.name}" '
                                                                            f'стоит {service.cost} руб.'))
    await cb.message.answer('Выбор специалиста:', reply_markup=m.get_specialist)
    await UserState.datetime.set()


@dp.callback_query_handler(Text([specialist for specialist in
                                 Specialist.objects.all().values_list('name', flat=True)] + ['Любой']),
                           state=UserState.datetime)
async def set_specialist(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    payloads = await state.get_data()
    for message in payloads['messages_responses']:
        await message.delete()

    async for specialist in Specialist.objects.filter(name=cb.data):  # результат - одно значение!
        await state.update_data(specialist_id=specialist.pk)
        await state.update_data(specialist_name=specialist.name)

        # ЗДЕСЬ НАДО ВСТАВИТЬ ВЫБОР ИЗ КАЛЕНДАРЯ!
        # И ЕСЛИ ВЫБРАН ЛЮБОЙ СПЕЦИАЛИСТ - ПОТОМ КОНКРЕТНОГО СОХРАНИТЬ В state

    await cb.message.answer('Выбор даты и времени:', reply_markup=m.choose_datetime)
    await UserState.registration.set()
    await cb.answer()


# ЗДЕСЬ НАДО ВСТАВИТЬ ВЫБОР ИЗ КАЛЕНДАРЯ!
@dp.callback_query_handler(Text(['today', 'tomorrow']), state=UserState.registration)
async def set_datetime(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    payloads = await state.get_data()
    for message in payloads['messages_responses']:
        await message.delete()
    client_id = await sync_to_async(funcs.get_client_id)(cb.from_user.username)
    if not client_id:
        # клиент зарегистрирован? проверка и далее - флаг и запрос номера телефона
        # если не зарегистрирован
        await state.update_data(client_id=None)
        payloads['messages_responses'].append(await cb.message.answer('Предлагаем Вам зарегистрироваться в нашей базе. '
                                                                      'Получите скидку 5%.'))
        payloads['messages_responses'].append(await cb.message.answer('Для регистрации ознакомьтесь с согласием '
                                                                      'на обработку персональных данных.'))
        payloads['messages_responses'].append(await bot.send_document(chat_id=cb.from_user.id,
                                                                      document=open(Path(BASE_DIR, 'permitted.pdf'),
                                                                                    'rb'),
                                                                      reply_markup=m.accept_personal_data))
        await UserState.name.set()
    else:
        await state.update_data(client_id=client_id)
        await UserState.record_save.set()
        await state.update_data(incognito_phone=None)
        await record_save(cb.message, state)
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
    await state.update_data(name=msg.text)
    await msg.answer('Введите свой телефон. Номер телефона необходимо ввести в формате: "+99999999999". '
                     'Допускается до 15 цифр.')
    await UserState.phone_verification.set()


@dp.message_handler(lambda msg: msg.text, state=UserState.phone_verification)
async def phone_verification(msg: types.Message, state: FSMContext):
    try:
        phone = PhoneNumber.from_string(msg.text, 'RU')
        phone_check = phone.is_valid()
    except NumberParseException:
        await msg.answer('Некорректно введен телефон! Попробуйте еще раз.')
        return
    if not phone_check:
        await msg.answer('Некорректно введен телефон! Проверьте формат. Попробуйте еще раз.')
        return
    phone_as_e164 = phone.as_e164
    await msg.answer(f'Телефон введен корректно! {phone_as_e164}')

    payloads = await state.get_data()
    incognito_phone = ''
    if payloads['registration_consent']:  # если дал согласие на регистрацию - сохранение юзера в БД
        client = await sync_to_async(funcs.registration_client)(payloads['name'], phone_as_e164,
                                                                msg.from_user.username, msg.from_user.id)
        await state.update_data(client_id=client.pk)
    else:
        incognito_phone = phone_as_e164
    await state.update_data(incognito_phone=incognito_phone)
    await UserState.record_save.set()
    await record_save(msg, state)


@dp.message_handler(state=UserState.record_save)
async def record_save(msg: types.Message, state: FSMContext):

    # нужно из введенных пользователем даты и времени сделать проверку их наличия свободных в расписании и оттуда взять
    # chedule_id
    chedule_id = 2  # временно
    chedule_date = '2022-02-02'
    chedule_time = '15:45'

    payloads = await state.get_data()
    client_id = payloads['client_id']
    incognito_phone = payloads['incognito_phone']

    await sync_to_async(funcs.make_order)(chedule_id, client_id, payloads['service_id'], incognito_phone)
    await msg.answer(f'Спасибо, Вы записаны на услугу "{payloads["service_name"]}" \n'
                     f'к специалисту {payloads["specialist_name"]}! \n'  # если "Любой" - будет ошибка. Надо выше сделать выбор и сохранение конкретного
                     f'До встречи {chedule_date} в {chedule_time} по адресу: МО, Балашиха, штабс DEVMAN”')
    await state.reset_state(with_data=False)
    await msg.answer('Главное меню', reply_markup=m.client_start_markup)


@dp.message_handler(state=UserState.standby)
async def incorrect_input_proceeding(msg: types.Message):
    await msg.answer('Главное меню', reply_markup=m.client_start_markup)


@dp.callback_query_handler(text="call_to_us", state=['*'])
async def call_to_us_message(cb: types.CallbackQuery):
    await cb.message.answer('Рады Вашему звонку в любое время – +7(800)555-35-35')
    await cb.answer()


async def sentinel():
    while 1:
        logging.info('Какая то проверка в течении какого то периода')
        await asyncio.sleep(86400)


async def on_startup(_):
    asyncio.create_task(sentinel())

executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
