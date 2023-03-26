from aiogram import types
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from settings.config import KEYBOARD

markup_clean = ReplyKeyboardRemove()


def back():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def client_back_main_menu():
    menu = InlineKeyboardMarkup()
    main_menu = InlineKeyboardButton(text="<< В Главное меню",
                                     callback_data="client_main_menu")
    menu.insert(main_menu)
    return menu


def client_start():
    menu = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Начать работу", callback_data="start_client")
    menu.insert(yes)
    return menu


def client_menu(orders):
    menu = InlineKeyboardMarkup()
    profile = InlineKeyboardButton(text="Профиль", callback_data="client_profile")
    create_orders = InlineKeyboardButton(text="Создать заказ", callback_data="client_create_order")
    if orders:
        my_orders = InlineKeyboardButton(text=f"Мои заказы ({orders})", callback_data="client_orders")
    else:
        my_orders = InlineKeyboardButton(text=f"Мои заказы", callback_data="client_orders")
    menu.row(profile, create_orders)
    menu.row(my_orders)
    return menu


def client_profile():
    menu = InlineKeyboardMarkup()
    profile = InlineKeyboardButton(text="Статистика", callback_data="client_statistics")
    back_ = InlineKeyboardButton(text="<< В главное меню", callback_data="client_main_menu")
    menu.row(profile)
    menu.row(back_)
    return menu


def client_create_order_photo():
    menu = InlineKeyboardMarkup()
    profile = InlineKeyboardButton(text="Далее >>", callback_data="client_create_order_photo")
    menu.row(profile)
    return menu


def client_create_order_finish():
    menu = InlineKeyboardMarkup()
    profile = InlineKeyboardButton(text="Завершить", callback_data="client_create_order_finish")
    menu.row(profile)
    return menu
