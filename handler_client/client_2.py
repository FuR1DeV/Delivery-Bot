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
        await callback.message.edit_text("Напишите в чат Описание Заказа, что нужно сделать\n",
                                         reply_markup=markup_client.client_back_main_menu())
        await client_states.ClientCreateOrder.create_order_text.set()

    @staticmethod
    async def client_create_order_text(message: types.Message, state: FSMContext):
        if message.text:
            await state.update_data(description=message.text)
            await bot.delete_message(message.from_user.id, message.message_id)
            await bot.send_message(message.from_user.id,
                                   f"Отлично! ваше Описание\n"
                                   f"{message.text}\n"
                                   f"Если в Описании вы допустили ошибку\n"
                                   f"Вы можете написать еще раз Описание и отправить мне сообщением\n"
                                   f"Если Описание вас устраивает нажимайте <b>Далее >></b>",
                                   reply_markup=markup_client.client_create_order_photo())

    @staticmethod
    async def client_create_order_photo(callback: types.CallbackQuery):
        await callback.message.edit_text("Теперь можете добавить Фото\n"
                                         "Или нажмите на кнопку Завершить, если Заказ без Фото",
                                         reply_markup=markup_client.client_create_order_finish())
        await client_states.ClientCreateOrder.create_order_photo.set()

    @staticmethod
    async def client_create_order_photo_add(message: types.Message):
        if message.text:
            await bot.delete_message(message.from_user.id, message.message_id)
        if message.photo:
            await bot.send_message(message.from_user.id,
                                   "Фото добавлено!",
                                   reply_markup=markup_client.client_create_order_finish())

    @staticmethod
    async def client_create_order_finish(callback: types.CallbackQuery):
        await callback.message.edit_text("Ваш Заказ создан!\n",
                                         reply_markup=markup_client.client_menu())
