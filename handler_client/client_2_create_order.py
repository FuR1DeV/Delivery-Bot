import calendar
from collections import Counter
from datetime import datetime
from random import randint

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
        await callback.message.edit_text("Отправьте мне сообщением Описание заказа, потом вы сможете отправить Фото\n"
                                         "Или вернитесь в Главное меню",
                                         reply_markup=markup_client.client_back_main_menu())
        await client_states.ClientCreateOrder.create_order_text.set()

    @staticmethod
    async def client_create_order_text(message: types.Message, state: FSMContext):
        if message.photo:
            await bot.delete_message(message.from_user.id, message.message_id)
        if message.text:
            await state.update_data(description=message.text,
                                    order_create=message.date)
            await bot.delete_message(message.from_user.id, message.message_id)
            await bot.delete_message(message.from_user.id, message.message_id - 1)
            await bot.send_message(message.from_user.id,
                                   f"Отлично! ваше Описание\n\n"
                                   f"{message.text}\n\n"
                                   f"Если в Описании вы допустили ошибку\n"
                                   f"Вы можете написать еще раз Описание и отправить мне сообщением\n"
                                   f"Если Описание вас устраивает нажимайте <b>Далее >></b>",
                                   reply_markup=markup_client.client_create_order_photo())

    @staticmethod
    async def client_create_order_photo(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text("Теперь можете добавить Фото\n"
                                         "Или нажмите на кнопку Завершить, если Заказ без Фото",
                                         reply_markup=markup_client.client_create_order_finish())
        await client_states.ClientCreateOrder.create_order_photo.set()
        async with state.proxy() as data:
            data["image"] = []
            data["media"] = types.MediaGroup()

    @staticmethod
    async def client_create_order_photo_add(message: types.Message, state: FSMContext):
        if message.text:
            await bot.delete_message(message.from_user.id, message.message_id)
        if message.photo:
            async with state.proxy() as data:
                data.get("image").append(message.photo[2].file_id)
                await bot.delete_message(message.from_user.id, message.message_id)
                for i in range(1, 5):
                    try:
                        await bot.delete_message(message.from_user.id, message.message_id - i)
                    except:
                        pass
                for i in data.get("image"):
                    data.get("media").attach_photo(i)
                await bot.send_media_group(message.from_user.id,
                                           media=data.get("media"))
                await bot.send_message(message.from_user.id,
                                       f"Ваше Описание\n"
                                       f"{data.get('description')}\n"
                                       f"Можете добавить еще фото или нажмите кнопку Завершить",
                                       reply_markup=markup_client.client_create_order_finish())

    @staticmethod
    async def client_create_order_finish(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            await client_set.client_add_order(callback.from_user.id,
                                              data.get("description"),
                                              data.get("image"),
                                              f"{datetime.now().strftime('%m%d')}{randint(1, 99999)}",
                                              data.get("order_create"))
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await client_states.ClientClear.client_clear.set()
        client = await client_get.client_select(callback.from_user.id)
        orders = await client_get.client_get_orders(callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               "Ваш Заказ Создан!\n"
                               "Главное меню Клиента\n"
                               f"ID - <b>{client.user_id}</b>\n"
                               f"Username - <b>@{client.username}</b>\n"
                               f"Телефон - <b>{client.telephone}</b>",
                               reply_markup=markup_client.client_menu(len(orders)))
