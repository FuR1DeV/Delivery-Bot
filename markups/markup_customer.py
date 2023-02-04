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
                 f"{KEYBOARD.get('ARROWS_BUTTON')} Погрузка/Разгрузка",
                 f"{KEYBOARD.get('INPUT_LATIN_LETTERS')} Другое")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
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
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def performer_category():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('AUTOMOBILE')} На машине {KEYBOARD.get('AUTOMOBILE')}",
                 f"{KEYBOARD.get('KICK_SCOOTER')} На скутере {KEYBOARD.get('KICK_SCOOTER')}")
    keyboard.add(f"{KEYBOARD.get('PERSON_RUNNING')} Пешеход {KEYBOARD.get('PERSON_RUNNING')}",
                 f"Любой")
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def expired_data():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def photo_or_video_create_task():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Без фото или видео")
    keyboard.add("Загрузить Фото")
    keyboard.add("Загрузить Видео")
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def customer_type_orders():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"{KEYBOARD.get('A_BUTTON')} Заказы Доставки {KEYBOARD.get('B_BUTTON')}",
                 f"{KEYBOARD.get('ARROWS_BUTTON')} Заказы Грузчики {KEYBOARD.get('ARROWS_BUTTON')}")
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
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
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад",
                 f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def details_task_not_at_work():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('CROSS_MARK')} Отменить заказ",
                 f"{KEYBOARD.get('HAMMER_AND_PICK')} Редактировать заказ")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def details_task_loading_at_work():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('CLIPBOARD')} Детали заказа",
                 f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Список Грузчиков")
    keyboard.row(f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Завершить заказ")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def details_task_loading():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('CLIPBOARD')} Детали заказа",
                 f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Список Грузчиков")
    keyboard.row(f"{KEYBOARD.get('HAMMER_AND_PICK')} Редактировать заказ",
                 f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Завершить заказ",)
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def details_task_status():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('INFORMATION')} Проверить статус заказа",
                 f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Завершить заказ")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в детали заказа")
    return keyboard


def details_task_history():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('TELEPHONE')} Позвонить исполнителю",
                 f"{KEYBOARD.get('PENCIL')} Написать исполнителю")
    keyboard.row(f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Профиль исполнителя",
                 f"{KEYBOARD.get('CLIPBOARD')} Детали заказа")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню")
    return keyboard


def details_task_history_details_order():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Посмотреть фото",
                 "Посмотреть видео")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад в детали заказа")
    return keyboard


def open_site():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    google = types.KeyboardButton(text=f'{KEYBOARD.get("GLOBE_WITH_MERIDIANS")} Карта Google',
                                  web_app=WebAppInfo(url="https://www.google.com/maps"))
    yandex = types.KeyboardButton(text=f'{KEYBOARD.get("GLOBE_WITH_MERIDIANS")} Карта Yandex',
                                  web_app=WebAppInfo(url="https://www.yandex.ru/maps"))
    keyboard.row(google, yandex)
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def choose():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('WORLD_MAP')} Ввести координаты с карт",
                 f"{KEYBOARD.get('WRITING_HAND')} Ввести адрес вручную")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def send_my_geo():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text=f'{KEYBOARD.get("A_BUTTON")} Отправить моё местоположение',
                                  request_location=True)
    keyboard.add(button)
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def send_my_geo_2():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text=f'{KEYBOARD.get("B_BUTTON")} Конечная точка - моё местоположение',
                                  request_location=True)
    keyboard.add(button)
    keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
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


def inline_get_all_people_loading():
    approve_ = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Да", callback_data="yes_all_people_loading")
    no = InlineKeyboardButton(text="Нет", callback_data="not_all_people_loading")
    approve_.insert(yes)
    approve_.insert(no)
    return approve_


def inline_approve_geo_from():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_from")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_geo_from_loading():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_from_loading")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_geo_from_comp():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="approve_geo_from_comp")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_geo_position_site():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="change_geo_position_site")
    approve_geo.insert(yes)
    return approve_geo


def inline_approve_geo_position_custom():
    approve_geo = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Все верно", callback_data="change_geo_position_custom")
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


def inline_close_loading_task():
    close = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Да, все сделано", callback_data="loading_close_order")
    no = InlineKeyboardButton(text="Нет, не до конца", callback_data="loading_no_close")
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


def inline_change_task():
    change = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Редактируем", callback_data="change")
    no = InlineKeyboardButton(text="Передумал", callback_data="no_change")
    change.insert(yes)
    change.insert(no)
    return change


def inline_delete_loader():
    delete = InlineKeyboardMarkup()
    deleter = InlineKeyboardButton(text="Уволить Грузчика", callback_data="delete_loader")
    delete.insert(deleter)
    return delete


def inline_delete_loader_approve(user_id):
    delete = InlineKeyboardMarkup()
    delete.insert(InlineKeyboardButton(text="Да", callback_data=f"delete_loader_approve_{user_id}"))
    delete.insert(InlineKeyboardButton(text="Нет", callback_data="no_change"))
    return delete


def inline_approve():
    approve_ = InlineKeyboardMarkup()
    get = InlineKeyboardButton(text='Взять',
                               callback_data='performer_get')
    decline = InlineKeyboardButton(text='Отказаться',
                                   callback_data='performer_decline')
    approve_.insert(get)
    approve_.insert(decline)
    return approve_


def inline_approve_proposal_with_new_price(price):
    approve_ = InlineKeyboardMarkup()
    get = InlineKeyboardButton(text=f'Взять за {price}',
                               callback_data='performer_get_with_new_price')
    decline = InlineKeyboardButton(text=f'Отказаться',
                                   callback_data='performer_decline')
    approve_.insert(get)
    approve_.insert(decline)
    return approve_


def inline_approve_loading_proposal(user_id):
    approve_ = InlineKeyboardMarkup()
    get = InlineKeyboardButton(text=f'Пригласить',
                               callback_data=f'loading_invite_{user_id}')
    decline = InlineKeyboardButton(text=f'Отказать',
                                   callback_data='decline_loading')
    approve_.insert(get)
    approve_.insert(decline)
    return approve_


def rating():
    rating_ = types.ReplyKeyboardMarkup(resize_keyboard=True)
    rating_.row("5", "4")
    rating_.row("3", "2", "1")
    rating_.row("Пропустить")
    return rating_


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


def details_task_change_loading():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('INFORMATION')} Описание",
                 f"{KEYBOARD.get('A_BUTTON')} Место работы")
    keyboard.row(f"{KEYBOARD.get('DOLLAR')} Цена за 1 час",
                 f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Количество грузчиков")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Разблокировать заказ / Назад")
    return keyboard


def orders_type_work():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('HAMMER_AND_PICK')} В работе",
                 f"{KEYBOARD.get('RECYCLING_SYMBOL')} В ожидании")
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
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
