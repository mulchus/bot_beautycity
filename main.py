import asyncio
import logging
import os
from datetime import datetime, timedelta
from textwrap import dedent
from pathlib import Path

import dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from asgiref.sync import sync_to_async
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException
from aiogram.types import CallbackQuery
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from aiogram.types.message import ContentType

from bot_beautycity import funcs
from bot_beautycity import markups as m
from admin_beautycity.models import Service, Specialist

BASE_DIR = Path(__file__).resolve().parent
dotenv.load_dotenv(Path(BASE_DIR, '.env'))
token = os.environ['BOT_TOKEN']
PAYMENT_TOKEN = os.environ['PAYMENT_TOKEN']

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)


class UserState(StatesGroup):
    choice_service = State()
    choice_specialist = State()
    choice_datetime = State()
    get_registration = State()
    set_name_phone = State()
    phone_verification = State()
    final_markup = State()


@dp.message_handler()
async def start_conversation(msg: types.Message, state: FSMContext):
    messages_responses = []
    message = dedent(
        '  Welcome! \n' 'BeautyCity beauty salon is not only highly'
        ' professional services, but also a cozy salon where guests'
        ' are always welcome. \nPerfection in work and creativity,'
        ' attentive craftsmen will take into account and realize '
        'all your wishes!')
    messages_responses.append(await msg.answer(dedent(message)))
    records_count = await sync_to_async(funcs.get_records_count)(
        msg.from_user.username
    )
    if records_count:
        message = await msg.answer(
            f'Welcome back, {msg.from_user.first_name}. '
            f'You already had recordings: {records_count}.'
        )
    else:
        message = await msg.answer(f'Hello, {msg.from_user.first_name}.')
    messages_responses.append(message)
    await msg.answer('Main menu', reply_markup=m.client_start_markup)
    await state.update_data(messages_responses=messages_responses)


