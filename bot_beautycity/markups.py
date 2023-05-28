from aiogram import types
from admin_beautycity.models import Service, Specialist

CALL_TO_US = types.InlineKeyboardButton('Позвонить нам', callback_data='call_to_us')
EXIT = types.InlineKeyboardButton('<= Вернуться', callback_data='exit')
ADDITIONAL_BUTTONS = [CALL_TO_US, EXIT, ]

client_start_markup = types.InlineKeyboardMarkup(row_width=2)
client_start_markup_buttons = [
    types.InlineKeyboardButton('О нас', url='https://telegra.ph/O-salonah-krasoty-BeautyCity-05-23'),
    types.InlineKeyboardButton('Записаться на услугу', callback_data='choice_service'),
    CALL_TO_US,
]
client_start_markup.add(*client_start_markup_buttons)

get_service = types.InlineKeyboardMarkup(row_width=2)
services = Service.objects.all()
get_service_buttons = [types.InlineKeyboardButton(
    service.name, callback_data=service.name_english) for service in services] + ADDITIONAL_BUTTONS
get_service.add(*get_service_buttons)

get_specialist = types.InlineKeyboardMarkup(row_width=2)
specialists = Specialist.objects.all()
get_specialist_buttons = [types.InlineKeyboardButton(
    specialist.name, callback_data=specialist.name) for specialist in specialists]
get_specialist_buttons.append(types.InlineKeyboardButton('Любой', callback_data='Любой'))
get_specialist_buttons += ADDITIONAL_BUTTONS
get_specialist.add(*get_specialist_buttons)

# здесь необходимо реализовать выбор даты-времени из какого то массива рабочего времени.
choose_datetime = types.InlineKeyboardMarkup(row_width=2)
choose_datetime_buttons = [
    types.InlineKeyboardButton('Сегодня', callback_data='today'),
    types.InlineKeyboardButton('Завтра', callback_data='tomorrow'),
    types.InlineKeyboardButton('Выбрать в календаре', callback_data='calendar')
] + ADDITIONAL_BUTTONS
choose_datetime.add(*choose_datetime_buttons)

make_order = types.InlineKeyboardMarkup(row_width=2)
make_order_buttons = [
    types.InlineKeyboardButton('Записаться', callback_data='order_yes'),
    types.InlineKeyboardButton('Отказаться', callback_data='order_no'),
] + ADDITIONAL_BUTTONS
make_order.add(*make_order_buttons)

accept_personal_data = types.InlineKeyboardMarkup(row_width=2)
accept_personal_data_buttons = [
    types.InlineKeyboardButton('Согласен', callback_data='personal_yes'),
    types.InlineKeyboardButton('Несогласен', callback_data='personal_no'),
] + ADDITIONAL_BUTTONS
accept_personal_data.add(*accept_personal_data_buttons)

exit_markup = types.InlineKeyboardMarkup(row_width=1)
exit_markup.add(EXIT)


# ======= CLIENT BLOCK (END) ===============================================================================
