import calendar
from collections import Counter
from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext

from bot import bot
from data.commands import store_set, store_get
from markups import markup_store
from states import store_states
from settings.config import KEYBOARD


class StoreMain:
    @staticmethod
    async def hi_store(callback: types.CallbackQuery):
        store = await store_get.store_select(callback.from_user.id)
        if store:
            await store_states.StoreStart.store_menu.set()
            store = await store_get.store_select(callback.from_user.id)
            await callback.message.edit_text("Ваш магазин\n"
                                             f"ID - <b>{store.user_id}</b>\n"
                                             f"Username - <b>@{store.username}</b>\n"
                                             f"Телефон - <b>{store.telephone}</b>\n"
                                             f"Название - <b>{store.store_name}</b>\n"
                                             f"Рейтинг - <b>{store.rating}</b>",
                                             reply_markup=markup_store.store_menu())
        else:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button = types.KeyboardButton(text='Запрос телефона', request_contact=True)
            keyboard.add(button)
            await bot.send_message(callback.from_user.id,
                                   f"{callback.from_user.first_name}\n"
                                   f"Поделитесь с нами вашим номером телефона!",
                                   reply_markup=keyboard)
            await store_states.StoreRegistration.phone.set()

    @staticmethod
    async def store_phone(message: types.Message, state: FSMContext):
        if message.text:
            await state.update_data(phone=message.text)
            await bot.send_message(message.from_user.id,
                                   f"Отлично! Ваш Номер телефона - <b>{message.text}</b>\n"
                                   f"Если это не ваш Номер, можете вернуться назад и ввести верный Номер\n"
                                   f"Если всё верно введите <b>Название</b> вашего <b>Магазина</b>",
                                   reply_markup=markup_store.back())
            await store_states.StoreRegistration.next()
        if message.contact:
            if message.contact.user_id == message.from_user.id:
                await state.update_data(phone=message.contact.phone_number)
                await bot.send_message(message.from_user.id,
                                       f"Отлично! Ваш Номер телефона - <b>{message.contact.phone_number}</b>\n"
                                       f"Если это не ваш Номер, можете вернуться назад и ввести верный Номер\n"
                                       f"Если всё верно введите <b>Название</b> вашего <b>Магазина</b>",
                                       reply_markup=markup_store.back())
                await store_states.StoreRegistration.next()
            else:
                await bot.send_message(message.from_user.id,
                                       "Это не ваш номер телефона! \n"
                                       "Нажмите /start чтобы начать заново")

    @staticmethod
    async def store_name(message: types.Message, state: FSMContext):
        if message.text:
            if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                await state.update_data(store_name=message.text)
                await bot.send_message(message.from_user.id,
                                       f"Отлично! Название вашего Магазина - <b>{message.text}</b>\n"
                                       f"Если это не верно, то можете еще раз написать Название вашего Магазина\n"
                                       f"Если все верно, нажмите кнопку <b>Начать работу </b>",
                                       reply_markup=markup_store.start_store())
            if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                await store_states.StoreRegistration.phone.set()
                await bot.send_message(message.from_user.id,
                                       "Введите номер телефона",
                                       reply_markup=markup_store.markup_clean)

    @staticmethod
    async def store_start(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        data = await state.get_data()
        await store_set.store_add(callback.from_user.id,
                                  callback.from_user.username,
                                  data.get("phone"),
                                  data.get("store_name"))
        await bot.send_message(callback.from_user.id,
                               "Ваш магазин добавлен!\n"
                               f"ID - <b>{callback.from_user.id}</b>\n"
                               f"Username - <b>{callback.from_user.username}</b>\n"
                               f"Телефон - <b>{data.get('phone')}</b>\n"
                               f"Название - <b>{data.get('store_name')}</b>\n"
                               f"Рейтинг - <b>5</b>",
                               reply_markup=markup_store.store_menu())

    @staticmethod
    async def store_menu(callback: types.CallbackQuery):
        store = await store_get.store_select(callback.from_user.id)
        await callback.message.edit_text("Ваш магазин\n"
                                         f"ID - <b>{store.user_id}</b>\n"
                                         f"Username - <b>@{store.username}</b>\n"
                                         f"Телефон - <b>{store.telephone}</b>\n"
                                         f"Название - <b>{store.store_name}</b>\n"
                                         f"Рейтинг - <b>{store.rating}</b>",
                                         reply_markup=markup_store.store_menu())

    @staticmethod
    async def store_profile(callback: types.CallbackQuery, state: FSMContext):
        store = await store_get.store_select(callback.from_user.id)
        await callback.message.edit_text("Ваш магазин\n"
                                         f"ID - <b>{store.user_id}</b>\n"
                                         f"Username - <b>@{store.username}</b>\n"
                                         f"Телефон - <b>{store.telephone}</b>\n"
                                         f"Название - <b>{store.store_name}</b>\n"
                                         f"Рейтинг ds - <b>{store.rating}</b>"
                                         f"ID - <b>{store.user_id}</b>\n"
                                         f"Username - <b>@{store.username}</b>\n"
                                         f"Телефон - <b>{store.telephone}</b>\n"
                                         f"Название - <b>{store.store_name}</b>\n"
                                         f"Рейтинг ds - <b>{store.rating}</b>",
                                         reply_markup=markup_store.store_profile())
