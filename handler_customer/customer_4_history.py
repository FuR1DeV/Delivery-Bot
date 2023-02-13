from aiogram import types
from aiogram.dispatcher import FSMContext

from bot import bot
from data.commands import customers_get, performers_get
from markups import markup_customer
from states import customer_states
from settings import config
from settings.config import KEYBOARD


class CustomerHistory:
    @staticmethod
    async def history(message: types.Message, state: FSMContext):
        if "Вернуться в главное меню" in message.text:
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
            await customer_states.CustomerStart.customer_menu.set()
        else:
            completed = await customers_get.customer_get_complete_order(message.text)
            async with state.proxy() as data:
                data["order_id"] = completed.order_id
                data[completed.order_id] = completed
            await customer_states.CustomerHistory.order_history.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вошли в историю заказа",
                                   reply_markup=markup_customer.details_task_history())

    @staticmethod
    async def order_history(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order = data.get(data.get("order_id"))
        performer_res = await performers_get.performer_select(order.in_work)
        if "Позвонить исполнителю" in message.text:
            await bot.send_message(message.from_user.id,
                                   f"Позвоните исполнителю {performer_res.telephone}")
        if "Написать исполнителю" in message.text:
            await bot.send_message(message.from_user.id,
                                   f"Напишите через телеграмм вот его никнейм @{performer_res.username}")
        if "Детали заказа" in message.text:
            category = {f"Цветы": f"{KEYBOARD.get('BOUQUET')}",
                        f"Подарки": f"{KEYBOARD.get('WRAPPED_GIFT')}",
                        f"Кондитерка": f"{KEYBOARD.get('SHORTCAKE')}",
                        f"Документы": f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')}",
                        f"Погрузка/Разгрузка": f"{KEYBOARD.get('ARROWS_BUTTON')}",
                        f"Другое": f"{KEYBOARD.get('INPUT_LATIN_LETTERS')}"}
            icon_category = None
            icon = None
            p_status = None
            for k, v in category.items():
                if order.category_delivery == k:
                    icon_category = v
            if order.performer_category == "pedestrian":
                p_status = "Пешеход"
                icon = f"{config.KEYBOARD.get('PERSON_RUNNING')}"
            if order.performer_category == "scooter":
                p_status = "На самокате"
                icon = f"{config.KEYBOARD.get('KICK_SCOOTER')}"
            if order.performer_category == "car":
                p_status = "На машине"
                icon = f"{config.KEYBOARD.get('AUTOMOBILE')}"
            elif order.performer_category == "any":
                p_status = "Любой"
                icon = f"{config.KEYBOARD.get('AUTOMOBILE')}" \
                       f"{config.KEYBOARD.get('KICK_SCOOTER')}" \
                       f"{config.KEYBOARD.get('PERSON_RUNNING')}"
            await customer_states.CustomerHistory.order_history_details.set()
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"<b>Детали заказа</b>\n"
                                   f"{icon_category} "
                                   f"Категория - <b>{order.category_delivery}</b>\n"
                                   f"{config.KEYBOARD.get('A_BUTTON')} "
                                   f"Откуда - <a href='https://yandex.ru/maps/?text="
                                   f"{'+'.join(order.geo_position_from.split())}'>{order.geo_position_from}</a>\n"
                                   f"{config.KEYBOARD.get('B_BUTTON')} "
                                   f"Куда - <a href='https://yandex.ru/maps/?text="
                                   f"{'+'.join(order.geo_position_to.split())}'>{order.geo_position_to}</a>\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} "
                                   f"Описание - <b>{order.description}</b>\n"
                                   f"{config.KEYBOARD.get('DOLLAR')} "
                                   f"Цена - <b>{order.price}</b>\n"
                                   f"{config.KEYBOARD.get('MONEY_BAG')} "
                                   f"Ценность вашего товара - <b>{order.order_worth}</b>\n"
                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                   f"ID заказа - <b>{order.order_id}</b>\n"
                                   f"{icon} "
                                   f"Исполнитель - <b>{p_status}</b>\n"
                                   f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                   f"Заказ создан: <b>{order.order_create}</b>\n"
                                   f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
                                   f"Заказ взят: <b>{order.order_get}</b>\n"
                                   f"{config.KEYBOARD.get('BLUE_CIRCLE')} "
                                   f"Заказ завершен: <b>{order.order_end}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   reply_markup=markup_customer.details_task_history_details_order(),
                                   disable_web_page_preview=True)
        if "Профиль исполнителя" in message.text:
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"Профиль <b>Исполнителя</b>:\n"
                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                   f"ID: <b>{performer_res.user_id}</b>\n"
                                   f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                   f"Никнейм <b>@{performer_res.username}</b>\n"
                                   f"{config.KEYBOARD.get('TELEPHONE')} "
                                   f"Номер <b>{performer_res.telephone}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Имя <b>{performer_res.first_name}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Фамилия <b>{performer_res.last_name}</b>\n"
                                   f"{config.KEYBOARD.get('STAR')} "
                                   f"Рейтинг <b>"
                                   f"{performer_res.performer_rating}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   )
        if "Вернуться в главное меню" in message.text:
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
            await customer_states.CustomerStart.customer_menu.set()

    @staticmethod
    async def order_details(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order = data.get(data.get("order_id"))
        if message.text == "Посмотреть фото":
            if order.image:
                await bot.send_photo(message.from_user.id, order.image)
            else:
                await bot.send_message(message.from_user.id, "В вашем заказе нет фото")
        if message.text == "Посмотреть видео":
            if order.video:
                await bot.send_video(message.from_user.id, order.video)
            else:
                await bot.send_message(message.from_user.id, "В вашем заказе нет видео")
        if "Назад в детали заказа" in message.text:
            await customer_states.CustomerHistory.order_history.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в детали заказа",
                                   reply_markup=markup_customer.details_task_history())
