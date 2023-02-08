import logging
from aiogram import types
from aiogram.dispatcher import FSMContext

from bot import bot
from data.commands import performers_get, performers_set
from markups import markup_performer
from settings import config
from states import performer_states


class PerformerHelp:
    logger = logging.getLogger("bot.handler_performer.performer_help")

    @staticmethod
    async def performer_help(message: types.Message):
        PerformerHelp.logger.debug(f"Функция отправки сообщения от исполнителя {message.from_user.id} в тех поддержку")
        if message.text == "Закрытый чат курьеров":
            await bot.send_message(message.from_user.id,
                                   "Вы хотите вступить в закрытый чат курьеров\n"
                                   "С вашего баланса спишется <b>300 рублей</b>",
                                   reply_markup=markup_performer.private_chat_pay())
        if message.text == "Загрузить Фото":
            await bot.send_message(message.from_user.id,
                                   "Загрузите фото",
                                   reply_markup=markup_performer.cancel())
            await performer_states.PerformerHelp.upload_photo.set()
        if message.text == "Загрузить Видео":
            await bot.send_message(message.from_user.id,
                                   "Загрузите видео",
                                   reply_markup=markup_performer.cancel())
            await performer_states.PerformerHelp.upload_video.set()
        if message.text == "Завершить":
            await bot.send_message(message.from_user.id,
                                   "Все сообщения в службу поддержки отправлены!")
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu())
            await performer_states.PerformerStart.performer_menu.set()
        if message.text == "Вернуться главное меню":
            await bot.send_message(message.from_user.id,
                                   "Вы вошли в главное меню заказчика")
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu())
            await performer_states.PerformerStart.performer_menu.set()
        if message.text != "Загрузить Фото" and message.text != "Загрузить Видео" \
                and message.text != "Завершить" and message.text != "Вернуться главное меню" \
                and message.text != "Закрытый чат курьеров":
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя исполнителя {message.from_user.first_name}\n"
                                   f"ID исполнителя {message.from_user.id}\n"
                                   f"Сообщение от исполнителя - <b>{message.text}</b>\n")
            await bot.send_message(message.from_user.id, "Сообщение доставлено в техподдержку!")

    @staticmethod
    async def performer_upload_photo(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            user_status_chat = data.get("user_status_chat")
        PerformerHelp.logger.debug(f"Функция отправки фото от исполнителя {message.from_user.id} в тех поддержку")
        if message.content_type == "photo":
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя исполнителя {message.from_user.first_name}\n"
                                   f"ID исполнителя {message.from_user.id}\n"
                                   f"Фото исполнителя {config.KEYBOARD.get('DOWNWARDS_BUTTON')}")
            await bot.send_photo('@FlowWorkDeliveryHelp',
                                 message.photo[2].file_id)
            await bot.send_message(message.from_user.id,
                                   'Фотография успешно отправлена в тех поддержку!',
                                   reply_markup=markup_performer.photo_or_video_help(user_status_chat))
            await performer_states.PerformerHelp.help.set()
        else:
            await bot.send_message(message.from_user.id,
                                   "Вы отменили загрузку",
                                   reply_markup=markup_performer.photo_or_video_help(user_status_chat))
            await performer_states.PerformerHelp.help.set()

    @staticmethod
    async def performer_upload_video(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            user_status_chat = data.get("user_status_chat")
        PerformerHelp.logger.debug(f"Функция отправки видео от исполнителя {message.from_user.id} в тех поддержку")
        if message.content_type == "video":
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя исполнителя {message.from_user.first_name}\n"
                                   f"ID исполнителя {message.from_user.id}\n"
                                   f"Видео исполнителя {config.KEYBOARD.get('DOWNWARDS_BUTTON')}")
            await bot.send_video('@FlowWorkDeliveryHelp',
                                 message.video.file_id)
            await bot.send_message(message.from_user.id,
                                   'Видео успешно отправлена в тех поддержку!',
                                   reply_markup=markup_performer.photo_or_video_help(user_status_chat))
            await performer_states.PerformerHelp.help.set()
        else:
            await bot.send_message(message.from_user.id,
                                   "Вы отменили загрузку",
                                   reply_markup=markup_performer.photo_or_video_help(user_status_chat))
            await performer_states.PerformerHelp.help.set()

    @staticmethod
    async def performer_private_chat(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await performers_set.private_chat_money(callback.from_user.id)
        res = await performers_get.performer_select(callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               "<b>С вас списалось 300 рублей!</b>")
        await bot.send_message('@FlowWorkDeliveryHelp',
                               f"{config.KEYBOARD.get('DOLLAR') * 10}\n"
                               f"<b>Вступил в закрытый чат:</b>\n"
                               f"Имя исполнителя {callback.from_user.first_name}\n"
                               f"ID исполнителя {callback.from_user.id}\n"
                               f"Username @{res.username}\n"
                               f"Телефон {res.telephone}\n"
                               f"{config.KEYBOARD.get('DOLLAR') * 10}")
        await bot.send_message(callback.from_user.id,
                               "<b>Перейдите по ссылке ниже</b>\n"
                               f"{config.PRIVATE_CHAT_LINK}")
