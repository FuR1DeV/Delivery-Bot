import calendar
from collections import Counter
from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext

from bot import bot
from data.commands import client_get, client_set
from markups import markup_client
from states import client_states
from settings.config import KEYBOARD


class ClientMain:

    @staticmethod
    async def client_clear(message: types.Message):
        if message.text:
            await bot.delete_message(message.from_user.id, message.message_id)

    @staticmethod
    async def hi_client(callback: types.CallbackQuery):
        client = await client_get.client_select(callback.from_user.id)
        if client:
            client = await client_get.client_select(callback.from_user.id)
            orders = await client_get.client_get_orders(callback.from_user.id)
            await callback.message.edit_text("Профиль Клиента\n"
                                             f"ID - <b>{client.user_id}</b>\n"
                                             f"Username - <b>@{client.username}</b>\n"
                                             f"Телефон - <b>{client.telephone}</b>",
                                             reply_markup=markup_client.client_menu(len(orders)))
        else:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button = types.KeyboardButton(text='Запрос телефона', request_contact=True)
            keyboard.add(button)
            await bot.send_message(callback.from_user.id,
                                   f"{callback.from_user.first_name}\n"
                                   f"Поделитесь с нами вашим номером телефона!",
                                   reply_markup=keyboard)
            await client_states.ClientRegistration.phone.set()

    @staticmethod
    async def client_phone(message: types.Message, state: FSMContext):
        if message.text:
            await state.update_data(phone=message.text)
            await bot.send_message(message.from_user.id,
                                   f"Отлично! Ваш Номер телефона - <b>{message.text}</b>\n"
                                   f"Если это не ваш Номер, можете вручную ввести верный Номер\n"
                                   f"Если все верно, нажмите Начать работу",
                                   reply_markup=markup_client.client_start())
        if message.contact:
            if message.contact.user_id == message.from_user.id:
                await state.update_data(phone=message.contact.phone_number)
                await bot.send_message(message.from_user.id,
                                       f"Отлично! Ваш Номер телефона - <b>{message.contact.phone_number}</b>\n"
                                       f"Если это не ваш Номер, можете вручную ввести верный Номер\n"
                                       f"Если все верно, нажмите Начать работу",
                                       reply_markup=markup_client.client_start())
            else:
                await bot.send_message(message.from_user.id,
                                       "Это не ваш номер телефона! \n"
                                       "Нажмите /start чтобы начать заново")

    @staticmethod
    async def client_start(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        data = await state.get_data()
        await client_set.client_add(callback.from_user.id,
                                    callback.from_user.username,
                                    data.get("phone"))
        await bot.send_message(callback.from_user.id,
                               "Профиль Клиента добавлен!\n"
                               f"ID - <b>{callback.from_user.id}</b>\n"
                               f"Username - <b>{callback.from_user.username}</b>\n"
                               f"Телефон - <b>{data.get('phone')}</b>\n",
                               reply_markup=markup_client.client_menu(False))

    @staticmethod
    async def client_menu(callback: types.CallbackQuery):
        await client_states.ClientClear.client_clear.set()
        client = await client_get.client_select(callback.from_user.id)
        orders = await client_get.client_get_orders(callback.from_user.id)
        await callback.message.edit_text("Главное меню Клиента\n"
                                         f"ID - <b>{client.user_id}</b>\n"
                                         f"Username - <b>@{client.username}</b>\n"
                                         f"Телефон - <b>{client.telephone}</b>",
                                         reply_markup=markup_client.client_menu(len(orders)))

    @staticmethod
    async def client_profile(callback: types.CallbackQuery, state: FSMContext):
        client = await client_get.client_select(callback.from_user.id)
        await callback.message.edit_text("Профиль Клиента\n"
                                         f"Создал Заказов - <b>{client.created_orders}</b>\n"
                                         f"Отменил Заказов - <b>{client.canceled_orders}</b>\n"
                                         f"Завершил Заказов - <b>{client.completed_orders}</b>",
                                         reply_markup=markup_client.client_profile())
