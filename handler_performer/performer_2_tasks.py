from collections import Counter
from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim
from geopy import distance

from bot import bot
from data.commands import performers_get, performers_set, customers_get, general_get, general_set
from markups import markup_performer, markup_customer
from settings import config
from states import performer_states


class PerformerTasks:
    @staticmethod
    async def check_all_orders(message: types.Message, state: FSMContext):
        if "Ввести ID задачи" in message.text:
            await performer_states.PerformerTasks.get_order.set()
            await bot.send_message(message.from_user.id,
                                   "Введите ID задачи!",
                                   reply_markup=markup_performer.markup_clean)
        if "Вернуться в главное меню" in message.text:
            await performer_states.PerformerStart.performer_menu.set()
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu(jobs))
        if "Грузчики" in message.text:
            geolocator = Nominatim(user_agent=f"FlowWork_{message.from_user.id}")
            performer = await performers_get.performer_select(message.from_user.id)
            res = await performers_get.performer_checks_all_orders_loading(message.from_user.id)
            if res:
                for i in res:
                    if i.image:
                        await bot.send_photo(message.from_user.id, i.image)
                    if i.video:
                        await bot.send_video(message.from_user.id, i.video)
                    try:
                        loc_a = geolocator.geocode(i.geo_position)
                        loc_a = loc_a.latitude, loc_a.longitude
                        location_result = f"{round(distance.distance(loc_a, performer.geo_position).km, 2)} км"
                    except AttributeError:
                        location_result = f"Не получилось определить {config.KEYBOARD.get('FROWNING_FACE')}"
                    await bot.send_message(message.from_user.id,
                                           f"<b>Детали заказа от Заказчика {i.user_id}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Место работы - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(i.geo_position.split())}'>{i.geo_position}</a>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Нужно грузчиков - <b>{i.person}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Уже грузчиков - <b>{i.count_person}</b>\n"
                                           f"{config.KEYBOARD.get('STOPWATCH')} "
                                           f"Начало работы - <b>{i.start_time}</b>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{i.description}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена - <b>{i.price}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <code>{i.order_id}</code>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{i.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('WORLD_MAP')} "
                                           f"<b>Место работы</b> находится в радиусе: "
                                           f"<b>{location_result}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n",
                                           reply_markup=markup_performer.inline_approve_loading(i.order_id),
                                           disable_web_page_preview=True)
            else:
                await bot.send_message(message.from_user.id,
                                       "В данный момент заказов для Грузчиков нет!")
        if "Доставка" in message.text:
            performer = await performers_get.performer_select(message.from_user.id)
            async with state.proxy() as data:
                data["performer_category"] = performer.performer_category
            p_c = None
            if performer.performer_category == "car":
                p_c = "Исполнителя на Машине"
            if performer.performer_category == "scooter":
                p_c = "Исполнителя на Самокате"
            elif performer.performer_category == "pedestrian":
                p_c = "Пешехода"
            res = await performers_get.performer_checks_all_orders(message.from_user.id, performer.performer_category)
            await bot.send_message(message.from_user.id,
                                   f"Выводим весь список задач для <b>{p_c}</b>")
            if res:
                finished_categories = InlineKeyboardMarkup()
                categories = []
                for i in res:
                    categories.append(i.category_delivery)
                result_categories = Counter(categories)
                for k, v in result_categories.items():
                    finished_categories.insert(InlineKeyboardButton(text=f"({v}) {k}",
                                                                    callback_data=f"cat_{k}"))
                await bot.send_message(message.from_user.id,
                                       "<b>Выберите категорию</b>\n"
                                       "<b>В скобках указано кол-во заказов в данной категории</b>",
                                       reply_markup=finished_categories)
            else:
                await bot.send_message(message.from_user.id,
                                       "В данный момент заказов для вашей категории нет!")
        if "Назад" in message.text:
            await performer_states.PerformerStart.performer_menu.set()
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu(jobs))

    @staticmethod
    async def choose_category(callback: types.CallbackQuery, state: FSMContext):
        geolocator = Nominatim(user_agent=f"FlowWork_{callback.from_user.id}")
        performer = await performers_get.performer_select(callback.from_user.id)
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            res_category = callback.data[4:]
            res = await performers_get.performer_checks_all_orders_with_category(callback.from_user.id,
                                                                                 data.get("performer_category"),
                                                                                 res_category)
        for i in res:
            order_rating = await performers_get.performer_check_order_rating(i.order_id, callback.from_user.id)
            p_status = None
            icon = None
            if i.performer_category == "pedestrian":
                p_status = "Пешеход"
                icon = f"{config.KEYBOARD.get('PERSON_RUNNING')}"
            if i.performer_category == "scooter":
                p_status = "На самокате"
                icon = f"{config.KEYBOARD.get('KICK_SCOOTER')}"
            if i.performer_category == "car":
                p_status = "На машине"
                icon = f"{config.KEYBOARD.get('AUTOMOBILE')}"
            elif i.performer_category == "any":
                p_status = "Любой"
                icon = f"{config.KEYBOARD.get('AUTOMOBILE')}" \
                       f"{config.KEYBOARD.get('KICK_SCOOTER')}" \
                       f"{config.KEYBOARD.get('PERSON_RUNNING')}"
            if i.image:
                await bot.send_photo(callback.from_user.id, i.image)
            if i.video:
                await bot.send_video(callback.from_user.id, i.video)
            try:
                loc_a = geolocator.geocode(i.geo_position_from)
                loc_a = loc_a.latitude, loc_a.longitude
                location_result = f"{round(distance.distance(loc_a, performer.geo_position).km, 2)} км"
            except AttributeError:
                location_result = f"Не получилось определить {config.KEYBOARD.get('FROWNING_FACE')}"
            await bot.send_message(callback.from_user.id,
                                   f"<b>Детали заказа</b>\n"
                                   f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                   f"Категория - <b>{i.category_delivery}</b>\n"
                                   f"{config.KEYBOARD.get('A_BUTTON')} "
                                   f"Откуда - <a href='https://yandex.ru/maps/?text="
                                   f"{'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                   f"{config.KEYBOARD.get('B_BUTTON')} "
                                   f"Куда - <a href='https://yandex.ru/maps/?text="
                                   f"{'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} "
                                   f"Описание - <b>{i.description}</b>\n"
                                   f"{config.KEYBOARD.get('DOLLAR')} "
                                   f"Цена - <b>{i.price}</b>\n"
                                   f"{config.KEYBOARD.get('MONEY_BAG')} "
                                   f"Ценность этого товара - <b>{i.order_worth}</b>\n"
                                   f"{icon} "
                                   f"Исполнитель - <b>{p_status}</b>\n"
                                   f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                   f"Заказ создан: <b>{i.order_create}</b>\n"
                                   f"{config.KEYBOARD.get('BAR_CHART')} "
                                   f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                   f"{config.KEYBOARD.get('WORLD_MAP')} "
                                   f"Точка <b>А</b> находится в радиусе: "
                                   f"<b>{location_result}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}\n",
                                   disable_web_page_preview=True,
                                   reply_markup=markup_performer.inline_order_request(i.order_id))
            if order_rating is None:
                await bot.send_message(callback.from_user.id,
                                       "Поставьте <b>Лайк</b> или <b>Дизлайк</b> этому заказу",
                                       reply_markup=markup_performer.order_rating(i.order_id))
            else:
                if order_rating == 1:
                    like = "Лайк"
                else:
                    like = "Дизлайк"
                await bot.send_message(callback.from_user.id,
                                       f"Вы поставили <b>{like}</b> этому заказу")

    @staticmethod
    async def order_request(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        performer = await performers_get.performer_select(callback.from_user.id)
        if performer.performer_money < 0:
            await bot.send_message(callback.from_user.id,
                                   "У вас отрицательный баланс!")
        else:
            order_id = callback.data[14:]
            geolocator = Nominatim(user_agent=f"FlowWork_{callback.from_user.id}")
            order = await general_get.order_select(order_id)
            customer_id = await performers_get.performer_checks_customer_user_id(order_id)
            try:
                loc_a = geolocator.geocode(order.geo_position_from)
                loc_a = loc_a.latitude, loc_a.longitude
                location_result = f"{round(distance.distance(loc_a, performer.geo_position).km, 2)} км"
            except AttributeError:
                location_result = f"Не получилось определить {config.KEYBOARD.get('FROWNING_FACE')}"

            """Здесь надо придумать как оповестить по СМС заказчику о том что его заказ хотят взять"""
            await bot.send_message(customer_id, f"Ваш заказ <b>{order_id}</b> хочет взять Исполнитель!\n"
                                                f"Его рейтинг - <b>{performer.performer_rating}</b>\n"
                                                f"Имя - <b>{callback.from_user.first_name}</b>\n"
                                                f"Фамилия - <b>{callback.from_user.last_name}</b>\n"
                                                f"Заказов взял - <b>{performer.get_orders}</b>\n"
                                                f"Заказов выполнил - <b>{performer.completed_orders}</b>\n"
                                                f"Исполнитель находится от точки <b>А</b> в радиусе "
                                                f"<b>{location_result}</b>",
                                   reply_markup=markup_performer.inline_approve_main(order_id,
                                                                                     callback.from_user.id))
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(callback.from_user.id,
                                   f"Отклик отправлен! Ожидайте ответа Заказчика")
            orders = await performers_get.performer_view_list_orders(callback.from_user.id)
            orders_loading = await performers_get.performer_loader_order(callback.from_user.id)
            promo = await performers_get.check_commission_promo(callback.from_user.id)
            jobs = await performers_get.performer_check_jobs_offers(callback.from_user.id)
            await bot.send_message(callback.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu(jobs))

    @staticmethod
    async def proposal(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        performer = await performers_get.performer_select(callback.from_user.id)
        if performer.performer_money < 0:
            await bot.send_message(callback.from_user.id,
                                   "У вас отрицательный баланс!")
        else:
            res = await customers_get.customer_view_order(callback.data[15:])
            await bot.send_message(callback.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"<b>Детали заказа</b>\n"
                                   f"{config.KEYBOARD.get('A_BUTTON')} "
                                   f"Откуда - <a href='https://yandex.ru/maps/?text="
                                   f"{'+'.join(res[0].geo_position_from.split())}'>{res[0].geo_position_from}</a>\n"
                                   f"{config.KEYBOARD.get('B_BUTTON')} "
                                   f"Куда - <a href='https://yandex.ru/maps/?text="
                                   f"{'+'.join(res[0].geo_position_to.split())}'>{res[0].geo_position_to}</a>\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} "
                                   f"Описание - <b>{res[0].description}</b>\n"
                                   f"{config.KEYBOARD.get('DOLLAR')} "
                                   f"Цена - <b>{res[0].price}</b>\n"
                                   f"{config.KEYBOARD.get('MONEY_BAG')} "
                                   f"Ценность этого товара - <b>{res[0].order_worth}</b>\n"
                                   f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                   f"Заказ создан: <b>{res[0].order_create}</b>\n"
                                   f"{config.KEYBOARD.get('BAR_CHART')} "
                                   f"Рейтинг заказа | <b>{res[0].order_rating}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}\n",
                                   disable_web_page_preview=True)
            async with state.proxy() as data:
                data["order_id"] = callback.data[15:]
                data["price"] = res[0].price
            await bot.send_message(callback.from_user.id,
                                   "Введите новую цену")
            await performer_states.PerformerTasks.proposal.set()

    @staticmethod
    async def proposal_price(message: types.Message, state: FSMContext):
        if message.text.isdigit():
            async with state.proxy() as data:
                customer_id = await performers_get.performer_checks_customer_user_id(data['order_id'])
                data["new_price"] = message.text
            await bot.send_message(message.from_user.id, f"Вы предложили новую цену! - {message.text}\n"
                                                         f"Подождите пока заказчик вам ответит")
            await bot.send_message(customer_id,
                                   f"{config.KEYBOARD.get('DOLLAR') * 10}\n"
                                   f"Предложение новой цены <b>{message.text}</b> "
                                   f"от Исполнителя <b>{message.from_user.id}</b> "
                                   f"на ваш заказ <b>{data.get('order_id')}</b>\n"
                                   f"Ваша цена заказа - <b>{data.get('price')}</b>\n"
                                   f"{config.KEYBOARD.get('DOLLAR') * 10}\n",
                                   reply_markup=markup_performer.inline_approve_proposal())
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(message.from_user.id,
                                   f"Отклик отправлен! Ожидайте ответа Заказчика")
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu(jobs))
        else:
            await bot.send_message(message.from_user.id, "Надо ввести целое число!")

    @staticmethod
    async def order_rating_plus(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await general_set.order_rating_change_plus(callback.data[5:])
        await performers_set.performer_set_order_rating(callback.data[5:], 1, callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               f"Вы поставили лайк заказу <b>{callback.data[5:]}</b>")

    @staticmethod
    async def order_rating_minus(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await general_set.order_rating_change_minus(callback.data[6:])
        await performers_set.performer_set_order_rating(callback.data[6:], -1, callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               f"Вы поставили дизлайк заказу <b>{callback.data[6:]}</b>")

    @staticmethod
    async def order_loading_into_yes(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await performers_set.performer_set_order_loading(callback.from_user.id,
                                                         callback.data[13:],
                                                         datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
        await performer_states.PerformerStart.performer_menu.set()
        await bot.send_message(callback.from_user.id,
                               "Вы вписались!")
        orders = await performers_get.performer_view_list_orders(callback.from_user.id)
        orders_loading = await performers_get.performer_loader_order(callback.from_user.id)
        promo = await performers_get.check_commission_promo(callback.from_user.id)
        jobs = await performers_get.performer_check_jobs_offers(callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                               reply_markup=markup_performer.main_menu(jobs))

    @staticmethod
    async def loading_request(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        order_loading = await performers_get.performer_check_order_loading(callback.data[16:])
        performer = await performers_get.performer_select(callback.from_user.id)
        async with state.proxy() as data:
            data["order_loading"] = order_loading
        if performer.performer_money < 0:
            await bot.send_message(callback.from_user.id,
                                   "У вас отрицательный баланс!")
        else:
            if order_loading.persons_list:
                if callback.from_user.id in order_loading.persons_list:
                    await bot.send_message(callback.from_user.id,
                                           "Вы уже подавали Запрос на этот заказ")
                else:
                    await performer_states.PerformerTasks.loading_request.set()
                    await bot.send_message(callback.from_user.id,
                                           "<b>Напишите комментарий Заказчику</b>\n"
                                           "<b>Например через сколько вы будете на месте</b>",
                                           reply_markup=markup_performer.back())
            else:
                await performer_states.PerformerTasks.loading_request.set()
                await bot.send_message(callback.from_user.id,
                                       "<b>Напишите комментарий Заказчику</b>\n"
                                       "<b>Например через сколько вы будете на месте</b>",
                                       reply_markup=markup_performer.back())

    @staticmethod
    async def loading_request_approve(message: types.Message, state: FSMContext):
        if message.text == f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await performer_states.PerformerTasks.check_all_orders.set()
            await bot.send_message(message.from_user.id,
                                   "Выберите тип Заказа",
                                   reply_markup=markup_performer.approve())
        if message.text != f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            async with state.proxy() as data:
                order_loading = data.get("order_loading")
                performer = await performers_get.performer_select(message.from_user.id)
                await bot.send_message(order_loading.user_id,
                                       f"Запрос на ваш заказ <b>{order_loading.order_id}</b>\n"
                                       f"Тип заказа - <b>Погрузка/Разгрузка</b>\n"
                                       f"Имя - <b>{performer.first_name}\n</b>"
                                       f"Рейтинг - <b>{performer.performer_rating}\n</b>"
                                       f"Взял заказов - <b>{performer.get_orders}\n</b>"
                                       f"Отменил заказов - <b>{performer.canceled_orders}\n</b>"
                                       f"Комментарий Грузчика: \n"
                                       f"<b>{message.text}</b>",
                                       reply_markup=markup_customer.inline_approve_loading_proposal(
                                           message.from_user.id))
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Запрос отправлен!\n"
                                   "Вы находитесь в Главном меню")
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu(jobs))

    @staticmethod
    async def loading_request_decline(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)


class PerformerDetailsTasks:
    @staticmethod
    async def performer_details(message: types.Message, state: FSMContext):
        if "Назад" in message.text:
            await performer_states.PerformerStart.orders.set()
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   "Выберите тип заказа",
                                   reply_markup=markup_performer.performer_type_orders(orders, orders_loading))
        else:
            try:
                res = await performers_get.performer_view_list_orders(message.from_user.id)
                async with state.proxy() as data:
                    try:
                        msg = message.text.split()[1]
                        data["order_id"] = msg
                        data["user_id"] = await performers_get.performer_checks_customer_user_id(msg)
                    except (AttributeError, IndexError):
                        await bot.send_message(message.from_user.id,
                                               "Откройте клавиатуру и нажмите на ID вашего заказа")
                for i in res:
                    try:
                        if i.order_id == msg:
                            await performer_states.PerformerDetailsTasks.enter_task.set()
                            await bot.send_message(message.from_user.id,
                                                   "Вы вошли в детали заказа\n"
                                                   "Здесь вы сможете отправить Заказчику <b>Видео сообщение</b> "
                                                   "и <b>Аудио сообщение</b>",
                                                   reply_markup=markup_performer.details_task())
                    except UnboundLocalError:
                        pass
            except TypeError:
                pass

    @staticmethod
    async def performer_details_loading(message: types.Message, state: FSMContext):
        if "Назад" in message.text:
            await performer_states.PerformerStart.orders.set()
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   "Выберите тип заказа",
                                   reply_markup=markup_performer.performer_type_orders(orders, orders_loading))
        else:
            try:
                """Когда пользователь нажимает кнопку заказа (order_id) здесь мы сохраняем order_id в памяти
                а потом проверяем взял ли этот заказ Исполнитель"""
                async with state.proxy() as data:
                    order_id = message.text.split()[1]
                    data["order_id"] = order_id
                    data["order"] = await performers_get.performer_check_order_loading(order_id)
                await bot.send_message(message.from_user.id,
                                       "Вы вошли в детали заказа\n"
                                       "Здесь вы сможете отправить Заказчику <b>Видео сообщение</b> "
                                       "и <b>Аудио сообщение</b>",
                                       reply_markup=markup_performer.details_task_loading())
                await performer_states.PerformerDetailsTasks.enter_loading_task.set()
            except IndexError:
                await bot.send_message(message.from_user.id,
                                       "Откройте клавиатуру и нажмите на ID вашего заказа")

    @staticmethod
    async def performer_details_loading_enter(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order_id = data.get("order_id")
            customer = await customers_get.customer_select(data.get("order").user_id)
        if message.video_note:
            await bot.send_video_note(customer.user_id, message.video_note.file_id)
            await bot.send_message(message.from_user.id,
                                   "Вы отправили Видео сообщение Заказчику!")
            await bot.send_message(customer.user_id,
                                   "Исполнитель отправил вам Видео сообщение, чтобы ему ответить "
                                   "Вам нужно зайти в 'Мои Заказы', далее 'В работе', далее "
                                   "выбираете ваш Заказ, после этого можете отправлять ответ")
        if message.voice:
            await bot.send_voice(customer.user_id, message.voice.file_id)
            await bot.send_message(message.from_user.id,
                                   "Вы отправили Аудио сообщение Заказчику!")
            await bot.send_message(customer.user_id,
                                   "Исполнитель отправил вам Аудио сообщение, чтобы ему ответить "
                                   "Вам нужно зайти в 'Мои Заказы', далее 'В работе', далее "
                                   "выбираете ваш Заказ, после этого можете отправлять ответ")
        if message.text:
            if message.text == f"{config.KEYBOARD.get('TELEPHONE')} Позвонить/написать заказчику":
                order = await performers_get.performer_check_order_loading_relevance(message.from_user.id, order_id)
                if order is None:
                    await performer_states.PerformerStart.performer_menu.set()
                    orders = await performers_get.performer_view_list_orders(message.from_user.id)
                    orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                    promo = await performers_get.check_commission_promo(message.from_user.id)
                    jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                           reply_markup=markup_performer.main_menu(jobs))
                else:
                    await bot.send_message(message.from_user.id,
                                           f"Вот его номер телефона {customer.telephone}\n"
                                           f"Или напишите ему в телеграм @{customer.username}")
            if message.text == f"{config.KEYBOARD.get('CLIPBOARD')} Детали заказа":
                order = await performers_get.performer_check_order_loading_relevance(message.from_user.id, order_id)
                if order is None:
                    await performer_states.PerformerStart.performer_menu.set()
                    orders = await performers_get.performer_view_list_orders(message.from_user.id)
                    orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                    promo = await performers_get.check_commission_promo(message.from_user.id)
                    jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                           reply_markup=markup_performer.main_menu(jobs))
                else:
                    if order.image:
                        await bot.send_photo(message.from_user.id, order.image)
                    if order.video:
                        await bot.send_video(message.from_user.id, order.video)
                    loaders = [await performers_get.performer_select(v) for v in order.persons_list]
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа для Грузчиков</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(order.geo_position.split())}'>{order.geo_position}</a>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Сколько Грузчиков - <b>{order.person}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Уже Грузчиков - <b>{order.count_person}</b>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{order.description}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена за 1 час - <b>{order.price}</b>\n"
                                           f"{config.KEYBOARD.get('STOPWATCH')} "
                                           f"Начало работ: <b>{order.start_time}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <code>{order.order_id}</code>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{order.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Грузчики: {' | '.join([k.username for k in loaders])}\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{order.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n",
                                           disable_web_page_preview=True)
            if message.text == f"{config.KEYBOARD.get('BUSTS_IN_SILHOUETTE')} Список Грузчиков":
                order = await performers_get.performer_check_order_loading_relevance(message.from_user.id, order_id)
                if order is None:
                    await performer_states.PerformerStart.performer_menu.set()
                    orders = await performers_get.performer_view_list_orders(message.from_user.id)
                    orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                    promo = await performers_get.check_commission_promo(message.from_user.id)
                    jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                           reply_markup=markup_performer.main_menu(jobs))
                else:
                    loaders = [await performers_get.performer_select(v) for v in order.persons_list]
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
                                               f"{config.KEYBOARD.get('DASH') * 14}")
            if message.text == f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} Профиль заказчика":
                order = await performers_get.performer_check_order_loading_relevance(message.from_user.id, order_id)
                if order is None:
                    await performer_states.PerformerStart.performer_menu.set()
                    orders = await performers_get.performer_view_list_orders(message.from_user.id)
                    orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                    promo = await performers_get.check_commission_promo(message.from_user.id)
                    jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                           reply_markup=markup_performer.main_menu(jobs))
                else:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"Профиль <b>Заказчика</b>:\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID : <b>{customer.user_id}</b>\n"
                                           f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                           f"Никнейм <b>@{customer.username}</b>\n"
                                           f"{config.KEYBOARD.get('TELEPHONE')} "
                                           f"Номер <b>{customer.telephone}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Имя <b>{customer.first_name}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Фамилия <b>{customer.last_name}</b>\n"
                                           f"{config.KEYBOARD.get('STAR')} "
                                           f"Рейтинг <b>{customer.customer_rating}</b>\n"
                                           f"{config.KEYBOARD.get('CHECK_BOX_WITH_CHECK')} "
                                           f"Заказов создано - <b>{customer.created_orders}</b>\n"
                                           f"{config.KEYBOARD.get('CROSS_MARK')} "
                                           f"Заказов отменено - <b>{customer.canceled_orders}</b>\n"
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                           f"Заказов завершено - <b>{customer.completed_orders}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}")
            if message.text == f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
                await performer_states.PerformerStart.orders.set()
                orders = await performers_get.performer_view_list_orders(message.from_user.id)
                orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       "Выберите тип заказа",
                                       reply_markup=markup_performer.performer_type_orders(orders, orders_loading))

    @staticmethod
    async def detail_task(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order = await performers_get.performer_view_order(data.get("order_id"))
            customer = await customers_get.customer_select(data.get("user_id"))
        if message.video_note:
            await bot.send_video_note(customer.user_id, message.video_note.file_id)
            await bot.send_message(message.from_user.id,
                                   "Вы отправили Видео сообщение Заказчику!")
            await bot.send_message(customer.user_id,
                                   "Исполнитель отправил вам Видео сообщение, чтобы ему ответить "
                                   "Вам нужно зайти в 'Мои Заказы', далее 'В работе', далее "
                                   "выбираете ваш Заказ, после этого можете отправлять ответ")
        if message.voice:
            await bot.send_voice(customer.user_id, message.voice.file_id)
            await bot.send_message(message.from_user.id,
                                   "Вы отправили Аудио сообщение Заказчику!")
            await bot.send_message(customer.user_id,
                                   "Исполнитель отправил вам Аудио сообщение, чтобы ему ответить "
                                   "Вам нужно зайти в 'Мои Заказы', далее 'В работе', далее "
                                   "выбираете ваш Заказ, после этого можете отправлять ответ")
        if message.text:
            if "Позвонить/написать заказчику" in message.text:
                end_order = await performers_get.performer_get_status_order(data.get("order_id"))
                if end_order is None:
                    await performer_states.PerformerStart.performer_menu.set()
                    orders = await performers_get.performer_view_list_orders(message.from_user.id)
                    orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                    promo = await performers_get.check_commission_promo(message.from_user.id)
                    jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                           reply_markup=markup_performer.main_menu(jobs))
                else:
                    await bot.send_message(message.from_user.id,
                                           f"Вот его номер телефона {customer.telephone}\n"
                                           f"Или напишите ему в телеграм @{customer.username}")
            if "Детали заказа" in message.text:
                end_order = await performers_get.performer_get_status_order(data.get("order_id"))
                if end_order is None:
                    await performer_states.PerformerStart.performer_menu.set()
                    orders = await performers_get.performer_view_list_orders(message.from_user.id)
                    orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                    promo = await performers_get.check_commission_promo(message.from_user.id)
                    jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                           reply_markup=markup_performer.main_menu(jobs))
                else:
                    if order.image:
                        await bot.send_photo(message.from_user.id, order.image)
                    if order.video:
                        await bot.send_video(message.from_user.id, order.video)
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                           f"Категория - <b>{order.category_delivery}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <code>{order.order_id}</code>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(order.geo_position_from.split())}'>"
                                           f"{order.geo_position_from}</a>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(order.geo_position_to.split())}'>"
                                           f"{order.geo_position_to}</a>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{order.description}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена - <b>{order.price}</b>\n"
                                           f"{config.KEYBOARD.get('MONEY_BAG')} "
                                           f"Ценность этого товара - <b>{order.order_worth}</b>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{order.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
                                           f"Заказ взят: <b>{order.order_get}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n",
                                           disable_web_page_preview=True)
            if "Статус заказа" in message.text:
                end_order = await performers_get.performer_get_status_order(data.get("order_id"))
                if end_order is None:
                    await performer_states.PerformerStart.performer_menu.set()
                    orders = await performers_get.performer_view_list_orders(message.from_user.id)
                    orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                    promo = await performers_get.check_commission_promo(message.from_user.id)
                    jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                           reply_markup=markup_performer.main_menu(jobs))
                else:
                    arrive = await performers_get.performer_arrive_info(data.get("order_id"))
                    await performer_states.PerformerDetailsTasksStatus.enter_status.set()
                    if int(arrive) > 0:
                        await bot.send_message(message.from_user.id,
                                               "Вы вошли в статус заказа, тут вы можете отменить заказ, "
                                               "Завершить заказ или проверить статус заказа для его закрытия",
                                               reply_markup=markup_performer.details_task_status(arrive))
                    if int(arrive) <= 0:
                        await bot.send_message(message.from_user.id,
                                               "Вы вошли в статус заказа, тут вы можете отменить заказ, "
                                               "Завершить заказ или проверить статус заказа для его закрытия",
                                               reply_markup=markup_performer.details_task_status_end())
            if "Профиль заказчика" in message.text:
                end_order = await performers_get.performer_get_status_order(data.get("order_id"))
                if end_order is None:
                    await performer_states.PerformerStart.performer_menu.set()
                    orders = await performers_get.performer_view_list_orders(message.from_user.id)
                    orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                    promo = await performers_get.check_commission_promo(message.from_user.id)
                    jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                    await bot.send_message(message.from_user.id,
                                           f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                           reply_markup=markup_performer.main_menu(jobs))
                else:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"Профиль <b>Заказчика</b>:\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID : <b>{customer.user_id}</b>\n"
                                           f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                           f"Никнейм <b>@{customer.username}</b>\n"
                                           f"{config.KEYBOARD.get('TELEPHONE')} "
                                           f"Номер <b>{customer.telephone}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Имя <b>{customer.first_name}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Фамилия <b>{customer.last_name}</b>\n"
                                           f"{config.KEYBOARD.get('STAR')} "
                                           f"Рейтинг <b>{customer.customer_rating}</b>\n"
                                           f"{config.KEYBOARD.get('CHECK_BOX_WITH_CHECK')} "
                                           f"Заказов создано - <b>{customer.created_orders}</b>\n"
                                           f"{config.KEYBOARD.get('CROSS_MARK')} "
                                           f"Заказов отменено - <b>{customer.canceled_orders}</b>\n"
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                           f"Заказов завершено - <b>{customer.completed_orders}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}")
            if "Вернуться в главное меню" in message.text:
                await performer_states.PerformerStart.performer_menu.set()
                orders = await performers_get.performer_view_list_orders(message.from_user.id)
                orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                promo = await performers_get.check_commission_promo(message.from_user.id)
                jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                       reply_markup=markup_performer.main_menu(jobs))
            if "Назад" in message.text:
                await performer_states.PerformerStart.orders.set()
                orders = await performers_get.performer_view_list_orders(message.from_user.id)
                orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       "Выберите тип заказа",
                                       reply_markup=markup_performer.performer_type_orders(orders, orders_loading))


