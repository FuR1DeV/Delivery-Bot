from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from settings.config import KEYBOARD

markup_clean = ReplyKeyboardRemove()


def back():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def inline_approve():
    approve_ = InlineKeyboardMarkup()
    get = InlineKeyboardButton(text='Запросить',
                               callback_data='performer_request')
    decline = InlineKeyboardButton(text='Отказаться',
                                   callback_data='performer_decline')
    price = InlineKeyboardButton(text='Предложить цену',
                                 callback_data='performer_proposal')
    approve_.insert(get)
    approve_.insert(decline)
    approve_.insert(price)
    return approve_


def inline_approve_loading(order_id):
    approve_ = InlineKeyboardMarkup()
    get = InlineKeyboardButton(text='Запрос',
                               callback_data=f'request_loading_{order_id}')
    decline = InlineKeyboardButton(text='Отказаться',
                                   callback_data=f'decline_loading')
    approve_.insert(get)
    approve_.insert(decline)
    return approve_


def inline_approve_loading_yes_no(order_id):
    approve_ = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text='Да',
                               callback_data=f'yes_req_load_{order_id}')
    no = InlineKeyboardButton(text='Нет',
                                   callback_data=f'no_req_load_{order_id}')
    approve_.insert(yes)
    approve_.insert(no)
    return approve_


def inline_approve_main():
    approve_ = InlineKeyboardMarkup()
    get = InlineKeyboardButton(text='Соглашаюсь',
                               callback_data='customer_yes')
    decline = InlineKeyboardButton(text='Отказаться',
                                   callback_data='customer_no')
    approve_.insert(get)
    approve_.insert(decline)
    return approve_


def inline_approve_proposal():
    approve_ = InlineKeyboardMarkup()
    get = InlineKeyboardButton(text='Соглашаюсь',
                               callback_data='proposal_yes')
    decline = InlineKeyboardButton(text='Отказаться',
                                   callback_data='proposal_no')
    approve_.insert(get)
    approve_.insert(decline)
    return approve_


def inline_you_sure():
    sure = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Да уверен", callback_data="cancel_order")
    no = InlineKeyboardButton(text="Нет, я передумал", callback_data="no_cancel")
    sure.insert(yes)
    sure.insert(no)
    return sure


def inline_close_task():
    close = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Да, все сделано", callback_data="close_order")
    no = InlineKeyboardButton(text="Нет, не до конца", callback_data="no_close")
    close.insert(yes)
    close.insert(no)
    return close


def inline_cancel_task():
    cancel_ = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Отменяем", callback_data="cancel")
    no = InlineKeyboardButton(text="Передумал", callback_data="no_cancel")
    cancel_.insert(yes)
    cancel_.insert(no)
    return cancel_


def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Мой профиль",
                 f"{KEYBOARD.get('HAMMER_AND_PICK')} Доступные Задачи")
    keyboard.row(f"{KEYBOARD.get('WRENCH')} Задачи в работе",
                 f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Выполненные Задачи")
    keyboard.row(f"{KEYBOARD.get('SOS_BUTTON')} Помощь")
    return keyboard


def get_order():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('ID_BUTTON')} Ввести ID задачи")
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def performer_type_orders():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('A_BUTTON')} Заказы Доставки {KEYBOARD.get('B_BUTTON')}",
                 f"{KEYBOARD.get('ARROWS_BUTTON')} Заказы Грузчика {KEYBOARD.get('ARROWS_BUTTON')}")
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def details_task_loading():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('TELEPHONE')} Позвонить/написать заказчику",
                 f"{KEYBOARD.get('CLIPBOARD')} Детали заказа")
    keyboard.row(f"{KEYBOARD.get('BUSTS_IN_SILHOUETTE')} Список Грузчиков",
                 f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Профиль заказчика")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def back_user_profile():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в Мой профиль")
    return keyboard


def back_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться главное меню")
    return keyboard


def rating():
    rating_ = types.ReplyKeyboardMarkup(resize_keyboard=True)
    rating_.row("5", "4")
    rating_.row("3", "2", "1")
    return rating_


def cancel():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('CROSS_MARK')} Отмена")
    return keyboard


def approve(auto):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('A_BUTTON')} Доставка {KEYBOARD.get('B_BUTTON')}",
                 f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Грузчики {KEYBOARD.get('ARROWS_BUTTON')}")
    if auto:
        keyboard.add(f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Автоотправление сообщений включено")
    else:
        keyboard.add(f"{KEYBOARD.get('CROSS_MARK')} Автоотправление сообщений отключено")
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def photo_or_video_help(chat_info):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"Загрузить Фото", f"Загрузить Видео")
    if not chat_info:
        keyboard.add(f"Закрытый чат курьеров")
    keyboard.add(f"Вернуться главное меню")
    return keyboard


