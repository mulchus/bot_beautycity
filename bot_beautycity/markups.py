from aiogram import types
from admin_beautycity.models import Service, Specialist

CALL_TO_US = types.InlineKeyboardButton('Call us', callback_data='call_to_us')
EXIT = types.InlineKeyboardButton('<= Return', callback_data='exit')
ADDITIONAL_BUTTONS = [CALL_TO_US, EXIT, ]

client_start_markup = types.InlineKeyboardMarkup(row_width=2)
client_start_markup_buttons = [
    types.InlineKeyboardButton('About us', url='https://telegra.ph/O-salonah-krasoty-BeautyCity-05-23'),
    types.InlineKeyboardButton('Sign up for the service', callback_data='choice_service'),
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
get_specialist_buttons.append(types.InlineKeyboardButton('Any', callback_data='Any'))
get_specialist_buttons += ADDITIONAL_BUTTONS
get_specialist.add(*get_specialist_buttons)

# здесь необходимо реализовать выбор даты-времени из какого то массива рабочего времени.
choose_datetime = types.InlineKeyboardMarkup(row_width=2)
choose_datetime_buttons = [
    types.InlineKeyboardButton('Today', callback_data='today'),
    types.InlineKeyboardButton('Tomorrow', callback_data='tomorrow'),
    types.InlineKeyboardButton('Select in calendar', callback_data='calendar'),
    types.InlineKeyboardButton('Pay the order', callback_data='buy'),
] + ADDITIONAL_BUTTONS
choose_datetime.add(*choose_datetime_buttons)

make_order = types.InlineKeyboardMarkup(row_width=2)
make_order_buttons = [
    types.InlineKeyboardButton('Sign up', callback_data='order_yes'),
    types.InlineKeyboardButton('Refuse', callback_data='order_no'),
] + ADDITIONAL_BUTTONS
make_order.add(*make_order_buttons)

accept_personal_data = types.InlineKeyboardMarkup(row_width=2)
accept_personal_data_buttons = [
    types.InlineKeyboardButton('I agree', callback_data='personal_yes'),
    types.InlineKeyboardButton('I dont agree', callback_data='personal_no'),
] + ADDITIONAL_BUTTONS
accept_personal_data.add(*accept_personal_data_buttons)

exit_markup = types.InlineKeyboardMarkup(row_width=1)
exit_markup.add(EXIT)
