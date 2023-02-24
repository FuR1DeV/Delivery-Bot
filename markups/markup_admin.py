from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup
from settings import config


markup_clean = ReplyKeyboardRemove()


def admin_main():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Комиссия", "Просмотр Заказов")
    keyboard.row("Управление пользователями", "Объявления")
    keyboard.row("Статистика", "Смены")
    return keyboard


def commission():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Просмотр комиссии")
    keyboard.row("Установить комиссию")
    keyboard.row("Назад")
    return keyboard


def commission_set():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Для Исполнителя")
    keyboard.row("Для категорий доставок", "Промо")
    keyboard.row("Назад")
    return keyboard


def commission_promo():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Введите ID Исполнителя")
    keyboard.row("Назад")
    return keyboard


def commission_promo_discount():
    keyboard = InlineKeyboardMarkup()
    without = InlineKeyboardButton(text="Без комиссии", callback_data="commission_free")
    comm_1 = InlineKeyboardButton(text="Комиссия 0.1%", callback_data="commission_0.1")
    comm_2 = InlineKeyboardButton(text="Комиссия 0.2%", callback_data="commission_0.2")
    comm_3 = InlineKeyboardButton(text="Комиссия 0.3%", callback_data="commission_0.3")
    comm_4 = InlineKeyboardButton(text="Комиссия 0.4%", callback_data="commission_0.4")
    comm_5 = InlineKeyboardButton(text="Комиссия 0.5%", callback_data="commission_0.5")
    comm_6 = InlineKeyboardButton(text="Комиссия 0.6%", callback_data="commission_0.6")
    comm_7 = InlineKeyboardButton(text="Комиссия 0.7%", callback_data="commission_0.7")
    comm_8 = InlineKeyboardButton(text="Комиссия 0.8%", callback_data="commission_0.8")
    comm_9 = InlineKeyboardButton(text="Комиссия 0.9%", callback_data="commission_0.9")
    comm_10 = InlineKeyboardButton(text="Комиссия 1.0%", callback_data="commission_1.0")
    comm_back = InlineKeyboardButton(text=f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад",
                                     callback_data="commission_back")
    keyboard.insert(without)
    keyboard.insert(comm_1)
    keyboard.insert(comm_2)
    keyboard.insert(comm_3)
    keyboard.insert(comm_4)
    keyboard.insert(comm_5)
    keyboard.insert(comm_6)
    keyboard.insert(comm_7)
    keyboard.insert(comm_8)
    keyboard.insert(comm_9)
    keyboard.insert(comm_10)
    keyboard.insert(comm_back)
    return keyboard


def commission_promo_set_time():
    keyboard = InlineKeyboardMarkup()
    time_1 = InlineKeyboardButton(text="3 часа", callback_data="time_3")
    time_2 = InlineKeyboardButton(text="6 часа", callback_data="time_6")
    time_3 = InlineKeyboardButton(text="9 часа", callback_data="time_9")
    time_4 = InlineKeyboardButton(text="12 часа", callback_data="time_12")
    time_back = InlineKeyboardButton(text=f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад",
                                     callback_data="time_back")
    keyboard.insert(time_1)
    keyboard.insert(time_2)
    keyboard.insert(time_3)
    keyboard.insert(time_4)
    keyboard.insert(time_back)
    return keyboard


def back():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Назад")
    return keyboard


def statistics():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("По заказчикам", "По исполнителям")
    keyboard.row("По категориям")
    keyboard.row("Назад")
    return keyboard


def enter_id():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Введите ID заказа", "Выгрузить БД отзывов")
    keyboard.row("Выгрузить БД заказов")
    keyboard.row("Назад")
    return keyboard


def order():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Просмотр Заказчика", "Просмотр Исполнителя", "Просмотр Отзывов")
    keyboard.row("Детали Заказа", "Просмотр Фото", "Просмотр Видео")
    keyboard.row("Выгрузить БД этого заказа")
    keyboard.row("Назад")
    return keyboard


def commission_for_categories():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Цветы", "Подарки", "Кондитерка")
    keyboard.row("Документы", "Погрузка/Разгрузка", "Другое")
    keyboard.row("Назад")
    return keyboard


def about_customers():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("По ID", "По имени", "По username")
    keyboard.row("Просмотреть всех Заказчиков")
    keyboard.row("Назад")
    return keyboard


def about_performers():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("По ID", "По имени")
    keyboard.row("По username", "По телефону")
    keyboard.row("Просмотреть всех Исполнителей")
    keyboard.row("Назад")
    return keyboard


def find_user(performer):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    if performer:
        keyboard.row("Заблокировать", "Разблокировать", "Просмотр профиля")
        keyboard.row("Начислить сумму", "Рейтинг", "Просмотр личных данных")
        keyboard.row("Вернуться в главное меню")
    else:
        keyboard.row("Заблокировать", "Разблокировать")
        keyboard.row("Вернуться в главное меню")
    return keyboard


def block():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Заблокировать", "Разблокировать")
    keyboard.row("Назад")
    return keyboard


def loading_db():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Загрузить БД Заказчиков", "Загрузить БД Исполнителей")
    keyboard.row("Назад")
    return keyboard


def jobs_sales():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Автоотправление сообщений", "Смена на 12 часов")
    keyboard.row("Смена на 1 день", "Смена на 3 дня")
    keyboard.row("Смена на 1 неделю", "Просмотреть все значения")
    keyboard.row("Назад")
    return keyboard


def user_control():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Управление Заказчиками", "Управление Исполнителями")
    keyboard.row("Выгрузка БД Заказчиков и Исполнителей")
    keyboard.row("Назад")
    return keyboard


def advert():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Для Заказчиков", "Для Исполнителей")
    keyboard.row("Назад")
    return keyboard
