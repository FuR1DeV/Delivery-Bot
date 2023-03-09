import logging
from aiogram import types

from bot import bot
from data.commands import performers_get, performers_set
from markups import markup_performer
from settings import config
from states import performer_states


class PerformerHelp:
    logger = logging.getLogger("bot.handler_performer.performer_help")

    @staticmethod
    async def performer_help(message: types.Message):
        # if message.text == "Закрытый чат курьеров":
        #     await bot.send_message(message.from_user.id,
        #                            "Вы хотите вступить в закрытый чат курьеров\n"
        #                            "С вашего баланса спишется <b>300 рублей</b>",
        #                            reply_markup=markup_performer.private_chat_pay())
        if message.text:
            if message.text == "Вернуться главное меню":
                await bot.send_message(message.from_user.id,
                                       "Вы вошли в главное меню заказчика")
                orders = await performers_get.performer_view_list_orders(message.from_user.id)
                orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                promo = await performers_get.check_commission_promo(message.from_user.id)
                jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                       reply_markup=markup_performer.main_menu(jobs))
                await performer_states.PerformerStart.performer_menu.set()
            if message.text != "Вернуться главное меню":
                await bot.send_message('@FlowWorkDeliveryHelp',
                                       f"Имя исполнителя {message.from_user.first_name}\n"
                                       f"ID исполнителя {message.from_user.id}\n"
                                       f"Сообщение от исполнителя - <b>{message.text}</b>\n")
                await bot.send_message(message.from_user.id,
                                       "Сообщение доставлено в техподдержку!",
                                       reply_markup=markup_performer.photo_or_video_help())
        if message.video_note:
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя исполнителя {message.from_user.first_name}\n"
                                   f"ID исполнителя {message.from_user.id}\n")
            await bot.send_video_note('@FlowWorkDeliveryHelp', message.video_note.file_id)
            await bot.send_message(message.from_user.id,
                                   "Видео сообщение доставлено в техподдержку!",
                                   reply_markup=markup_performer.photo_or_video_help())
        if message.voice:
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя исполнителя {message.from_user.first_name}\n"
                                   f"ID исполнителя {message.from_user.id}\n")
            await bot.send_voice('@FlowWorkDeliveryHelp', message.voice.file_id)
            await bot.send_message(message.from_user.id,
                                   "Аудио сообщение доставлено в техподдержку!",
                                   reply_markup=markup_performer.photo_or_video_help())
        if message.photo:
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя исполнителя {message.from_user.first_name}\n"
                                   f"ID исполнителя {message.from_user.id}\n")
            await bot.send_photo('@FlowWorkDeliveryHelp', message.photo[2].file_id)
            await bot.send_message(message.from_user.id,
                                   "Фото доставлено в техподдержку!",
                                   reply_markup=markup_performer.photo_or_video_help())
        if message.video:
            await bot.send_message('@FlowWorkDeliveryHelp',
                                   f"Имя исполнителя {message.from_user.first_name}\n"
                                   f"ID исполнителя {message.from_user.id}\n")
            await bot.send_video('@FlowWorkDeliveryHelp', message.video.file_id)
            await bot.send_message(message.from_user.id,
                                   "Видео доставлено в техподдержку!",
                                   reply_markup=markup_performer.photo_or_video_help())

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
