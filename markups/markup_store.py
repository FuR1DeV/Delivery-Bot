from aiogram import types
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from settings.config import KEYBOARD

markup_clean = ReplyKeyboardRemove()


def back():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
    return keyboard


def start_store():
    menu = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text="Начать работу", callback_data="start_store")
    menu.insert(yes)
    return menu


def store_menu():
    menu = InlineKeyboardMarkup()
    profile = InlineKeyboardButton(text="Профиль", callback_data="store_profile")
    find_orders = InlineKeyboardButton(text="Найти заказы", callback_data="store_find_orders")
    my_orders = InlineKeyboardButton(text="Мои заказы", callback_data="store_orders")
    menu.row(profile, find_orders)
    menu.row(my_orders)
    return menu


def store_profile():
    menu = InlineKeyboardMarkup()
    profile = InlineKeyboardButton(text="Статистика", callback_data="store_statistics")
    back_ = InlineKeyboardButton(text="<< В главное меню", callback_data="store_main_menu")
    menu.row(profile)
    menu.row(back_)
    return menu