class PerformerDetailsTasksStatus:
    @staticmethod
    async def details_status(message: types.Message, state: FSMContext):
        if "Отменить заказ" in message.text:
            async with state.proxy() as data:
                status = await general_get.check_details_status(data.get("order_id"))
            if status is None:
                await bot.send_message(message.from_user.id,
                                       "Заказ закрыт")
                orders = await performers_get.performer_view_list_orders(message.from_user.id)
                orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                promo = await performers_get.check_commission_promo(message.from_user.id)
                jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                       reply_markup=markup_performer.main_menu(jobs))
                await performer_states.PerformerStart.performer_menu.set()
            if status:
                if status.performer_status:
                    await bot.send_message(message.from_user.id,
                                           "Вы уже не сможете отменить заказ так как вы его завершили",
                                           reply_markup=markup_performer.details_task_status_end())
                    await performer_states.PerformerDetailsTasksStatus.enter_status.set()
                else:
                    await bot.send_message(message.from_user.id,
                                           "Вы хотите отменить заказ ?\n"
                                           "С вас спишется 5% от стоимости заказа",
                                           reply_markup=markup_performer.inline_cancel_task())
        if "Завершить заказ" in message.text:
            async with state.proxy() as data:
                status = await general_get.check_details_status(data.get("order_id"))
            if status is None:
                await bot.send_message(message.from_user.id,
                                       "Заказ закрыт")
                orders = await performers_get.performer_view_list_orders(message.from_user.id)
                orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                promo = await performers_get.check_commission_promo(message.from_user.id)
                jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                       reply_markup=markup_performer.main_menu(jobs))
                await performer_states.PerformerStart.performer_menu.set()
            if status:
                if status.performer_status:
                    await bot.send_message(message.from_user.id,
                                           "Вы уже завершали заказ",
                                           reply_markup=markup_performer.details_task_status_end())
                    await performer_states.PerformerDetailsTasksStatus.enter_status.set()
                else:
                    await bot.send_message(message.from_user.id,
                                           "Вас все устраивает ?",
                                           reply_markup=markup_performer.markup_clean)
                    await bot.send_message(message.from_user.id,
                                           "Хотите завершить заказ ?",
                                           reply_markup=markup_performer.inline_close_task())
        if "Проверить статус заказа" in message.text:
            await bot.send_message(message.from_user.id, "Проверяем статус заказа...")
            async with state.proxy() as data:
                status = await general_get.check_details_status(data.get("order_id"))
            if status is not None:
                if status.performer_status == 1:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}"
                                           f"С вашей стороны заказ помечен как ВЫПОЛНЕННЫЙ!"
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}")

                if status.performer_status == 0:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('CROSS_MARK')}"
                                           f"С вашей стороны заказ помечен как НЕ ВЫПОЛНЕННЫЙ"
                                           f"{config.KEYBOARD.get('CROSS_MARK')}")
                if status.customer_status == 1:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}"
                                           f"Со стороны заказчика помечен как ВЫПОЛНЕННЫЙ"
                                           f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}")
                if status.customer_status == 0:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('CROSS_MARK')}"
                                           f"Со стороны заказчика помечен как НЕ ВЫПОЛНЕННЫЙ"
                                           f"{config.KEYBOARD.get('CROSS_MARK')}")
            else:
                await bot.send_message(message.from_user.id,
                                       "Заказ закрыт")
                orders = await performers_get.performer_view_list_orders(message.from_user.id)
                orders_loading = await performers_get.performer_loader_order(message.from_user.id)
                promo = await performers_get.check_commission_promo(message.from_user.id)
                jobs = await performers_get.performer_check_jobs_offers(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                       reply_markup=markup_performer.main_menu(jobs))
                await performer_states.PerformerStart.performer_menu.set()
        if "Сообщить о прибытии" in message.text:
            async with state.proxy() as data:
                order_id = data.get("order_id")
                order = await general_get.order_select(order_id)
                await performers_set.performer_change_arrive_status(order_id)
                res = await performers_get.performer_arrive_info(order_id)
            if int(res) <= 0:
                await bot.send_message(order.user_id,
                                       f"Курьер на месте, вас ожидает\n"
                                       f"Ждёт от вас обратной связи\n"
                                       f"Заказ {order_id}",
                                       reply_markup=markup_performer.inline_approve_arrive(message.from_user.id))
                await bot.send_message(message.from_user.id,
                                       "Заказчику отправлено сообщение о вашем прибытии!",
                                       reply_markup=markup_performer.details_task_status_end())
            if int(res) > 0:
                await bot.send_message(order.user_id,
                                       f"Курьер на месте, вас ожидает\n"
                                       f"Ждёт от вас обратной связи\n"
                                       f"Заказ {order_id}",
                                       reply_markup=markup_performer.inline_approve_arrive(message.from_user.id))
                await bot.send_message(message.from_user.id,
                                       "Заказчику отправлено сообщение о вашем прибытии!",
                                       reply_markup=markup_performer.details_task_status(res))
        if "Вернуться в детали заказа" in message.text:
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в детали заказа",
                                   reply_markup=markup_performer.details_task())
            await performer_states.PerformerDetailsTasks.enter_task.set()

    @staticmethod
    async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            order = await performers_get.performer_view_order(data.get("order_id"))
            price = order.price
            commission = (price * 5) / 100
            await performers_set.performer_cancel_order(callback.from_user.id, data.get("order_id"))
            await performers_set.performer_set_commission_for_cancel(callback.from_user.id, commission)
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CROSS_MARK') * 14}")
            await bot.send_message(data.get("user_id"),
                                   f"Ваша заказ <b>{data.get('order_id')}</b> был отменён исполнителем!")
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CROSS_MARK') * 14}")
        await performer_states.PerformerStart.performer_menu.set()
        await bot.send_message(callback.from_user.id,
                               "Вы отменили заказ!")
        orders = await performers_get.performer_view_list_orders(callback.from_user.id)
        orders_loading = await performers_get.performer_loader_order(callback.from_user.id)
        promo = await performers_get.check_commission_promo(callback.from_user.id)
        jobs = await performers_get.performer_check_jobs_offers(callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                               reply_markup=markup_performer.main_menu(jobs))

    @staticmethod
    async def no_cancel_order(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            res = await performers_get.performer_arrive_info(data.get("order_id"))
        if int(res) <= 0:
            await bot.send_message(callback.from_user.id,
                                   "Хорошо что передумали, заказ будет сделан!",
                                   reply_markup=markup_performer.details_task_status_end())
        if int(res) > 0:
            await bot.send_message(callback.from_user.id,
                                   "Хорошо что передумали, заказ будет сделан!",
                                   reply_markup=markup_performer.details_task_status(res))

    @staticmethod
    async def close_order(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 10}\n"
                                   f"Ваша задача <b>{data.get('order_id')}</b> "
                                   f"была помечена Исполнителем как выполненная!\n"
                                   f"Посмотрите в разделе 'Проверить статус заказа'\n"
                                   f"Если Заказчик и Исполнитель завершили заказ, "
                                   f"то заказ будет перемещен в раздел Завершенных заказов\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 10}")
            await performers_set.performer_set_order_status(data.get("order_id"),
                                                            datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
        await bot.send_message(callback.from_user.id,
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 10}\n"
                               "Отлично! Вы установили статус заказа завершенным\n"
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 10}")
        await bot.send_message(callback.from_user.id,
                               "Оцените заказчика",
                               reply_markup=markup_performer.rating())
        await performer_states.PerformerDetailsTasksStatus.rating.set()

    @staticmethod
    async def no_close(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            res = await performers_get.performer_arrive_info(data.get("order_id"))
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        if int(res) <= 0:
            await bot.send_message(callback.from_user.id,
                                   "Сделайте до конца, а потом завершайте",
                                   reply_markup=markup_performer.details_task_status_end())
        if int(res) > 0:
            await bot.send_message(callback.from_user.id,
                                   "Сделайте до конца, а потом завершайте",
                                   reply_markup=markup_performer.details_task_status(res))

    @staticmethod
    async def rating(message: types.Message, state: FSMContext):
        rate = ['1', '2', '3', '4', '5', 'Пропустить']
        if message.text in rate:
            if message.text == "Пропустить":
                await bot.send_message(message.from_user.id,
                                       f"Вы не поставили оценку Заказчику\n"
                                       f"Вы можете оставить отзыв, или войти в детали заказа",
                                       reply_markup=markup_performer.details_task_status_review())
                await performer_states.PerformerDetailsTasksStatus.review.set()
            else:
                async with state.proxy() as data:
                    await performers_set.performer_set_rating_to_customer(data.get("user_id"),
                                                                          message.text)
                    await performers_set.performer_set_rating_to_customer_in_review_db(data.get("order_id"),
                                                                                       message.text)
                await bot.send_message(message.from_user.id,
                                       f"Вы поставили оценку Заказчику - <b>{message.text}</b>\n"
                                       f"Спасибо за оценку!\n"
                                       f"Вы можете оставить отзыв, или войти в детали заказа",
                                       reply_markup=markup_performer.details_task_status_review())
                await performer_states.PerformerDetailsTasksStatus.review.set()
        else:
            await bot.send_message(message.from_user.id, "Надо поставить оценку 1,2,3,4,5")

    @staticmethod
    async def review(message: types.Message, state: FSMContext):
        if "Войти в детали заказа" in message.text:
            await bot.send_message(message.from_user.id,
                                   "Вы вошли в детали заказа\n"
                                   "Здесь вы сможете отправить Заказчику <b>Видео сообщение</b> "
                                   "и <b>Аудио сообщение</b>",
                                   reply_markup=markup_performer.details_task_status_end())
            await performer_states.PerformerDetailsTasksStatus.enter_status.set()
        else:
            async with state.proxy() as data:
                await performers_set.performer_set_review_to_customer_in_review_db(data.get("order_id"),
                                                                                   message.text)
                await bot.send_message(message.from_user.id,
                                       "Отзыв отправлен!",
                                       reply_markup=markup_performer.details_task_status_end())
                await performer_states.PerformerDetailsTasksStatus.enter_status.set()