@dp.callback_query_handler(text="exit", state=[UserState, None])
async def exit_client_proceeding(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await cb.message.answer('Main menu', reply_markup=m.client_start_markup)
    await state.reset_state(with_data=False)
    await state.update_data(registration_consent=False)
    await cb.answer()


@dp.callback_query_handler(text="call_to_us", state=[UserState, None])
async def call_to_us_message(cb: types.CallbackQuery):
    await cb.message.answer(
        'We are glad to receive your call at any time – +7(800)555-35-35'
    )
    await cb.answer()


@dp.callback_query_handler(Text('choice_service'), state=[UserState, None])
async def service_choosing(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    try:
        messages_responses = await state.get_data('messages_responses')
        for message in messages_responses['messages_responses']:
            await message.delete()
        await state.update_data(messages_responses=[])
    except TypeError:
        pass
    await cb.message.answer(
        'Choosing a service:',
        reply_markup=await sync_to_async(m.get_services)()
    )
    await UserState.choice_service.set()
    await cb.answer()


@dp.callback_query_handler(state=UserState.choice_service)
async def set_service(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await state.update_data(tg_id=cb.from_user.id)

    async for service in Service.objects.filter(name=cb.data):
        await state.update_data(service_id=service.pk)
        await state.update_data(service_name=service.name)
        await state.update_data(service_cost=service.cost)

    messages_responses = await state.get_data('messages_responses')
    messages_responses['messages_responses'].append(await cb.message.answer(
        f'Service "{service.name}" '
        f'costs {service.cost} rub.'))
    await cb.message.answer(
        'Choosing a specialist:',
        reply_markup=await sync_to_async(m.get_specialists)()
    )
    await UserState.choice_specialist.set()
    await cb.answer()


@dp.callback_query_handler(state=UserState.choice_specialist)
async def set_specialist(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    payloads = await state.get_data()
    for message in payloads['messages_responses']:
        await message.delete()
    async for specialist in Specialist.objects.filter(name=cb.data):
        await state.update_data(specialist_id=specialist.pk)
        await state.update_data(specialist_name=specialist.name)

    await cb.message.answer(
        'Choose date and time:',
        reply_markup=m.choose_datetime
    )
    await UserState.choice_datetime.set()
    await cb.answer()


@dp.callback_query_handler(
        Text(['today', 'tomorrow']),
        state=UserState.choice_datetime
    )
async def set_datetime(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    payloads = await state.get_data()
    for message in payloads['messages_responses']:
        await message.delete()
    if cb.data == 'today':
        date = datetime.now()
    if cb.data == 'tomorrow':
        date = datetime.now() + timedelta(days=1)
    await state.update_data(date=date)
    markup, dates = await sync_to_async(funcs.get_datetime)(
        date,
        payloads['specialist_id']
    )
    if not dates:
        await cb.message.answer(
            'No free slots, please choose other day',
            reply_markup=m.choose_datetime
        )
    else:
        await state.update_data(dates=dates)
        await cb.message.answer(
            'Possible time windows:',
            reply_markup=markup
        )

    await cb.answer()


@dp.callback_query_handler(
        Text(['personal_yes', 'personal_no']),
        state=UserState.get_registration
    )
async def accepting_permission(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete()
    payloads = await state.get_data()
    for message in payloads['messages_responses']:
        await message.delete()

    if cb.data == 'personal_no':
        registration_consent = False
        await cb.message.answer(
            'Sorry. But we need your name and phone number to contact you.'
        )
    else:
        registration_consent = True
    await state.update_data(registration_consent=registration_consent)
    await cb.message.answer('Enter your name:')
    await UserState.set_name_phone.set()
    await cb.answer()


@dp.message_handler(lambda msg: msg.text, state=UserState.set_name_phone)
async def set_name_phone(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer(
        'Enter your phone number. The phone number must be entered'
        ' in the format: "+99999999999". '
        'Up to 15 digits are allowed.'
    )
    await UserState.phone_verification.set()



@dp.message_handler(lambda msg: msg.text, state=UserState.phone_verification)
async def phone_verification(msg: types.Message, state: FSMContext):
    try:
        phone = PhoneNumber.from_string(msg.text, 'RU')
        phone_check = phone.is_valid()
    except NumberParseException:
        await msg.answer(
            'The phone number was entered incorrectly! Try again.'
        )
        return
    if not phone_check:
        await msg.answer(
            'The phone number was entered incorrectly!'
            'Check the format. Try again.'
        )
        return
    phone_as_e164 = phone.as_e164
    await msg.answer(f'The phone number is entered correctly! {phone_as_e164}')

    payloads = await state.get_data()
    incognito_phone = ''
    if payloads['registration_consent']:
        client = await sync_to_async(funcs.registration_client)(
            payloads['name'],
            phone_as_e164,
            msg.from_user.username,
            msg.from_user.id
        )
        await state.update_data(client_id=client.pk)
    else:
        incognito_phone = phone_as_e164
    await state.update_data(incognito_phone=incognito_phone)
    await record_save(state)


async def record_save(state: FSMContext):

    payloads = await state.get_data()
    tg_id = payloads['tg_id']
    client_id = payloads['client_id']
    incognito_phone = payloads['incognito_phone']
    specialist_id = payloads['specialist_id']
    full_schedule_date = payloads['dates'][int(payloads['date_index'])]
    schedule_date = full_schedule_date.strftime('%m/%d/%Y')
    schedule_time = full_schedule_date.strftime('%H:%M')

    schedule_id = await sync_to_async(funcs.make_order)(
        full_schedule_date,
        specialist_id,
        client_id,
        payloads['service_id'],
        incognito_phone
    )
    await state.update_data(schedule_id=schedule_id)
    await bot.send_message(
        tg_id,
        f'Thank you, you are signed up for the service'
        f' "{payloads["service_name"]}" '
        f'to a specialist {payloads["specialist_name"]}! \n'
        f'See you soon {schedule_date} в {schedule_time} at: '
        f'Moscow region, Balashikha, headquarters DEVMAN')
    await state.reset_state(with_data=False)
    await bot.send_message(tg_id, 'Final menu', reply_markup=m.final_markup)


@dp.callback_query_handler(Text(['final']), state=[UserState, None])
async def final(cb: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False)
    await state.update_data(registration_consent=False)
    await bot.delete_message(
        chat_id=cb.from_user.id,
        message_id=cb.message.message_id
    )


# buy
@dp.callback_query_handler(Text(['buy']), state=[UserState, None])
async def buy(cb: types.CallbackQuery, state: FSMContext):
    payloads = await state.get_data()
    if payloads['registration_consent']:
        amount = int(payloads['service_cost']) * 95
    else:
        amount = int(payloads['service_cost']) * 100
    txt = payloads['service_name']
    price = types.LabeledPrice(
        label=txt,
        amount=amount
    )
    await bot.send_invoice(
        cb.message.chat.id,
        title=txt,
        description=txt,
        provider_token=PAYMENT_TOKEN,
        currency='rub',
        photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[price],
        start_parameter='test',
        payload='test-invoice-payload'
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(
        content_types=ContentType.SUCCESSFUL_PAYMENT,
        state=[UserState, None]
    )
async def successful_payment(message: types.Message, state: FSMContext):
    payloads = await state.get_data()
    await bot.send_message(
        message.chat.id,
        f'Payment at {message.successful_payment.total_amount // 100}'
        f'{message.successful_payment.currency} done'
    )
    await sync_to_async(funcs.pay_order)(payloads['schedule_id'])
    await state.reset_state(with_data=False)
    await state.update_data(registration_consent=False)
    await message.answer('Main menu', reply_markup=m.client_start_markup)


@dp.callback_query_handler(Text(['calendar']), state=UserState.choice_datetime)
async def set_datetime_calendar(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.answer(
        "Please select a date: ",
        reply_markup=await SimpleCalendar().start_calendar()
    )


@dp.callback_query_handler(
        simple_cal_callback.filter(),
        state=UserState.choice_datetime
    )
async def process_simple_calendar(
    cb: CallbackQuery,
    callback_data: dict,
    state: FSMContext
):
    selected, date = await SimpleCalendar().process_selection(cb,
                                                              callback_data)
    if selected:
        current_date = date.strftime("%d/%m/%Y")
        await cb.message.delete()
        await cb.message.answer(
            f'You have chosen {current_date}, choose a convenient time:',
        )
        payloads = await state.get_data()
        await state.update_data(date=date)
        markup, dates = await sync_to_async(funcs.get_datetime)(
            date,
            payloads['specialist_id']
        )
        if dates:
            await state.update_data(dates=dates)
            await cb.message.answer(
                'Possible time windows:',
                reply_markup=markup
            )
        else:
            await cb.message.answer(
                'No free slots, please choose other day',
                reply_markup=m.choose_datetime
            )
    await cb.answer()


@dp.callback_query_handler(
    Text(startswith='Possible time'),
    state=UserState.choice_datetime
)
async def set_time_window(cb: types.CallbackQuery, state: FSMContext):
    date_index = cb.data[22:]
    await state.update_data(date_index=date_index)
    payloads = await state.get_data()
    client_id = await sync_to_async(funcs.get_client_id)(cb.from_user.username)
    if not client_id:
        await state.update_data(client_id=None)
        payloads['messages_responses'].append(await cb.message.answer(
            'We invite you to register in our database.'
            'Get a 5% discount.')
        )
        payloads['messages_responses'].append(await cb.message.answer(
            'To register, read the consent '
            'for the processing of personal data.')
        )
        payloads['messages_responses'].append(await bot.send_document(
            chat_id=cb.from_user.id,
            document=open(Path(BASE_DIR, 'permitted.pdf'), 'rb'),
            reply_markup=m.accept_personal_data)
        )
        await UserState.get_registration.set()
    else:
        await state.update_data(client_id=client_id)
        await state.update_data(incognito_phone=None)
        await record_save(state)


@dp.callback_query_handler(
        Text(startswith='Possible time'),
        state=UserState.phone_verification
    )
async def set_time_win(cb: types.CallbackQuery, state: FSMContext):
    date_index = cb.data[22:]
    await state.update_data(date_index=date_index)


# видимо эти блоки ниже не понадобидись. Сделать запуск бота без on_startup
async def sentinel():
    while 1:
        logging.info('Какая то проверка в течении какого то периода')
        await asyncio.sleep(86400)


async def on_startup(_):
    asyncio.create_task(sentinel())

executor.start_polling(dp, skip_updates=False)
