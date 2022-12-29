from aiogram import types
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from settings.config import KEYBOARD

markup_clean = ReplyKeyboardRemove()


def back():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Мой профиль",
                 f"{KEYBOARD.get('HAMMER_AND_PICK')} Создать заказ")
    keyboard.row(f"{KEYBOARD.get('WRENCH')} Мои заказы",
                 f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Завершенные заказы")
    keyboard.row(f"{KEYBOARD.get('SOS_BUTTON')} Помощь")
    return keyboard


def category_delivery():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('BOUQUET')} Цветы",
                 f"{KEYBOARD.get('WRAPPED_GIFT')} Подарки",
                 f"{KEYBOARD.get('SHORTCAKE')} Кондитерка")
    keyboard.row(f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')} Документы",
                 f"{KEYBOARD.get('ARROWS_BUTTON')} Погрузка/Разгрузка")
    keyboard.row(f"{KEYBOARD.get('INPUT_LATIN_LETTERS')} Другое")
    keyboard.row(f"{KEYBOARD.get('CROSS_MARK')} Отмена")
    return keyboard


def back_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def cancel():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('CROSS_MARK')} Отмена")
    return keyboard


def approve():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('COMP')} С компьютера", f"{KEYBOARD.get('PHONE')} С телефона")
    keyboard.add(f"{KEYBOARD.get('CROSS_MARK')} Отмена")
    return keyboard


def performer_category():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('AUTOMOBILE')} На машине {KEYBOARD.get('AUTOMOBILE')}",
                 f"{KEYBOARD.get('KICK_SCOOTER')} На скутере {KEYBOARD.get('KICK_SCOOTER')}")
    keyboard.add(f"{KEYBOARD.get('PERSON_RUNNING')} Пешеход {KEYBOARD.get('PERSON_RUNNING')}",
                 f"Любой")
    keyboard.add(f"{KEYBOARD.get('CROSS_MARK')} Отмена")
    return keyboard


def expired_data():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('CROSS_MARK')} Отмена")
    return keyboard


def photo_or_video_create_task():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Без фото или видео")
    keyboard.add("Загрузить Фото")
    keyboard.add("Загрузить Видео")
    keyboard.add(f"{KEYBOARD.get('CROSS_MARK')} Отмена")
    return keyboard


def photo_or_video_help():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Загрузить Фото")
    keyboard.add("Загрузить Видео")
    keyboard.add("Вернуться главное меню")
    return keyboard


def customer_profile():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('BAR_CHART')} Статистика по заказам")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Главное меню")
    return keyboard


def details_task():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Написать/Позвонить исполнителю",
                 f"{KEYBOARD.get('CLIPBOARD')} Детали заказа")
    keyboard.row(f"{KEYBOARD.get('EX_QUEST_MARK')} Статус заказа",
                 f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Профиль исполнителя")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def details_task_not_at_work():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('CROSS_MARK')} Отменить заказ",
                 f"{KEYBOARD.get('HAMMER_AND_PICK')} Редактировать заказ")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def details_task_status():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('CROSS_MARK')} Отменить заказ",
                 f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Завершить заказ")
    keyboard.row(f"{KEYBOARD.get('INFORMATION')} Проверить статус заказа")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в детали заказа")
    return keyboard


def details_task_history():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('TELEPHONE')} Позвонить исполнителю",
                 f"{KEYBOARD.get('PENCIL')} Написать исполнителю")
    keyboard.row(f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Профиль исполнителя")
    keyboard.row(f"{KEYBOARD.get('CLIPBOARD')} Посмотреть детали заказа")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def details_task_history_details_order():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Посмотреть фото")
    keyboard.row("Посмотреть видео")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад в детали заказа")
    return keyboard


def open_site():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    google = types.KeyboardButton(text=f'{KEYBOARD.get("GLOBE_WITH_MERIDIANS")} Карта Google', web_app=WebAppInfo(url="https://www.google.com/maps"))
    keyboard.add(google)
    keyboard.add(f"{KEYBOARD.get('CROSS_MARK')} Отмена")
    return keyboard


def choose():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('WORLD_MAP')} Ввести координаты с карт",
                 f"{KEYBOARD.get('WRITING_HAND')} Ввести адрес вручную")
    keyboard.row(f"{KEYBOARD.get('CROSS_MARK')} Отмена")
    return keyboard


def send_my_geo():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text='Отправить моё местоположение', request_location=True)
    keyboard.add(button)
    keyboard.add(f"{KEYBOARD.get('CROSS_MARK')} Отмена")
    return keyboard


def change_my_geo():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text='Отправить моё местоположение', request_location=True)
    keyboard.add(button)
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def details_task_status_review():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('UPWARDS_BUTTON')} Войти в детали заказа")
    return keyboard


def inline_approve_geo_from():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_from")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_geo_from_comp():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_from_comp")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_geo_from_custom():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_from_custom")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_geo_to():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_to")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_geo_to_custom():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_to_custom")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_geo_to_comp():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_to_comp")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_change_geo_from():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_from")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_change_geo_to():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_to")
    approve_geo.insert(yes)
    return approve_geo


def inline_close_task():
    close = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Да, все сделано", callback_data="close_order")
    no = InlineKeyboardButton(text="Нет, не до конца", callback_data="no_close")
    close.insert(yes)
    close.insert(no)
    return close


def inline_cancel_task():
    cancel = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Отменяем", callback_data="cancel")
    no = InlineKeyboardButton(text="Передумал", callback_data="no_cancel")
    cancel.insert(yes)
    cancel.insert(no)
    return cancel


def inline_change_task():
    change = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Редактируем", callback_data="change")
    no = InlineKeyboardButton(text="Передумал", callback_data="no_change")
    change.insert(yes)
    change.insert(no)
    return change


def inline_approve():
    approve = InlineKeyboardMarkup()
    get = InlineKeyboardButton(text='Взять',
                               callback_data='performer_get')
    decline = InlineKeyboardButton(text='Отказаться',
                                   callback_data='performer_decline')
    approve.insert(get)
    approve.insert(decline)
    return approve


def inline_approve_proposal_with_new_price(price):
    approve = InlineKeyboardMarkup()
    get = InlineKeyboardButton(text=f'Взять за {price}',
                               callback_data='performer_get_with_new_price')
    decline = InlineKeyboardButton(text=f'Отказаться',
                                   callback_data='performer_decline')
    approve.insert(get)
    approve.insert(decline)
    return approve


def rating():
    rating = types.ReplyKeyboardMarkup(resize_keyboard=True)
    rating.row("5", "4")
    rating.row("3", "2", "1")
    return rating


def help_customer():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Завершить")
    return keyboard


def details_task_change():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('INFORMATION')} Название",
                 f"{KEYBOARD.get('INFORMATION')} Описание")
    keyboard.row(f"{KEYBOARD.get('A_BUTTON')} Откуда забрать",
                 f"{KEYBOARD.get('B_BUTTON')} Куда доставить")
    keyboard.row(f"{KEYBOARD.get('DOLLAR')} Цену")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Разблокировать заказ / Назад")
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
