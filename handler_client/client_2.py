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


class ClientCreateOrder:
    @staticmethod
    async def client_create_order(callback: types.CallbackQuery):
        await callback.message.edit_text("Напишите в чат Описание Заказа, что нужно сделать\n"
                                         "Вы так же можете прикрепить Фото",
                                         reply_markup=markup_client.client_back_main_menu())
        await client_states.ClientCreateOrder.create_order.set()

    @staticmethod
    async def client_finish_create_order(message: types.Message, state: FSMContext):
        await bot.send_message(message.from_user.id,
                               f"Вы ввели {message.text}")




