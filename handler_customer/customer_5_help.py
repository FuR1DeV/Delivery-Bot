import logging
from aiogram import types

from bot import bot
from data.commands import customers_get
from markups import markup_customer
from states import customer_states


class CustomerHelp:
    logger = logging.getLogger("bot.handler_customer.customer_help")

    @staticmethod
    async def customer_help(message: types.Message):
        if message.text:
            if message.text == "Вернуться главное меню":
                await bot.send_message(message.from_user.id,
                                       "Вы вошли в главное меню заказчика")
                not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                       reply_markup=markup_customer.main_menu())
                await customer_states.CustomerStart.customer_menu.set()
            if message.text != "Вернуться главное меню":
                await bot.send_message('@FlowWorkDeliveryHelp',
                                       f"Имя Заказчика {message.from_user.first_name}\n"
                                       f"ID Заказчика {message.from_user.id}\n"
                                       f"Сообщение от Заказчика - <b>{message.text}</b>\n")
                await bot.send_message(message.from_user.id,
                                       "Сообщение доставлено в техподдержку!",
                                       reply_markup=markup_customer.photo_or_video_help())
        if message.video_note:
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя Заказчика {message.from_user.first_name}\n"
                                   f"ID Заказчика {message.from_user.id}\n")
            await bot.send_video_note('@FlowWorkDeliveryHelp', message.video_note.file_id)
            await bot.send_message(message.from_user.id,
                                   "Видео сообщение доставлено в техподдержку!",
                                   reply_markup=markup_customer.photo_or_video_help())
        if message.voice:
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя Заказчика {message.from_user.first_name}\n"
                                   f"ID Заказчика {message.from_user.id}\n")
            await bot.send_voice('@FlowWorkDeliveryHelp', message.voice.file_id)
            await bot.send_message(message.from_user.id,
                                   "Аудио сообщение доставлено в техподдержку!",
                                   reply_markup=markup_customer.photo_or_video_help())
        if message.photo:
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя Заказчика {message.from_user.first_name}\n"
                                   f"ID Заказчика {message.from_user.id}\n")
            await bot.send_photo('@FlowWorkDeliveryHelp', message.photo[2].file_id)
            await bot.send_message(message.from_user.id,
                                   "Фото доставлено в техподдержку!",
                                   reply_markup=markup_customer.photo_or_video_help())
        if message.video:
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя Заказчика {message.from_user.first_name}\n"
                                   f"ID Заказчика {message.from_user.id}\n")
            await bot.send_video('@FlowWorkDeliveryHelp', message.video.file_id)
            await bot.send_message(message.from_user.id,
                                   "Видео доставлено в техподдержку!",
                                   reply_markup=markup_customer.photo_or_video_help())
