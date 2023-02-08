from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from geopy.geocoders import Nominatim

from bot import bot
from data.commands import customers_get, customers_set, performers_get, general_get
from markups import markup_customer
from states import customer_states
from settings import config
from settings.config import KEYBOARD


class CustomerDetailsTasks:
    @staticmethod
    async def customer_details(message: types.Message, state: FSMContext):
        if "Назад" in message.text:
            orders_not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            orders = await customers_get.customer_all_orders_in_work(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад",
                                   reply_markup=markup_customer.orders_type_work(len(orders_not_at_work),
                                                                                 len(orders)))
            await customer_states.CustomerStart.orders.set()
        else:
            orders = None
            in_work = None
            loading = None
            try:
                """Когда пользователь нажимает кнопку заказа (order_id) здесь мы сохраняем order_id в памяти
                а потом проверяем взял ли этот заказ Исполнитель"""
                async with state.proxy() as data:
                    msg = message.text.split()[1]
                    data["order_id"] = msg
                try:
                    in_work = await customers_get.customer_in_work_order(msg)
                    orders = await customers_get.customer_all_orders(message.from_user.id)
                    loading = 0
                except AttributeError:
                    in_work = await customers_get.customer_in_work_order_loading(msg)
                    orders = await customers_get.customer_all_orders_loading(message.from_user.id)
                    loading = 1
                async with state.proxy() as data:
                    data["user_id"] = in_work
            except IndexError:
                pass
            if in_work:
                for i in orders:
                    if i.order_id == msg:
                        await customer_states.CustomerDetailsTasks.enter_task.set()
                        await bot.send_message(message.from_user.id,
                                               "Вы вошли в детали этого заказа",
                                               reply_markup=markup_customer.details_task())
            elif in_work is None:
                await bot.send_message(message.from_user.id,
                                       "Откройте клавиатуру и нажмите на ID вашего заказа")
            else:
                for i in orders:
                    if i.order_id == msg:
                        if loading == 0:
                            await customer_states.CustomerDetailsTasks.not_at_work.set()
                            await bot.send_message(message.from_user.id,
                                                   "Ваш Заказ еще не взяли, но его можно отредактировать или отменить",
                                                   reply_markup=markup_customer.details_task_not_at_work())
                        if loading == 1:
                            await customer_states.CustomerDetailsTasks.loading.set()
                            await bot.send_message(message.from_user.id,
                                                   "Вы вошли в заказ с типом Погрузка/Разгрузка",
                                                   reply_markup=markup_customer.details_task_loading())

    @staticmethod
    async def detail_task(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            res_performer = await performers_get.performer_select(data.get("user_id"))
            res_order = await general_get.order_select(data.get("order_id"))
        if "Написать/Позвонить исполнителю" in message.text:
            res = await customers_get.customer_get_status_order(data.get("order_id"))
            if res is None:
                not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                       reply_markup=markup_customer.main_menu())
                await customer_states.CustomerStart.customer_menu.set()
            else:
                await bot.send_message(message.from_user.id,
                                       f"Вот его номер телефона {res_performer.telephone}\n"
                                       f"Или напишите ему в телеграм @{res_performer.username}")
        if "Детали заказа" in message.text:
            res = await customers_get.customer_get_status_order(data.get("order_id"))
            if res is None:
                not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                       reply_markup=markup_customer.main_menu())
                await customer_states.CustomerStart.customer_menu.set()
            else:
                if res_order.image:
                    await bot.send_photo(message.from_user.id, res_order.image)
                if res_order.video:
                    await bot.send_video(message.from_user.id, res_order.video)
                await bot.send_message(message.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"<b>Детали заказа</b>\n"
                                       f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                       f"Категория - <b>{res_order.category_delivery}</b>\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID заказа - <b>{res_order.order_id}</b>\n"
                                       f"{config.KEYBOARD.get('A_BUTTON')} "
                                       f"Откуда - <a href='https://yandex.ru/maps/?text="
                                       f"{'+'.join(res_order.geo_position_from.split())}'>"
                                       f"{res_order.geo_position_from}</a>\n"
                                       f"{config.KEYBOARD.get('B_BUTTON')} "
                                       f"Куда - <a href='https://yandex.ru/maps/?text="
                                       f"{'+'.join(res_order.geo_position_to.split())}'>"
                                       f"{res_order.geo_position_to}</a>\n"
                                       f"{config.KEYBOARD.get('INFORMATION')} "
                                       f"Название - <b>{res_order.title}</b>\n"
                                       f"{config.KEYBOARD.get('CLIPBOARD')} "
                                       f"Описание - <b>{res_order.description}</b>\n"
                                       f"{config.KEYBOARD.get('DOLLAR')} "
                                       f"Цена - <b>{res_order.price}</b>\n"
                                       f"{config.KEYBOARD.get('MONEY_BAG')} "
                                       f"Ценность вашего товара - <b>{res_order.order_worth}</b>\n"
                                       f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                       f"Создан <b>{res_order.order_create}</b>\n"
                                       f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
                                       f"Взят <b>{res_order.order_get}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}\n",
                                       disable_web_page_preview=True)
        if "Статус заказа" in message.text:
            res = await customers_get.customer_get_status_order(data.get("order_id"))
            if res is None:
                not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                       reply_markup=markup_customer.main_menu())
                await customer_states.CustomerStart.customer_menu.set()
            else:
                await bot.send_message(message.from_user.id,
                                       "Вы вошли в статус заказа, тут вы можете завершить заказ "
                                       "или проверить статус заказа для его закрытия",
                                       reply_markup=markup_customer.details_task_status())
                await customer_states.CustomerDetailsTasksStatus.enter_status.set()
        if "Профиль исполнителя" in message.text:
            res = await customers_get.customer_get_status_order(data.get("order_id"))
            if res is None:
                not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                       reply_markup=markup_customer.main_menu())
                await customer_states.CustomerStart.customer_menu.set()
            else:
                await bot.send_message(message.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"Профиль <b>Исполнителя</b>:\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID: <b>{res_performer.user_id}</b>\n"
                                       f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                       f"Никнейм <b>@{res_performer.username}</b>\n"
                                       f"{config.KEYBOARD.get('TELEPHONE')} "
                                       f"Номер <b>{res_performer.telephone}</b>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Имя <b>{res_performer.first_name}</b>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Фамилия <b>{res_performer.last_name}</b>\n"
                                       f"{config.KEYBOARD.get('STAR')} "
                                       f"Рейтинг <b>{res_performer.performer_rating}</b>\n"
                                       f"{config.KEYBOARD.get('CHECK_BOX_WITH_CHECK')} "
                                       f"Заказов взял - <b>{res_performer.get_orders}</b>\n"
                                       f"{config.KEYBOARD.get('CROSS_MARK')} "
                                       f"Заказов отменил - <b>{res_performer.canceled_orders}</b>\n"
                                       f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                       f"Заказов выполнил - <b>{res_performer.completed_orders}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}",
                                       )
        if "Назад" in message.text:
            orders_not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            orders_at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            await customer_states.CustomerStart.orders.set()
            await bot.send_message(message.from_user.id,
                                   "Выберите тип заказа",
                                   reply_markup=markup_customer.orders_type_work(len(orders_not_at_work),
                                                                                 len(orders_at_work)))
        if "Вернуться в главное меню" in message.text:
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
            await customer_states.CustomerStart.customer_menu.set()

    @staticmethod
    async def detail_task_not_at_work(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            orders = await general_get.order_select(data.get("order_id"))
        if "Отменить заказ" in message.text:
            if orders:
                if orders.in_work == 0:
                    await bot.send_message(message.from_user.id,
                                           "Вы хотите отменить заказ ?",
                                           reply_markup=markup_customer.inline_cancel_task())
                else:
                    await customer_states.CustomerStart.customer_menu.set()
                    await bot.send_message(message.from_user.id,
                                           "Ваш заказ уже взяли!")
                    not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                    at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                    loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                           reply_markup=markup_customer.main_menu())
        if "Редактировать заказ" in message.text:
            if orders:
                if orders.in_work == 0:
                    await bot.send_message(message.from_user.id,
                                           "Вы хотите редактировать заказ ?\n"
                                           "<b>Ваш заказ будет заблокирован до тех "
                                           "пор пока вы не закончите редактировать заказ!</b>",
                                           reply_markup=markup_customer.inline_change_task())
                else:
                    await customer_states.CustomerStart.customer_menu.set()
                    await bot.send_message(message.from_user.id,
                                           "Ваш заказ уже взяли!")
                    not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                    at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                    loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                           reply_markup=markup_customer.main_menu())
        if "Назад" in message.text:
            orders_not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            orders_at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            orders_loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await customer_states.CustomerStart.orders.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в меню выбора типов Заказа",
                                   reply_markup=markup_customer.customer_type_orders(len(orders_not_at_work),
                                                                                     len(orders_at_work),
                                                                                     len(orders_loading)))

    @staticmethod
    async def details_task_loading(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            orders_loading = await general_get.order_select_loading(data.get("order_id"))
        if message.text == f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Нашли всех грузчиков":
            await bot.send_message(message.from_user.id,
                                   "Вы точно нашли всех грузчиков ?",
                                   reply_markup=markup_customer.inline_get_all_people_loading())
        if message.text == f"{KEYBOARD.get('HAMMER_AND_PICK')} Редактировать заказ":
            if orders_loading:
                if orders_loading.in_work == 0:
                    await bot.send_message(message.from_user.id,
                                           "Вы хотите редактировать заказ ?\n"
                                           "<b>Ваш заказ будет заблокирован до тех "
                                           "пор пока вы не закончите редактировать заказ!</b>",
                                           reply_markup=markup_customer.inline_change_task())
                else:
                    await customer_states.CustomerStart.customer_menu.set()
                    await bot.send_message(message.from_user.id,
                                           "Ваш заказ уже взяли!")
                    not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                    at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                    loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                           reply_markup=markup_customer.main_menu())
        if message.text == f"{KEYBOARD.get('BUST_IN_SILHOUETTE')} Список Грузчиков":
            loaders = [await performers_get.performer_select(v) for v in orders_loading.persons_list]
            if loaders:
                for i in loaders:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"Профиль <b>Исполнителя</b>:\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID: <b>{i.user_id}</b>\n"
                                           f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                           f"Никнейм <b>@{i.username}</b>\n"
                                           f"{config.KEYBOARD.get('TELEPHONE')} "
                                           f"Номер <b>{i.telephone}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Имя <b>{i.first_name}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Фамилия <b>{i.last_name}</b>\n"
                                           f"{config.KEYBOARD.get('STAR')} "
                                           f"Рейтинг <b>{i.performer_rating}</b>\n"
                                           f"{config.KEYBOARD.get('CHECK_BOX_WITH_CHECK')} "
                                           f"Заказов взял - <b>{i.get_orders}</b>\n"
                                           f"{config.KEYBOARD.get('CROSS_MARK')} "
                                           f"Заказов отменил - <b>{i.canceled_orders}</b>\n"
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                           f"Заказов выполнил - <b>{i.completed_orders}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}",
                                           reply_markup=markup_customer.inline_delete_loader())
            else:
                await bot.send_message(message.from_user.id,
                                       "Пока грузчиков нет!")
        if message.text == f"{KEYBOARD.get('CLIPBOARD')} Детали заказа":
            if orders_loading.image:
                await bot.send_photo(message.from_user.id, orders_loading.image)
            if orders_loading.video:
                await bot.send_video(message.from_user.id, orders_loading.video)
            loaders = [await performers_get.performer_select(v) for v in orders_loading.persons_list]
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"<b>Детали заказа для Грузчиков</b>\n"
                                   f"{config.KEYBOARD.get('A_BUTTON')} "
                                   f"Откуда - <a href='https://yandex.ru/maps/?text="
                                   f"{'+'.join(orders_loading.geo_position.split())}'>"
                                   f"{orders_loading.geo_position}</a>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Сколько Грузчиков - <b>{orders_loading.person}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Уже Грузчиков - <b>{orders_loading.count_person}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Грузчики: <b>{' | '.join([k.username for k in loaders])}</b>\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} "
                                   f"Описание - <b>{orders_loading.description}</b>\n"
                                   f"{config.KEYBOARD.get('DOLLAR')} "
                                   f"Цена за 1 час - <b>{orders_loading.price}</b>\n"
                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                   f"ID заказа - <b>{orders_loading.order_id}</b>\n"
                                   f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                   f"Заказ создан: <b>{orders_loading.order_create}</b>\n"
                                   f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                   f"Действует до: <b>{orders_loading.order_expired}</b>\n"
                                   f"{config.KEYBOARD.get('BAR_CHART')} "
                                   f"Рейтинг заказа | <b>{orders_loading.order_rating}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}\n",
                                   disable_web_page_preview=True)
        if message.text == f"{KEYBOARD.get('CHECK_MARK_BUTTON')} Завершить заказ":
            await bot.send_message(message.from_user.id,
                                   "Подтвердите завершение заказа",
                                   reply_markup=markup_customer.inline_close_loading_task())
        if "Назад" in message.text:
            orders_not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            orders = await customers_get.customer_all_orders_in_work(message.from_user.id)
            orders_loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await customer_states.CustomerStart.orders.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в меню выбора типов Заказа",
                                   reply_markup=markup_customer.customer_type_orders(len(orders_not_at_work),
                                                                                     len(orders),
                                                                                     len(orders_loading)))

    @staticmethod
    async def close_loading_order(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            order_loading = await customers_get.customer_view_order(data.get('order_id'))
            await customers_set.customer_close_order_loading(callback.from_user.id,
                                                             data.get('order_id'),
                                                             datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
        await customer_states.CustomerStart.customer_menu.set()
        await bot.send_message(callback.from_user.id,
                               "Заказ закрыт")
        not_at_work = await customers_get.customer_all_orders_not_at_work(callback.from_user.id)
        at_work = await customers_get.customer_all_orders_in_work(callback.from_user.id)
        loading = await customers_get.customer_all_orders_loading(callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                               reply_markup=markup_customer.main_menu())
        for i in order_loading[0].persons_list:
            await bot.send_message(i,
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 10}\n"
                                   f"<b>Заказ Погрузка/Разгрузка завершен!</b>\n"
                                   f"ID: {order_loading[0].order_id}\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 10}")

    @staticmethod
    async def no_close_loading_order(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)

    @staticmethod
    async def cancel_order_not_at_work(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            await customers_set.customer_cancel_order(data.get("order_id"), callback.from_user.id)
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await customer_states.CustomerStart.customer_menu.set()
        await bot.send_message(callback.from_user.id,
                               "Вы отменили заказ!")
        not_at_work = await customers_get.customer_all_orders_not_at_work(callback.from_user.id)
        at_work = await customers_get.customer_all_orders_in_work(callback.from_user.id)
        loading = await customers_get.customer_all_orders_loading(callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                               reply_markup=markup_customer.main_menu())

    @staticmethod
    async def no_cancel_order_not_at_work(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await customer_states.CustomerDetailsTasks.not_at_work.set()
        await bot.send_message(callback.from_user.id,
                               "Ваш Заказ еще не взяли, но его можно отредактировать или отменить",
                               reply_markup=markup_customer.details_task_not_at_work())

    @staticmethod
    async def no_change_order_not_at_work(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)

    @staticmethod
    async def dismiss_loader(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        user_id = callback.message.text.split()[5]
        await bot.send_message(callback.from_user.id,
                               "Вы действительно хотите уволить этого Грузчика ?",
                               reply_markup=markup_customer.inline_delete_loader_approve(user_id))

    @staticmethod
    async def dismiss_loader_approve(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        user_id = callback.data[22:]
        async with state.proxy() as data:
            order_id = data.get("order_id")
            await customers_set.customer_delete_loader(user_id, order_id)
        await bot.send_message(callback.from_user.id,
                               "Грузчик был уволен!")
        await bot.send_message(user_id,
                               f"{config.KEYBOARD.get('CROSS_MARK') * 10}\n"
                               f"<b>ВНИМАНИЕ!</b>\n"
                               f"<b>Вы были уволены из Заказа Погрузки/Разгрузки</b>\n"
                               f"<b>ID заказа - {order_id}</b>\n"
                               f"{config.KEYBOARD.get('CROSS_MARK') * 10}")


class CustomerDetailsTasksChange:
    @staticmethod
    async def change_task_enter(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            res = await customers_set.customer_set_block_order(data.get("order_id"), 1)
        if res == "order":
            await bot.send_message(callback.from_user.id,
                                   "<b>Ваш заказ временно заблокирован!</b>\n"
                                   "Что будем менять ?",
                                   reply_markup=markup_customer.details_task_change())
            await customer_states.CustomerChangeOrder.enter.set()
        if res == "order_loading":
            await bot.send_message(callback.from_user.id,
                                   "<b>Ваш заказ временно заблокирован!</b>\n"
                                   "Что будем менять ?",
                                   reply_markup=markup_customer.details_task_change_loading())
            await customer_states.CustomerChangeOrder.enter.set()

    @staticmethod
    async def change_task_main(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order_id = data.get("order_id")
            order_tuple = await customers_get.customer_view_order(order_id)
            order, data["order_type"] = order_tuple[0], order_tuple[1]
        if "Название" in message.text:
            async with state.proxy() as data:
                data["change"] = "title"
                data["len"] = 100
            await bot.send_message(message.from_user.id,
                                   f'Название вашего заказа - "{order.title}"',
                                   reply_markup=markup_customer.markup_clean)
            await bot.send_message(message.from_user.id,
                                   f"Введите чтобы поменять Название",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerChangeOrder.change.set()
        if "Описание" in message.text:
            async with state.proxy() as data:
                data["change"] = "description"
                data["len"] = 255
            await bot.send_message(message.from_user.id,
                                   f'Описание вашего заказа - "{order.description}"',
                                   reply_markup=markup_customer.markup_clean)
            await bot.send_message(message.from_user.id,
                                   f"Введите чтобы поменять Описание",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerChangeOrder.change.set()
        if "Откуда забрать" in message.text:
            await bot.send_message(message.from_user.id,
                                   f'Откуда сейчас забирают "Точка А" - "{order.geo_position_from}"')
            await bot.send_message(message.from_user.id,
                                   f'Выберите способ смены Точки А',
                                   reply_markup=markup_customer.choose())
            await customer_states.CustomerChangeOrder.change_geo.set()
            async with state.proxy() as data:
                data["geo_method"] = "A"
        if "Куда доставить" in message.text:
            await bot.send_message(message.from_user.id,
                                   f'Куда сейчас доставляют "Точка B" - "{order.geo_position_to}"')
            await bot.send_message(message.from_user.id,
                                   f'Выберите способ смены Точки B',
                                   reply_markup=markup_customer.choose())
            await customer_states.CustomerChangeOrder.change_geo.set()
            async with state.proxy() as data:
                data["geo_method"] = "B"
        if "Цену" in message.text:
            await bot.send_message(message.from_user.id,
                                   f'Цена заказа сейчас - "{order.price}"',
                                   reply_markup=markup_customer.markup_clean)
            await bot.send_message(message.from_user.id,
                                   f"Введите чтобы поменять Цену заказа",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerChangeOrder.change_money.set()
        if "Цена за 1 час" in message.text:
            await bot.send_message(message.from_user.id,
                                   f'Цена заказа сейчас за 1 час - "{order.price}"',
                                   reply_markup=markup_customer.markup_clean)
            await bot.send_message(message.from_user.id,
                                   f"Введите чтобы поменять Цену заказа за 1 час",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerChangeOrder.change_money.set()
        if "Разблокировать заказ / Назад" in message.text:
            async with state.proxy() as data:
                if data.get("order_type") == "order":
                    await customers_set.customer_set_block_order(data.get("order_id"), 0)
                    await customer_states.CustomerDetailsTasks.not_at_work.set()
                    await bot.send_message(message.from_user.id,
                                           "<b>Ваш заказ снова доступен!</b>",
                                           reply_markup=markup_customer.details_task_not_at_work())
                else:
                    await customers_set.customer_set_block_order(data.get("order_id"), 0)
                    await customer_states.CustomerDetailsTasks.loading.set()
                    await bot.send_message(message.from_user.id,
                                           "<b>Ваш заказ снова доступен!</b>",
                                           reply_markup=markup_customer.details_task_loading())
        if "Количество грузчиков" in message.text:
            await bot.send_message(message.from_user.id,
                                   f'Количество грузчиков сейчас <b>{order.person}</b>',
                                   reply_markup=markup_customer.markup_clean)
            await bot.send_message(message.from_user.id,
                                   f"Введите чтобы поменять количество грузчиков",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerChangeOrder.change_person.set()
        if "Место работы" in message.text:
            await bot.send_message(message.from_user.id,
                                   f'Сейчас выезжают Грузчики на адрес - <b>{order.geo_position}</b>')
            await bot.send_message(message.from_user.id,
                                   f'Выберите способ смены Место работы',
                                   reply_markup=markup_customer.choose())
            await customer_states.CustomerChangeOrder.change_geo.set()
            async with state.proxy() as data:
                data["geo_method"] = "Loading"

    @staticmethod
    async def change(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order_id = data.get("order_id")
            change_ = data.get("change")
            len_ = data.get("len")
            order_type = data.get("order_type")
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            if order_type == "order":
                await bot.send_message(message.from_user.id,
                                       "Что будем менять ?",
                                       reply_markup=markup_customer.details_task_change())
                await customer_states.CustomerChangeOrder.enter.set()
            if order_type == "order_loading":
                await bot.send_message(message.from_user.id,
                                       "Что будем менять ?",
                                       reply_markup=markup_customer.details_task_change_loading())
                await customer_states.CustomerChangeOrder.enter.set()
        if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customers_set.customer_change_order(order_id, change_, message.text)
            if len(message.text) < len_ and message.text != "Назад":
                if order_type == "order":
                    await bot.send_message(message.from_user.id,
                                           f"Отлично! Мы поменяли {change_} заказа!",
                                           reply_markup=markup_customer.details_task_change())
                    await customer_states.CustomerChangeOrder.enter.set()
                if order_type == "order_loading":
                    await bot.send_message(message.from_user.id,
                                           f"Отлично! Мы поменяли {change_} заказа!",
                                           reply_markup=markup_customer.details_task_change_loading())
                    await customer_states.CustomerChangeOrder.enter.set()
            if len(message.text) > len_:
                await bot.send_message(message.from_user.id, "Слишком длинное предложение\n"
                                                             "Ограничение на название заказа - 100 символов\n"
                                                             "Ограничение на описание заказа - 255 символов")

    @staticmethod
    async def change_money(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order_id = data.get("order_id")
            order_type = data.get("order_type")
        if message.text.isdigit():
            await customers_set.customer_change_order(order_id, "price", message.text)
            if order_type == "order":
                await bot.send_message(message.from_user.id,
                                       "Отлично! Мы поменяли цену заказа!",
                                       reply_markup=markup_customer.details_task_change())
                await customer_states.CustomerChangeOrder.enter.set()
            if order_type == "order_loading":
                await bot.send_message(message.from_user.id,
                                       "Отлично! Мы поменяли цену заказа!",
                                       reply_markup=markup_customer.details_task_change_loading())
                await customer_states.CustomerChangeOrder.enter.set()
        if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад" and not message.text.isdigit():
            await bot.send_message(message.from_user.id,
                                   "Надо ввести цифру!")
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            if order_type == "order":
                await customer_states.CustomerChangeOrder.enter.set()
                await bot.send_message(message.from_user.id,
                                       "Что будем менять ?",
                                       reply_markup=markup_customer.details_task_change())
            if order_type == "order_loading":
                await customer_states.CustomerChangeOrder.enter.set()
                await bot.send_message(message.from_user.id,
                                       "Что будем менять ?",
                                       reply_markup=markup_customer.details_task_change_loading())

    @staticmethod
    async def change_person(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order_id = data.get("order_id")
        if message.text.isdigit():
            await customers_set.customer_change_order(order_id, "person", message.text)
            await bot.send_message(message.from_user.id,
                                   "Отлично! Мы поменяли количество грузчиков!",
                                   reply_markup=markup_customer.details_task_change_loading())
            await customer_states.CustomerChangeOrder.enter.set()
        if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад" and not message.text.isdigit():
            await bot.send_message(message.from_user.id,
                                   "Надо ввести цифру!")
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerChangeOrder.enter.set()
            await bot.send_message(message.from_user.id,
                                   "Что будем менять ?",
                                   reply_markup=markup_customer.details_task_change_loading())

    @staticmethod
    async def change_geo(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if data.get("geo_method") == "A":
                if "Ввести координаты с карт" in message.text:
                    await bot.send_message(message.from_user.id,
                                           "<b>Введите Точку А</b>\n"
                                           "Введите координаты",
                                           reply_markup=markup_customer.open_site())
                    await customer_states.CustomerChangeOrder.change_geo_site.set()
                if "Ввести адрес вручную" in message.text:
                    await bot.send_message(message.from_user.id,
                                           "Введите адрес в таком формате:\n"
                                           "Город улица дом\n"
                                           "Пример:\n"
                                           "<b>Москва Лобачевского 12</b>",
                                           reply_markup=markup_customer.back())
                    await customer_states.CustomerChangeOrder.change_geo_custom.set()
                if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                    await bot.send_message(message.from_user.id,
                                           "Что будем менять ?",
                                           reply_markup=markup_customer.details_task_change())
                    await customer_states.CustomerChangeOrder.enter.set()
            elif data.get("geo_method") == "B":
                if "Ввести координаты с карт" in message.text:
                    await bot.send_message(message.from_user.id,
                                           "<b>Введите Точку B</b>\n"
                                           "Введите координаты",
                                           reply_markup=markup_customer.open_site())
                    await customer_states.CustomerChangeOrder.change_geo_site.set()
                if "Ввести адрес вручную" in message.text:
                    await bot.send_message(message.from_user.id,
                                           "Введите адрес в таком формате:\n"
                                           "Город улица дом\n"
                                           "Пример:\n"
                                           "<b>Москва Лобачевского 12</b>",
                                           reply_markup=markup_customer.back())
                    await customer_states.CustomerChangeOrder.change_geo_custom.set()
                if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                    await bot.send_message(message.from_user.id,
                                           "Что будем менять ?",
                                           reply_markup=markup_customer.details_task_change())
                    await customer_states.CustomerChangeOrder.enter.set()
            elif data.get("geo_method") == "Loading":
                if "Ввести координаты с карт" in message.text:
                    await bot.send_message(message.from_user.id,
                                           "<b>Куда выезжать ?</b>\n"
                                           "Введите координаты",
                                           reply_markup=markup_customer.open_site())
                    await customer_states.CustomerChangeOrder.change_geo_site.set()
                if "Ввести адрес вручную" in message.text:
                    await bot.send_message(message.from_user.id,
                                           "Введите адрес в таком формате:\n"
                                           "Город улица дом\n"
                                           "Пример:\n"
                                           "<b>Москва Лобачевского 12</b>",
                                           reply_markup=markup_customer.back())
                    await customer_states.CustomerChangeOrder.change_geo_custom.set()
                if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                    await bot.send_message(message.from_user.id,
                                           "Что будем менять ?",
                                           reply_markup=markup_customer.details_task_change_loading())
                    await customer_states.CustomerChangeOrder.enter.set()

    @staticmethod
    async def change_geo_site(message: types.Message, state: FSMContext):
        if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            try:
                n = Nominatim(user_agent='User')
                loc = f"{message.text}"
                address = n.reverse(loc)
                city = address.raw.get("address").get("city")
                if city is None:
                    city = address.raw.get("address").get("town")
                await bot.send_message(message.from_user.id,
                                       f'Город подачи: {city}\n'
                                       f'Адрес подачи: {address.raw.get("address").get("road")}, '
                                       f'{address.raw.get("address").get("house_number")}\n')
                await bot.send_message(message.from_user.id,
                                       "Проверьте пожалуйста координаты, если вы ошиблись "
                                       "вы можете еще раз отправить геопозицию. "
                                       "Если же все в порядке нажмите Все верно",
                                       reply_markup=markup_customer.inline_approve_geo_position_site())
                async with state.proxy() as data:
                    data["change_geo_position_site"] = f'{city}, ' \
                                                 f'{address.raw.get("address").get("road")}, ' \
                                                 f'{address.raw.get("address").get("house_number")}'
            except (AttributeError, ValueError):
                await bot.send_message(message.from_user.id,
                                       "Вам нужно ввести координаты в таком формате:\n"
                                       "<b>Пример:</b>\n"
                                       "41.06268142529587, 28.99228891099907")
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете выбрать способ ввода",
                                   reply_markup=markup_customer.choose())
            await customer_states.CustomerChangeOrder.change_geo.set()

    @staticmethod
    async def change_geo_site_approve(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            result = data.get("change_geo_position_site")
            order_id = data.get("order_id")
            if data.get("geo_method") == "A":
                geo = "geo_position_from"
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
                await bot.send_message(callback.from_user.id,
                                       "Вы успешно поменяли Точку A",
                                       reply_markup=markup_customer.details_task_change())
            elif data.get("geo_method") == "B":
                geo = "geo_position_to"
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
                await bot.send_message(callback.from_user.id,
                                       "Вы успешно поменяли Точку B",
                                       reply_markup=markup_customer.details_task_change())
            elif data.get("geo_method") == "Loading":
                geo = "geo_position"
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
                await bot.send_message(callback.from_user.id,
                                       "Вы успешно поменяли Место работы",
                                       reply_markup=markup_customer.details_task_change_loading())
        await customers_set.customer_change_order(order_id, geo, result)
        await customer_states.CustomerChangeOrder.enter.set()

    @staticmethod
    async def change_geo_custom(message: types.Message, state: FSMContext):
        if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            msg = message.text.split()
            if len(msg) == 4:
                await bot.send_message(message.from_user.id,
                                       f'Город подачи: {msg[0]}\n'
                                       f'Адрес подачи: {msg[1]} {msg[2]} - '
                                       f'{msg[-1]}')
                await bot.send_message(message.from_user.id,
                                       "Проверьте пожалуйста введенные данные, если вы ошиблись "
                                       "вы можете еще раз отправить адрес.\n"
                                       "Если же все в порядке нажмите Все верно",
                                       reply_markup=markup_customer.inline_approve_geo_position_custom())
                async with state.proxy() as data:
                    data["change_geo_position_custom"] = message.text
            elif len(msg) == 3:
                await bot.send_message(message.from_user.id,
                                       f'Город подачи: {msg[0]}\n'
                                       f'Адрес подачи: {msg[1]} - '
                                       f'{msg[-1]}')
                await bot.send_message(message.from_user.id,
                                       "Проверьте пожалуйста введенные данные, если вы ошиблись "
                                       "вы можете еще раз отправить адрес.\n"
                                       "Если же все в порядке нажмите Все верно",
                                       reply_markup=markup_customer.inline_approve_geo_position_custom())
                async with state.proxy() as data:
                    data["change_geo_position_custom"] = message.text
            else:
                await bot.send_message(message.from_user.id,
                                       "Надо ввести данные в формате\n"
                                       "<b>Город Улица Дом</b>")
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerChangeOrder.change_geo.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад\n"
                                   "Здесь вы сможете выбрать способ ввода адреса\n"
                                   "С помощью <b>Карт</b> или <b>Ручной метод</b>",
                                   reply_markup=markup_customer.choose())

    @staticmethod
    async def change_geo_custom_approve(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            result = data.get("change_geo_position_custom")
            order_id = data.get("order_id")
            if data.get("geo_method") == "A":
                geo = "geo_position_from"
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
                await bot.send_message(callback.from_user.id,
                                       "Вы успешно поменяли Точку A",
                                       reply_markup=markup_customer.details_task_change())
            elif data.get("geo_method") == "B":
                geo = "geo_position_to"
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
                await bot.send_message(callback.from_user.id,
                                       "Вы успешно поменяли Точку B",
                                       reply_markup=markup_customer.details_task_change())
            elif data.get("geo_method") == "Loading":
                geo = "geo_position"
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
                await bot.send_message(callback.from_user.id,
                                       "Вы успешно поменяли Место работы",
                                       reply_markup=markup_customer.details_task_change_loading())
        await customers_set.customer_change_order(order_id, geo, result)
        await customer_states.CustomerChangeOrder.enter.set()

    @staticmethod
    async def approve_people_loading(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Вы нашли всех грузчиков\n"
                               "Заказ исчез из поиска",
                               reply_markup=markup_customer.details_task_loading_at_work())
        async with state.proxy() as data:
            await customers_set.customer_find_all_persons(data.get("order_id"))

    @staticmethod
    async def decline_people_loading(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)

    @staticmethod
    async def loading_invite_people(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)

        order_id = callback.message.text.split()[4]
        user = await performers_get.performer_select(int(callback.data[15:]))

        order_loading = await customers_get.customer_view_order(order_id)
        order_loading = order_loading[0]

        if int(order_loading.person) - int(order_loading.count_person) == 0:
            await bot.send_message(callback.from_user.id,
                                   "<b>Для этого заказа все Грузчики уже найдены!</b>")
            await bot.send_message(user.user_id,
                                   f"По этому заказу <b>{order_id}</b> уже набраны все Грузчики!")
        if order_loading.block == 1:
            await bot.send_message(callback.from_user.id,
                                   "<b>Вы заблокировали заказ!</b>")
            await bot.send_message(user.user_id,
                                   f"По этому заказу <b>{order_id}</b> уже набраны все Грузчики!")
        if user.user_id in order_loading.persons_list:
            await bot.send_message(callback.from_user.id,
                                   "<b>Вы уже пригласили этого Грузчика!</b>")
        else:
            await customers_set.customer_loading_set_count_person(order_id, user.user_id)
            order_loading = await customers_get.customer_view_order(order_id)
            order_loading = order_loading[0]
            if int(order_loading.person) - int(order_loading.count_person) == 0:
                await bot.send_message(callback.from_user.id,
                                       "<b>Все Грузчики найдены!</b>")
            else:
                await bot.send_message(callback.from_user.id,
                                       f"Теперь у вас - <b>{order_loading.count_person}</b> Грузчик/Грузчика\n"
                                       f"Вам осталось найти - "
                                       f"<b>{int(order_loading.person) - int(order_loading.count_person)}</b> "
                                       f"Грузчик/Грузчика")
            tel = await customers_get.customer_select(callback.from_user.id)
            await bot.send_message(callback.from_user.id,
                                   f"Данные вашего Грузчика\n"
                                   f"Username - <b>@{user.username}</b>\n"
                                   f"Телефон - <b>{user.telephone}</b>\n"
                                   f"Имя - <b>{user.first_name}</b>")
            await bot.send_message(user.user_id,
                                   "Вас взяли на заказ Грузчиком\n"
                                   f"Ваш Заказчик - <b>{callback.from_user.first_name}</b>\n"
                                   f"Написать - <b>@{callback.from_user.username}</b>\n"
                                   f"Позвонить - <b>{tel.telephone}</b>")


class CustomerDetailsTasksStatus:
    @staticmethod
    async def details_status(message: types.Message, state: FSMContext):
        # if "Отменить заказ" in message.text:
        #     async with state.proxy() as data:
        #         status = await general_get.check_details_status(data.get("order_id"))
        #     if status is None:
        #         await bot.send_message(message.from_user.id,
        #                                "Заказ закрыт",
        #                                reply_markup=markup_customer.main_menu())
        #         await customer_states.CustomerStart.customer_menu.set()
        #     if status:
        #         if status.customer_status:
        #             await bot.send_message(message.from_user.id,
        #                                    "Вы уже не сможете отменить заказ так как вы его завершили",
        #                                    reply_markup=markup_customer.details_task_status())
        #             await customer_states.CustomerDetailsTasksStatus.enter_status.set()
        #         else:
        #             await bot.send_message(message.from_user.id,
        #                                    "Вы хотите отменить заказ ?",
        #                                    reply_markup=markup_customer.inline_cancel_task())
        if "Завершить заказ" in message.text:
            async with state.proxy() as data:
                status = await general_get.check_details_status(data.get("order_id"))
            if status is None:
                await bot.send_message(message.from_user.id,
                                       "Заказ закрыт")
                not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                       reply_markup=markup_customer.main_menu())
                await customer_states.CustomerStart.customer_menu.set()
            if status:
                if status.customer_status:
                    await bot.send_message(message.from_user.id,
                                           "Вы уже завершали заказ",
                                           reply_markup=markup_customer.details_task_status())
                    await customer_states.CustomerDetailsTasksStatus.enter_status.set()
                else:
                    await bot.send_message(message.from_user.id,
                                           "Вас все устраивает ?",
                                           reply_markup=markup_customer.markup_clean)
                    await bot.send_message(message.from_user.id,
                                           "Хотите завершить заказ ?",
                                           reply_markup=markup_customer.inline_close_task())
        if "Проверить статус заказа" in message.text:
            await bot.send_message(message.from_user.id, "Проверяем статус заказа...")
            async with state.proxy() as data:
                status = await general_get.check_details_status(data.get("order_id"))
            if status is not None:
                if status.customer_status == 1:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}"
                                           f"С вашей стороны заказ помечен как ВЫПОЛНЕННЫЙ!"
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}")

                if status.customer_status == 0:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('CROSS_MARK')}"
                                           f"С вашей стороны заказ помечен как НЕ ВЫПОЛНЕННЫЙ"
                                           f"{config.KEYBOARD.get('CROSS_MARK')}")
                if status.performer_status == 1:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}"
                                           f"Со стороны Исполнителя помечен как ВЫПОЛНЕННЫЙ"
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}")
                if status.performer_status == 0:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('CROSS_MARK')}"
                                           f"Со стороны Исполнителя помечен как НЕ ВЫПОЛНЕННЫЙ"
                                           f"{config.KEYBOARD.get('CROSS_MARK')}")
            else:
                await bot.send_message(message.from_user.id,
                                       "Заказ закрыт")
                not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
                at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
                loading = await customers_get.customer_all_orders_loading(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                       reply_markup=markup_customer.main_menu())
                await customer_states.CustomerStart.customer_menu.set()
        if "Вернуться в детали заказа" in message.text:
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в детали заказа",
                                   reply_markup=markup_customer.details_task())
            await customer_states.CustomerDetailsTasks.enter_task.set()

    @staticmethod
    async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            await customers_set.customer_cancel_order(data.get("order_id"),
                                                      callback.from_user.id)
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CROSS_MARK') * 14}")
            await bot.send_message(data.get("user_id"),
                                   f"Ваша задача <b>{data.get('order_id')}</b> была отменена заказчиком!")
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CROSS_MARK') * 14}")
        await customer_states.CustomerStart.customer_menu.set()
        await bot.send_message(callback.from_user.id,
                               "Вы отменили заказ!")
        not_at_work = await customers_get.customer_all_orders_not_at_work(callback.from_user.id)
        at_work = await customers_get.customer_all_orders_in_work(callback.from_user.id)
        loading = await customers_get.customer_all_orders_loading(callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                               reply_markup=markup_customer.main_menu())

    @staticmethod
    async def no_cancel_order(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Хорошо что передумали, заказ будет сделан!",
                               reply_markup=markup_customer.details_task_status())

    @staticmethod
    async def close_order(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 14}")
            await bot.send_message(data.get("user_id"),
                                   f"Ваша задача <b>{data.get('order_id')}</b> "
                                   f"была помечена Заказчиком как выполненная!\n"
                                   f"Посмотрите в разделе 'Проверить статус заказа'\n"
                                   f"Если Заказчик и Исполнитель завершили заказ, "
                                   f"то заказ будет перемещен в раздел Завершенных заказов")
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 14}")
            await customers_set.customer_set_order_status(data.get("order_id"))
        await bot.send_message(callback.from_user.id,
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 14}")
        await bot.send_message(callback.from_user.id,
                               "Отлично! Вы установили статус заказа завершенным")
        await bot.send_message(callback.from_user.id,
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 14}")
        await bot.send_message(callback.from_user.id,
                               "Оцените исполнителя",
                               reply_markup=markup_customer.rating())
        await customer_states.CustomerDetailsTasksStatus.rating.set()

    @staticmethod
    async def no_close(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Пусть сделают до конца, а потом завершайте",
                               reply_markup=markup_customer.details_task_status())

    @staticmethod
    async def rating(message: types.Message, state: FSMContext):
        rate = ['1', '2', '3', '4', '5', 'Пропустить']
        if message.text in rate:
            if message.text == "Пропустить":
                await bot.send_message(message.from_user.id,
                                       f"Вы не поставили оценку Исполнителю\n"
                                       f"Вы можете оставить отзыв, или войти в детали заказа",
                                       reply_markup=markup_customer.details_task_status_review())
                await customer_states.CustomerDetailsTasksStatus.review.set()
            else:
                async with state.proxy() as data:
                    await customers_set.customer_set_rating_to_performer(data.get("user_id"), message.text)
                    await customers_set.customer_set_rating_to_performer_in_review_db(data.get("order_id"),
                                                                                      message.text)
                await bot.send_message(message.from_user.id,
                                       f"Вы поставили оценку Исполнителю - <b>{message.text}</b>\n"
                                       f"Спасибо за оценку!\n"
                                       f"Вы можете оставить отзыв, или войти в детали заказа",
                                       reply_markup=markup_customer.details_task_status_review())
                await customer_states.CustomerDetailsTasksStatus.review.set()
        else:
            await bot.send_message(message.from_user.id, "Надо поставить оценку 1,2,3,4,5")

    @staticmethod
    async def review(message: types.Message, state: FSMContext):
        if "Войти в детали заказа" in message.text:
            await bot.send_message(message.from_user.id,
                                   "Вы вошли в детали заказа",
                                   reply_markup=markup_customer.details_task_status())
            await customer_states.CustomerDetailsTasksStatus.enter_status.set()
        else:
            async with state.proxy() as data:
                await customers_set.customer_set_review_to_performer_in_review_db(data.get("order_id"),
                                                                                  message.text)
                await bot.send_message(message.from_user.id,
                                       "Отзыв отправлен!",
                                       reply_markup=markup_customer.details_task_status())
                await customer_states.CustomerDetailsTasksStatus.enter_status.set()
