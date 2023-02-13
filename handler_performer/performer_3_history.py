from aiogram import types
from aiogram.dispatcher import FSMContext

from bot import bot
from data.commands import performers_get, customers_get
from markups import markup_performer
from settings import config
from states import performer_states


class PerformerHistory:
    @staticmethod
    async def history(message: types.Message, state: FSMContext):
        if "Вернуться в главное меню" in message.text:
            await performer_states.PerformerStart.performer_menu.set()
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu(jobs))
        else:
            completed = await performers_get.performer_get_complete_order(message.text)
            async with state.proxy() as data:
                data["order_id"] = completed.order_id
                data[completed.order_id] = completed
            await performer_states.PerformerHistory.order_history.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вошли в историю заказа",
                                   reply_markup=markup_performer.details_task_history())

    @staticmethod
    async def order_history(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order = data.get(data.get("order_id"))
        customer_res = await customers_get.customer_select(order.user_id)
        if "Позвонить Заказчику" in message.text:
            await bot.send_message(message.from_user.id,
                                   f"Позвоните заказчику {customer_res.telephone}")
        if "Написать Заказчику" in message.text:
            await bot.send_message(message.from_user.id,
                                   f"Напишите через телеграмм вот его никнейм @{customer_res.username}")
        if "Детали заказа" in message.text:
            await performer_states.PerformerHistory.order_history_details.set()
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"<b>Детали заказа</b>\n"
                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                   f"ID заказа <b>{order.order_id}</b>\n"
                                   f"{config.KEYBOARD.get('A_BUTTON')} "
                                   f"Откуда <b>{order.geo_position_from}</b>\n"
                                   f"{config.KEYBOARD.get('B_BUTTON')} "
                                   f"Куда <b>{order.geo_position_to}</b>\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} "
                                   f"Описание <b>{order.description}</b>\n"
                                   f"{config.KEYBOARD.get('DOLLAR')} "
                                   f"Цена <b>{order.price}</b>\n"
                                   f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                   f"Создан <b>{order.order_create}</b>\n"
                                   f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
                                   f"Взят <b>{order.order_get}</b>\n"
                                   f"{config.KEYBOARD.get('BLUE_CIRCLE')} "
                                   f"Завершен <b>{order.order_end}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}\n",
                                   reply_markup=markup_performer.details_task_history_details_order())
        if "Профиль Заказчика" in message.text:
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"Профиль <b>Заказчика</b>:\n"
                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                   f"ID : <b>{customer_res.user_id}</b>\n"
                                   f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                   f"Никнейм <b>@{customer_res.username}</b>\n"
                                   f"{config.KEYBOARD.get('TELEPHONE')} "
                                   f"Номер <b>{customer_res.telephone}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Имя <b>{customer_res.first_name}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Фамилия <b>{customer_res.last_name}</b>\n"
                                   f"{config.KEYBOARD.get('STAR')} "
                                   f"Рейтинг <b>"
                                   f"{customer_res.customer_rating}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   )
        if "Вернуться в главное меню" in message.text:
            await performer_states.PerformerStart.performer_menu.set()
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu(jobs))

    @staticmethod
    async def order_details(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order = data.get(data.get("order_id"))
        if "Посмотреть фото" in message.text:
            if order.image:
                await bot.send_photo(message.from_user.id, order.image)
            else:
                await bot.send_message(message.from_user.id, "В вашем заказе нет фото")
        if "Посмотреть видео" in message.text:
            if order.video:
                await bot.send_video(message.from_user.id, order.video)
            else:
                await bot.send_message(message.from_user.id, "В вашем заказе нет видео")
        if "Назад в детали заказа" in message.text:
            await performer_states.PerformerHistory.order_history.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в детали заказа",
                                   reply_markup=markup_performer.details_task_history())
