from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

inline_start = InlineKeyboardMarkup()
markup_clean = ReplyKeyboardRemove()

start_1 = InlineKeyboardButton(text='Я Заказчик',
                               callback_data='customer')
start_2 = InlineKeyboardButton(text='Я Исполнитель',
                               callback_data='performer')
start_3 = InlineKeyboardButton(text='Магазин',
                               callback_data='store')
inline_start.insert(start_1)
inline_start.insert(start_2)
inline_start.insert(start_3)
