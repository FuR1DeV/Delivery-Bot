import logging
from aiogram import types

from bot import bot
from data.commands import customers_get
from markups import markup_customer
from states import customer_states
from settings import config


class CustomerHelp:
    logger = logging.getLogger("bot.handler_customer.customer_help")

    @staticmethod
    async def customer_help(message: types.Message):
        if message.text == "Загрузить Фото":
            await bot.send_message(message.from_user.id,
                                   "Загрузите фото",
                                   reply_markup=markup_customer.cancel())
            await customer_states.CustomerHelp.upload_photo.set()

        if message.text == "Загрузить Видео":
            await bot.send_message(message.from_user.id,
                                   "Загрузите видео",
                                   reply_markup=markup_customer.cancel())
            await customer_states.CustomerHelp.upload_video.set()

        if message.text == "Завершить":
            await bot.send_message(message.from_user.id,
                                   "Все сообщения в службу поддержки отправлены!")
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
            await customer_states.CustomerStart.customer_menu.set()
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
        if message.text != "Загрузить Фото" and message.text != "Загрузить Видео" \
                and message.text != "Завершить" and message.text != "Вернуться главное меню":
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя заказчика {message.from_user.first_name}\n"
                                   f"ID заказчика {message.from_user.id}\n"
                                   f"Сообщение от заказчика - <b>{message.text}</b>\n")
            await bot.send_message(message.from_user.id, "Сообщение доставлено в техподдержку!")

    @staticmethod
    async def customer_upload_photo(message: types.Message):
        if message.content_type == "photo":
            CustomerHelp.logger.debug(f"Функция отправки фото от заказчика {message.from_user.id} в тех поддержку")
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя заказчика {message.from_user.first_name}\n"
                                   f"ID заказчика {message.from_user.id}\n"
                                   f"Фото заказчика {config.KEYBOARD.get('DOWNWARDS_BUTTON')}")
            await bot.send_photo('@FlowWorkDeliveryHelp',
                                 message.photo[2].file_id)
            await bot.send_message(message.from_user.id,
                                   'Фотография успешно отправлена в тех поддержку!',
                                   reply_markup=markup_customer.photo_or_video_help())
            await customer_states.CustomerHelp.help.set()
        else:
            await bot.send_message(message.from_user.id,
                                   "Вы отменили загрузку",
                                   reply_markup=markup_customer.photo_or_video_help())
            await customer_states.CustomerHelp.help.set()

    @staticmethod
    async def customer_upload_video(message: types.Message):
        if message.content_type == "video":
            CustomerHelp.logger.debug(f"Функция отправки видео от заказчика {message.from_user.id} в тех поддержку")
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя заказчика {message.from_user.first_name}\n"
                                   f"ID заказчика {message.from_user.id}\n"
                                   f"Видео заказчика {config.KEYBOARD.get('DOWNWARDS_BUTTON')}")
            await bot.send_video('@FlowWorkDeliveryHelp',
                                 message.video.file_id)
            await bot.send_message(message.from_user.id,
                                   'Видео успешно отправлена в тех поддержку!',
                                   reply_markup=markup_customer.photo_or_video_help())
            await customer_states.CustomerHelp.help.set()
        else:
            await bot.send_message(message.from_user.id,
                                   "Вы отменили загрузку",
                                   reply_markup=markup_customer.photo_or_video_help())
            await customer_states.CustomerHelp.help.set()

