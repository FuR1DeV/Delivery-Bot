import calendar
from collections import Counter
from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import bot
from data.commands import customers_get, customers_set, performers_get, performers_set
from markups import markup_customer
from states import customer_states
from settings import config
from settings.config import KEYBOARD


class CustomerMain:
    @staticmethod
    async def hi_customer(callback: types.CallbackQuery):
        customer = await customers_get.customer_select(callback.from_user.id)
        if customer is None:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button = types.KeyboardButton(text='Запрос телефона', request_contact=True)
            keyboard.add(button)
            await bot.send_message(callback.from_user.id,
                                   f"{callback.from_user.first_name}\n"
                                   f"Поделитесь с нами вашим номером телефона!",
                                   reply_markup=keyboard)
            await customer_states.CustomerPhone.phone.set()
        elif customer.ban == 0:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(callback.from_user.id,
                                   "Спасибо что пользуетесь нашим ботом!")
            not_at_work = await customers_get.customer_all_orders_not_at_work(callback.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(callback.from_user.id)
            loading = await customers_get.customer_all_orders_loading(callback.from_user.id)
            await bot.send_message(callback.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
        else:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await bot.send_message(callback.from_user.id, "Вы заблокированы! Обратитесь в техподдержку!")

    @staticmethod
    async def phone(message: types.Message):
        if message.contact.user_id == message.from_user.id:
            res = message.contact.phone_number[-10:]
            await customers_set.customer_add(message.from_user.id,
                                             message.from_user.username,
                                             f'+7{res}',
                                             message.from_user.first_name,
                                             message.from_user.last_name)
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Спасибо что пользуетесь нашим ботом!",
                                   reply_markup=markup_customer.main_menu())
        else:
            await bot.send_message(message.from_user.id,
                                   "Это не ваш номер телефона! \n"
                                   "Нажмите /start чтобы начать заново")

    @staticmethod
    async def main(message: types.Message):
        not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
        at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
        loading = await customers_get.customer_all_orders_loading(message.from_user.id)
        await bot.send_message(message.from_user.id,
                               f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                               reply_markup=markup_customer.main_menu())
        await customer_states.CustomerStart.customer_menu.set()

    @staticmethod
    async def customer_menu(message: types.Message, state: FSMContext):
        await state.finish()
        if "Мой профиль" in message.text:
            customer = await customers_get.customer_select(message.from_user.id)
            await customer_states.CustomerProfile.my_profile.set()
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"Ваш профиль <b>Заказчика</b>:\n"
                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                   f"Ваш ID: <b>{message.from_user.id}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Ваш никнейм <b>@{message.from_user.username}</b>\n"
                                   f"{config.KEYBOARD.get('TELEPHONE')} "
                                   f"Ваш номер <b>{customer.telephone}</b>\n"
                                   f"{config.KEYBOARD.get('STAR')} "
                                   f"Ваш рейтинг <b>"
                                   f"{customer.customer_rating}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   reply_markup=markup_customer.customer_profile())
        if "Создать заказ" in message.text:
            await customer_states.CustomerCreateTask.create.set()
            await bot.send_message(message.from_user.id,
                                   "Вы можете создать новый заказ с Компьютера или с Телефона",
                                   reply_markup=markup_customer.approve())
        if "Мои заказы" in message.text:
            orders_not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            orders_at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            orders_loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   "Выберите тип заказа",
                                   reply_markup=markup_customer.customer_type_orders(len(orders_not_at_work),
                                                                                     len(orders_at_work),
                                                                                     len(orders_loading)))
            await customer_states.CustomerStart.orders.set()
        if "Завершенные заказы" in message.text:
            res = await customers_get.customer_all_completed_orders(message.from_user.id)
            if res:
                finished_orders = InlineKeyboardMarkup()
                year = []
                for i in res:
                    year.append(datetime.strptime(i.order_end, '%d-%m-%Y, %H:%M:%S').year)
                res_years = Counter(year)
                for k, v in res_years.items():
                    finished_orders.insert(InlineKeyboardButton(text=f"{k} ({v})",
                                                                callback_data=f"year_finish_{k}"))
                await bot.send_message(message.from_user.id,
                                       "<b>Выберите год</b>\n"
                                       "В скобках указано количество завершенных заказов",
                                       reply_markup=finished_orders)
                await customer_states.CustomerStart.customer_menu.set()
            else:
                await customer_states.CustomerStart.customer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "У вас еще нет завершенных заказов!")
        if "Помощь" in message.text:
            await customer_states.CustomerHelp.help.set()
            await bot.send_message(message.from_user.id,
                                   "Опишите вашу проблему, можете прикрепить фото или видео\n"
                                   "Когда закончите сможете вернуться в главное меню",
                                   reply_markup=markup_customer.photo_or_video_help())

    @staticmethod
    async def orders(message: types.Message):
        category = {f"Цветы": f"{KEYBOARD.get('BOUQUET')}",
                    f"Подарки": f"{KEYBOARD.get('WRAPPED_GIFT')}",
                    f"Кондитерка": f"{KEYBOARD.get('SHORTCAKE')}",
                    f"Документы": f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')}",
                    f"Погрузка/Разгрузка": f"{KEYBOARD.get('ARROWS_BUTTON')}",
                    f"Другое": f"{KEYBOARD.get('INPUT_LATIN_LETTERS')}"}
        if "Заказы Доставки" in message.text:
            orders_not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            orders_at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   "В ожидании или в работе ?",
                                   reply_markup=markup_customer.orders_type_work(len(orders_not_at_work),
                                                                                 len(orders_at_work)))
        if "Заказы Грузчики" in message.text:
            orders_loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            if orders_loading:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for i in orders_loading:
                    if i.image:
                        await bot.send_photo(message.from_user.id, i.image)
                    if i.video:
                        await bot.send_video(message.from_user.id, i.video)
                    loaders = [await performers_get.performer_select(v) for v in i.persons_list]
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа для Грузчиков</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(i.geo_position.split())}'>{i.geo_position}</a>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Сколько Грузчиков - <b>{i.person}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Уже Грузчиков - <b>{i.count_person}</b>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{i.description}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена за 1 час - <b>{i.price}</b>\n"
                                           f"{config.KEYBOARD.get('STOPWATCH')} "
                                           f"Начало работ: <b>{i.start_time}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <b>{i.order_id}</b>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{i.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                           f"Действует до: <b>{i.order_expired}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Грузчики: {' | '.join([k.username for k in loaders])}\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n",
                                           disable_web_page_preview=True)
                    keyboard.add(f"{KEYBOARD.get('ARROWS_BUTTON')} {i.order_id} {KEYBOARD.get('ARROWS_BUTTON')}")
                keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
                refresh = InlineKeyboardMarkup()
                r = InlineKeyboardButton(text="Обновить", callback_data="refresh_loading")
                refresh.insert(r)
                await bot.send_message(message.from_user.id,
                                       "Нажмите обновить для обновление рейтинга",
                                       reply_markup=refresh)
                await bot.send_message(message.from_user.id,
                                       "Выберите ID задачи чтобы войти в детали заказа",
                                       reply_markup=keyboard)
                await customer_states.CustomerDetailsTasks.my_tasks.set()
            else:
                await bot.send_message(message.from_user.id,
                                       "У вас нет созданных заказов для Грузчиков")
        if "В ожидании" in message.text:
            orders = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            if orders:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for i in orders:
                    order_get = "Пока не взят"
                    icon_category = None
                    icon = None
                    p_status = None
                    for k, v in category.items():
                        if i.category_delivery == k:
                            icon_category = v
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
                    if i.order_get is not None:
                        order_get = i.order_get
                    if i.image:
                        await bot.send_photo(message.from_user.id, i.image)
                    if i.video:
                        await bot.send_video(message.from_user.id, i.video)
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{icon_category} "
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
                                           f"Ценность вашего товара - <b>{i.order_worth}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <b>{i.order_id}</b>\n"
                                           f"{icon} "
                                           f"Исполнитель - <b>{p_status}</b>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{i.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
                                           f"Заказ взят: <b>{order_get}</b>\n"
                                           f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                           f"Действует до: <b>{i.order_expired}</b>\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n",
                                           disable_web_page_preview=True)
                    keyboard.add(f"{icon} {i.order_id} {icon_category}")
                keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
                refresh = InlineKeyboardMarkup()
                r = InlineKeyboardButton(text="Обновить", callback_data="refresh")
                refresh.insert(r)
                await bot.send_message(message.from_user.id,
                                       "Нажмите обновить для обновление рейтинга",
                                       reply_markup=refresh)
                await bot.send_message(message.from_user.id,
                                       "Выберите ID задачи чтобы войти в детали заказа",
                                       reply_markup=keyboard)
                await customer_states.CustomerDetailsTasks.my_tasks.set()
            else:
                await bot.send_message(message.from_user.id,
                                       "У вас нет созданных заказов в ожидании")
        if "В работе" in message.text:
            orders = await customers_get.customer_all_orders_in_work(message.from_user.id)
            if orders:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for i in orders:
                    order_get = "Пока не взят"
                    icon_category = None
                    icon = None
                    p_status = None
                    for k, v in category.items():
                        if i.category_delivery == k:
                            icon_category = v
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
                    if i.order_get is not None:
                        order_get = i.order_get
                    if i.image:
                        await bot.send_photo(message.from_user.id, i.image)
                    if i.video:
                        await bot.send_video(message.from_user.id, i.video)
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{icon_category} "
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
                                           f"Ценность вашего товара - <b>{i.order_worth}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <b>{i.order_id}</b>\n"
                                           f"{icon} "
                                           f"Исполнитель - <b>{p_status}</b>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{i.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
                                           f"Заказ взят: <b>{order_get}</b>\n"
                                           f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                           f"Действует до: <b>{i.order_expired}</b>\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n",
                                           disable_web_page_preview=True)
                    keyboard.add(f"{icon} {i.order_id} {icon_category}")
                keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
                await bot.send_message(message.from_user.id,
                                       "Выберите ID задачи чтобы войти в детали заказа",
                                       reply_markup=keyboard)
                await customer_states.CustomerDetailsTasks.my_tasks.set()
            else:
                await bot.send_message(message.from_user.id,
                                       "У вас нет заказов в работе")
        if "Назад" in message.text:
            orders_not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            orders_at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            orders_loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   "Выберите тип заказа",
                                   reply_markup=markup_customer.customer_type_orders(len(orders_not_at_work),
                                                                                     len(orders_at_work),
                                                                                     len(orders_loading)))
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню":
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
            await customer_states.CustomerStart.customer_menu.set()

    @staticmethod
    async def refresh(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        orders = await customers_get.customer_all_orders_not_at_work(callback.from_user.id)
        category = {f"Цветы": f"{KEYBOARD.get('BOUQUET')}",
                    f"Подарки": f"{KEYBOARD.get('WRAPPED_GIFT')}",
                    f"Кондитерка": f"{KEYBOARD.get('SHORTCAKE')}",
                    f"Документы": f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')}",
                    f"Погрузка/Разгрузка": f"{KEYBOARD.get('ARROWS_BUTTON')}",
                    f"Другое": f"{KEYBOARD.get('INPUT_LATIN_LETTERS')}"}
        if orders:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i in orders:
                order_get = "Пока не взят"
                icon_category = None
                icon = None
                p_status = None
                for k, v in category.items():
                    if i.category_delivery == k:
                        icon_category = v
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
                if i.order_get is not None:
                    order_get = i.order_get
                if i.image:
                    await bot.send_photo(callback.from_user.id, i.image)
                if i.video:
                    await bot.send_video(callback.from_user.id, i.video)
                await bot.send_message(callback.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"<b>Детали заказа</b>\n"
                                       f"{icon_category} "
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
                                       f"Ценность вашего товара - <b>{i.order_worth}</b>\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID заказа - <b>{i.order_id}</b>\n"
                                       f"{icon} "
                                       f"Исполнитель - <b>{p_status}</b>\n"
                                       f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                       f"Заказ создан: <b>{i.order_create}</b>\n"
                                       f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
                                       f"Заказ взят: <b>{order_get}</b>\n"
                                       f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                       f"Действует до: <b>{i.order_expired}</b>\n"
                                       f"{config.KEYBOARD.get('BAR_CHART')} "
                                       f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}\n",
                                       disable_web_page_preview=True)
                keyboard.add(f"{icon} {i.order_id} {icon_category}")
            keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
            refresh = InlineKeyboardMarkup()
            r = InlineKeyboardButton(text="Обновить", callback_data="refresh")
            refresh.insert(r)
            await bot.send_message(callback.from_user.id,
                                   "Нажмите обновить для обновление рейтинга",
                                   reply_markup=refresh)
            await bot.send_message(callback.from_user.id,
                                   "Выберите ID задачи чтобы войти в детали заказа",
                                   reply_markup=keyboard)
            await customer_states.CustomerDetailsTasks.my_tasks.set()

    @staticmethod
    async def refresh_loading(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        orders_loading = await customers_get.customer_all_orders_loading(callback.from_user.id)
        if orders_loading:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i in orders_loading:
                if i.image:
                    await bot.send_photo(callback.from_user.id, i.image)
                if i.video:
                    await bot.send_video(callback.from_user.id, i.video)
                loaders = [await performers_get.performer_select(v) for v in i.persons_list]
                await bot.send_message(callback.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"<b>Детали заказа для Грузчиков</b>\n"
                                       f"{config.KEYBOARD.get('A_BUTTON')} "
                                       f"Откуда - <a href='https://yandex.ru/maps/?text="
                                       f"{'+'.join(i.geo_position.split())}'>{i.geo_position}</a>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Сколько Грузчиков - <b>{i.person}</b>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Уже Грузчиков - <b>{i.count_person}</b>\n"
                                       f"{config.KEYBOARD.get('CLIPBOARD')} "
                                       f"Описание - <b>{i.description}</b>\n"
                                       f"{config.KEYBOARD.get('DOLLAR')} "
                                       f"Цена за 1 час - <b>{i.price}</b>\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID заказа - <b>{i.order_id}</b>\n"
                                       f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                       f"Заказ создан: <b>{i.order_create}</b>\n"
                                       f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                       f"Действует до: <b>{i.order_expired}</b>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Грузчики: {' | '.join([k.username for k in loaders])}\n"
                                       f"{config.KEYBOARD.get('BAR_CHART')} "
                                       f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}\n",
                                       disable_web_page_preview=True)
                keyboard.add(f"{KEYBOARD.get('ARROWS_BUTTON')} {i.order_id} {KEYBOARD.get('ARROWS_BUTTON')}")
            keyboard.add(f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
            refresh = InlineKeyboardMarkup()
            r = InlineKeyboardButton(text="Обновить", callback_data="refresh_loading")
            refresh.insert(r)
            await bot.send_message(callback.from_user.id,
                                   "Нажмите обновить для обновление рейтинга",
                                   reply_markup=refresh)
            await bot.send_message(callback.from_user.id,
                                   "Выберите ID задачи чтобы войти в детали заказа",
                                   reply_markup=keyboard)
            await customer_states.CustomerDetailsTasks.my_tasks.set()

    @staticmethod
    async def choose_month(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        year = callback.data[12:]
        async with state.proxy() as data:
            data["year"] = year
        res = await customers_get.customer_get_finished_orders_year(callback.from_user.id,
                                                                    year)
        finished_orders = InlineKeyboardMarkup()
        months = []
        for i in res:
            months.append(calendar.month_name[datetime.strptime(i.order_end, '%d-%m-%Y, %H:%M:%S').month])
        res_months = Counter(months)
        for k, v in res_months.items():
            finished_orders.insert(InlineKeyboardButton(text=f"{k} ({v})",
                                                        callback_data=f"month_finish_{k}"))
        await bot.send_message(callback.from_user.id,
                               "<b>Выберите месяц</b>\n"
                               "В скобках указано кол-во завершенных заказов",
                               reply_markup=finished_orders)

    @staticmethod
    async def choose_day(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        month = callback.data[13:]
        months = {month: index for index, month in enumerate(calendar.month_name) if month}
        for k, v in months.items():
            if k == month:
                month = v
        if len(str(month)) == 1:
            month = f"0{month}"
        async with state.proxy() as data:
            data["month"] = month
        res = await customers_get.customer_get_finished_orders_month(callback.from_user.id,
                                                                     data.get("year"),
                                                                     month)
        finished_orders = InlineKeyboardMarkup()
        days = []
        for i in res:
            days.append(datetime.strptime(i.order_end, '%d-%m-%Y, %H:%M:%S').day)
        res_days = Counter(days)
        for k, v in res_days.items():
            finished_orders.insert(InlineKeyboardButton(text=f"{k} ({v})",
                                                        callback_data=f"day_finish_{k}"))
        await bot.send_message(callback.from_user.id,
                               "<b>Выберите день</b>\n"
                               "В скобках указано кол-во завершенных заказов",
                               reply_markup=finished_orders)

    @staticmethod
    async def choose_job(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        day = callback.data[11:]
        async with state.proxy() as data:
            data["day"] = day
        res = await customers_get.customer_get_finished_orders_day(callback.from_user.id,
                                                                   data.get("year"),
                                                                   data.get("month"),
                                                                   day)
        if res:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            category = {f"Цветы": f"{KEYBOARD.get('BOUQUET')}",
                        f"Подарки": f"{KEYBOARD.get('WRAPPED_GIFT')}",
                        f"Кондитерка": f"{KEYBOARD.get('SHORTCAKE')}",
                        f"Документы": f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')}",
                        f"Погрузка/Разгрузка": f"{KEYBOARD.get('ARROWS_BUTTON')}",
                        f"Другое": f"{KEYBOARD.get('INPUT_LATIN_LETTERS')}"}
            icon_category = None
            for i in res:
                for k, v in category.items():
                    if i.category_delivery == k:
                        icon_category = v
                icon = None
                p_status = None
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
                await bot.send_message(callback.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"<b>Детали заказа</b>\n"
                                       f"{icon_category} "
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
                                       f"Ценность вашего товара - <b>{i.order_worth}</b>\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID заказа - <b>{i.order_id}</b>\n"
                                       f"{icon} "
                                       f"Исполнитель - <b>{p_status}</b>\n"
                                       f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                       f"Заказ создан: <b>{i.order_create}</b>\n"
                                       f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
                                       f"Заказ взят: <b>{i.order_get}</b>\n"
                                       f"{config.KEYBOARD.get('BLUE_CIRCLE')} "
                                       f"Заказ завершен: <b>{i.order_end}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}",
                                       disable_web_page_preview=True)
                keyboard.add(f"{i.order_id}")
                async with state.proxy() as data:
                    data[i.order_id] = {
                        'Откуда': i.geo_position_from,
                        'Куда': i.geo_position_to,
                        'ID заказа': i.order_id,
                        'ID исполнителя': i.in_work,
                        'Бюджет': i.price,
                    }
            keyboard.add("Вернуться в главное меню")
            await bot.send_message(callback.from_user.id,
                                   "Выберите ID задачи чтобы войти в детали заказа",
                                   reply_markup=keyboard)
            await customer_states.CustomerHistory.enter_history.set()

    @staticmethod
    async def customer_approve(callback: types.CallbackQuery):
        res = callback.data.split("-")
        order_id, performer_id = res[2], int(res[0])
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        exist = await customers_get.customer_get_status_order(order_id)
        if exist:
            await bot.send_message(callback.from_user.id,
                                   "Вы уже взяли Исполнителя!")
        else:
            await bot.send_message(performer_id,
                                   f"{config.KEYBOARD.get('CHECK_BOX_WITH_CHECK') * 5}\n"
                                   f"Заказчик <b>{callback.from_user.id}</b> "
                                   f"одобрил ваш запрос по заказу <b>{res[2]}\n</b>"
                                   f"{config.KEYBOARD.get('CHECK_BOX_WITH_CHECK') * 5}")
            await performers_set.performer_set_order(performer_id,
                                                     order_id,
                                                     datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
            await bot.send_message(callback.from_user.id,
                                   "Вы взяли Исполнителя!")
            not_at_work = await customers_get.customer_all_orders_not_at_work(callback.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(callback.from_user.id)
            loading = await customers_get.customer_all_orders_loading(callback.from_user.id)
            await bot.send_message(callback.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
            await customer_states.CustomerStart.customer_menu.set()

    @staticmethod
    async def customer_decline(callback: types.CallbackQuery):
        res = callback.message.text.split()
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(res[-1],
                               f"{config.KEYBOARD.get('CROSS_MARK')} "
                               f"Заказчик <b>{callback.from_user.id}</b> "
                               f"не одобрил ваш запрос по заказу <b>{res[2]}</b>. "
                               f"Возможно ему не понравился ваш рейтинг "
                               f"{config.KEYBOARD.get('CROSS_MARK')}")

    @staticmethod
    async def customer_view_perf_profile(callback: types.CallbackQuery):
        performer_id = int(callback.data[27:])
        personal_data = await customers_get.customer_check_personal_data(performer_id)
        await bot.send_message(callback.from_user.id,
                               f"Имя - {personal_data.real_first_name}\n"
                               f"Фамилия - {personal_data.real_last_name}")
        await bot.send_photo(callback.from_user.id,
                             personal_data.selfie)

    @staticmethod
    async def proposal_from_performer_yes(callback: types.CallbackQuery):
        res = callback.message.text.split()
        new_price, order_id, performer_id = res[4], res[11], res[7]
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        exist = await customers_get.customer_get_status_order(order_id)
        if exist:
            await bot.send_message(callback.from_user.id,
                                   "Вы уже взяли Исполнителя!")
        else:
            await bot.send_message(res[7],
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                   f"Заказчик <b>{callback.from_user.id}</b> "
                                   f"одобрил ваше предложение о новой цене <b>{res[4]}</b>\n"
                                   f"По заказу <b>{res[11]}</b>\n"
                                   f"<b>Вы успешно взяли новый Заказ!</b>"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}")
            await performers_set.performer_set_order(int(performer_id),
                                                     order_id,
                                                     datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
            await performers_set.add_new_price(order_id, new_price)
            await bot.send_message(callback.from_user.id,
                                   "Вы взяли Исполнителя!")
            not_at_work = await customers_get.customer_all_orders_not_at_work(callback.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(callback.from_user.id)
            loading = await customers_get.customer_all_orders_loading(callback.from_user.id)
            await bot.send_message(callback.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
            await customer_states.CustomerStart.customer_menu.set()

    @staticmethod
    async def proposal_from_performer_no(callback: types.CallbackQuery):
        res = callback.message.text.split()
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(res[7],
                               f"{config.KEYBOARD.get('CROSS_MARK')} "
                               f"Заказчик <b>{callback.from_user.id}</b> отказался от вашего предложения "
                               f"{config.KEYBOARD.get('CROSS_MARK')}")
        await bot.send_message(callback.from_user.id,
                               f"Вы отказались от предложения новой цены <b>{res[4]}</b>, "
                               f"от Исполнителя <b>{res[7]}</b> на ваш заказ <b>{res[11]}</b>")

    @staticmethod
    async def approve_info_arrived(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.data[15:],
                               "Заказчик <b>подтвердил</b> получение информации о вашем прибытии")

    @staticmethod
    async def cancel(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)


class CustomerProfile:
    @staticmethod
    async def customer_profile(message: types.Message):
        if "Главное меню" in message.text:
            not_at_work = await customers_get.customer_all_orders_not_at_work(message.from_user.id)
            at_work = await customers_get.customer_all_orders_in_work(message.from_user.id)
            loading = await customers_get.customer_all_orders_loading(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_customer.text_menu(len(not_at_work), len(at_work), len(loading))}",
                                   reply_markup=markup_customer.main_menu())
            await customer_states.CustomerStart.customer_menu.set()
        if "Статистика по заказам" in message.text:
            customer = await customers_get.customer_count_orders(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} "
                                   f"Всего заказов - <b>{customer[0].created_orders}</b>\n"
                                   f"{config.KEYBOARD.get('WRENCH')} В работе - <b>{customer[1]}</b>\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} Завершенных - "
                                   f"<b>{customer[0].completed_orders}</b>\n"
                                   f"{config.KEYBOARD.get('CROSS_MARK')} Отмененных - "
                                   f"<b>{customer[0].canceled_orders}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}")