def performer_profile():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('OUTBOX_TRAY')} Вывести средства",
                 f"{KEYBOARD.get('INBOX_TRAY')} Пополнить баланс")
    keyboard.row(f"{KEYBOARD.get('BAR_CHART')} Статистика по заказам",
                 f"{KEYBOARD.get('PERSON_RUNNING')}{KEYBOARD.get('AUTOMOBILE')} Статус категории")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Главное меню")
    return keyboard


def performer_profile_change_status():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('PERSON_RUNNING')} Я пешеход")
    keyboard.row(f"{KEYBOARD.get('AUTOMOBILE')} Я на транспорте")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def performer_profile_change_status_transport():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('AUTOMOBILE')} Я на машине")
    keyboard.row(f"{KEYBOARD.get('KICK_SCOOTER')} Я на самокате")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def details_task():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('TELEPHONE')} Позвонить/написать заказчику",
                 f"{KEYBOARD.get('CLIPBOARD')} Детали заказа")
    keyboard.row(f"{KEYBOARD.get('EX_QUEST_MARK')} Статус заказа",
                 f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Профиль заказчика")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def details_task_status_review():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('UPWARDS_BUTTON')} Войти в детали заказа")
    return keyboard


def details_task_status(arrive):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('CROSS_MARK')} Отменить заказ",
                 f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Завершить заказ")
    keyboard.row(f"{KEYBOARD.get('EX_QUEST_MARK')} Проверить статус заказа",
                 f"{KEYBOARD.get('WAVING_HAND')} Сообщить о прибытии {arrive}")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в детали заказа")
    return keyboard


def details_task_status_end():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('CROSS_MARK')} Отменить заказ",
                 f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Завершить заказ")
    keyboard.row(f"{KEYBOARD.get('EX_QUEST_MARK')} Проверить статус заказа")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в детали заказа")
    return keyboard


def inline_approve_arrive(user_id):
    approve_ = InlineKeyboardMarkup()
    get = InlineKeyboardButton(text='Принято. Отправить сообщение Исполнителю',
                               callback_data=f'arrive_approve_{user_id}')
    approve_.insert(get)
    return approve_


def details_task_history():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('TELEPHONE')} Позвонить Заказчику",
                 f"{KEYBOARD.get('PENCIL')} Написать Заказчику")
    keyboard.row(f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Профиль Заказчика")
    keyboard.row(f"{KEYBOARD.get('CLIPBOARD')} Посмотреть детали заказа")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def details_task_history_details_order():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"Посмотреть фото")
    keyboard.row(f"Посмотреть видео")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад в детали заказа")
    return keyboard


def help_performer():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Завершить")
    return keyboard


def buy_menu(is_url=True, url='', bill=''):
    menu = InlineKeyboardMarkup(row_width=1)
    if is_url:
        btn_url = InlineKeyboardButton(text="Ссылка на оплату", url=url)
        menu.insert(btn_url)
    btn_check = InlineKeyboardButton(text="Проверить оплату", callback_data="check_"+bill)
    btn_cancel = InlineKeyboardButton(text="Отмена", callback_data="cancel_pay")
    menu.insert(btn_check)
    menu.insert(btn_cancel)
    return menu


def cancel_pay():
    cancel_btn = InlineKeyboardButton(text="Отмена", callback_data='cancel_pay')
    cancel_menu = InlineKeyboardMarkup(row_width=1)
    cancel_menu.insert(cancel_btn)
    return cancel_menu


def private_chat_pay():
    btn = InlineKeyboardButton(text="Запрос на вхождение", callback_data='private_chat')
    private_chat = InlineKeyboardMarkup(row_width=1)
    private_chat.insert(btn)
    return private_chat


def order_rating(order_id):
    btn_plus = InlineKeyboardButton(text=f"{KEYBOARD.get('THUMBS_UP')}", callback_data=f'plus_{order_id}')
    btn_minus = InlineKeyboardButton(text=f"{KEYBOARD.get('THUMBS_DOWN')}", callback_data=f'minus_{order_id}')
    rate = InlineKeyboardMarkup()
    rate.insert(btn_plus)
    rate.insert(btn_minus)
    return rate
