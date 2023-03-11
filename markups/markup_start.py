from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

inline_start = InlineKeyboardMarkup()
markup_clean = ReplyKeyboardRemove()

start_1 = InlineKeyboardButton(text='Я Заказчик',
                               callback_data='customer')
start_2 = InlineKeyboardButton(text='Курьер',
                               callback_data='performer')
start_3 = InlineKeyboardButton(text='Магазин',
                               callback_data='store')
start_4 = InlineKeyboardButton(text='Клиент',
                               callback_data='client')
inline_start.row(start_4, start_2)
inline_start.row(start_3)
