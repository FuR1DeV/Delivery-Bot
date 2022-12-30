import logging
from collections import Counter
from random import randint
from datetime import datetime, timedelta
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, MenuButtonWebApp, WebAppInfo
from geopy.geocoders import Nominatim

from bot import bot, dp
from data.commands import customers_get, customers_set, performers_get, general_set, general_get
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
                                   "Спасибо что пользуетесь нашим ботом!",
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
        await bot.send_message(message.from_user.id,
                               f"{message.from_user.first_name} Вы в главном меню Заказчика",
                               reply_markup=markup_customer.main_menu())
        await customer_states.CustomerStart.customer_menu.set()

    @staticmethod
    async def customer_menu(message: types.Message, state: FSMContext):
        await state.finish()
        if "Мой профиль" in message.text:
            CustomerProfile.register_customer_profile(dp)
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
                                   f"{config.KEYBOARD.get('BAR_CHART')} "
                                   f"Ваш рейтинг <b>"
                                   f"{str(customer.customer_rating)[0:5]}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   reply_markup=markup_customer.customer_profile())
        if "Создать заказ" in message.text:
            CustomerCreateTask.register_customer_create_task(dp)
            CustomerCreateTaskComp.register_customer_create_task_comp(dp)
            await customer_states.CustomerCreateTask.create.set()
            await bot.send_message(message.from_user.id,
                                   "Хотите создать новый заказ ?",
                                   reply_markup=markup_customer.approve())
        if "Мои заказы" in message.text:
            res = await customers_get.customer_all_orders(message.from_user.id)
            category = {f"Цветы": f"{KEYBOARD.get('BOUQUET')}",
                        f"Подарки": f"{KEYBOARD.get('WRAPPED_GIFT')}",
                        f"Кондитерка": f"{KEYBOARD.get('SHORTCAKE')}",
                        f"Документы": f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')}",
                        f"Погрузка/Разгрузка": f"{KEYBOARD.get('ARROWS_BUTTON')}",
                        f"Другое": f"{KEYBOARD.get('INPUT_LATIN_LETTERS')}"}
            if res:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for i in res:
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
                    try:
                        await bot.send_photo(message.from_user.id, i.image)
                        await bot.send_message(message.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"<b>Детали заказа</b>\n"
                                               f"{icon_category} "
                                               f"Категория - <b>{i.category_delivery}</b>\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                               f"{config.KEYBOARD.get('INFORMATION')} "
                                               f"Название - <b>{i.title}</b>\n"
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
                    except:
                        try:
                            await bot.send_video(message.from_user.id, i.video)
                            await bot.send_message(message.from_user.id,
                                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                                   f"<b>Детали заказа</b>\n"
                                                   f"{icon_category} "
                                                   f"Категория - <b>{i.category_delivery}</b>\n"
                                                   f"{config.KEYBOARD.get('A_BUTTON')} "
                                                   f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                                   f"{config.KEYBOARD.get('B_BUTTON')} "
                                                   f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                                   f"{config.KEYBOARD.get('INFORMATION')} "
                                                   f"Название - <b>{i.title}</b>\n"
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
                        except:
                            await bot.send_message(message.from_user.id,
                                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                                   f"<b>Детали заказа</b>\n"
                                                   f"{icon_category} "
                                                   f"Категория - <b>{i.category_delivery}</b>\n"
                                                   f"{config.KEYBOARD.get('A_BUTTON')} "
                                                   f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                                   f"{config.KEYBOARD.get('B_BUTTON')} "
                                                   f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                                   f"{config.KEYBOARD.get('INFORMATION')} "
                                                   f"Название - <b>{i.title}</b>\n"
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
                keyboard.add("Вернуться в главное меню")
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
                CustomerDetailsTasks.register_customer_details_tasks(dp)
            else:
                await bot.send_message(message.from_user.id,
                                       "У вас нет созданных заказов",
                                       reply_markup=markup_customer.main_menu())
                await customer_states.CustomerStart.customer_menu.set()
        if "Завершенные заказы" in message.text:
            try:
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
            except:
                await customer_states.CustomerStart.customer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "У вас еще нет завершенных заказов!")
        if "Помощь" in message.text:
            await customer_states.CustomerHelp.help.set()
            await bot.send_message(message.from_user.id,
                                   "Опишите вашу проблему, можете прикрепить фото или видео\n"
                                   "Когда закончите сможете вернуться в главное меню",
                                   reply_markup=markup_customer.photo_or_video_help())
            CustomerHelp.register_customer_help(dp)

    @staticmethod
    async def refresh(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        res = await customers_get.customer_all_orders(callback.from_user.id)
        category = {f"Цветы": f"{KEYBOARD.get('BOUQUET')}",
                    f"Подарки": f"{KEYBOARD.get('WRAPPED_GIFT')}",
                    f"Кондитерка": f"{KEYBOARD.get('SHORTCAKE')}",
                    f"Документы": f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')}",
                    f"Погрузка/Разгрузка": f"{KEYBOARD.get('ARROWS_BUTTON')}",
                    f"Другое": f"{KEYBOARD.get('INPUT_LATIN_LETTERS')}"}
        if res:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i in res:
                order_get = "Пока не взят"
                icon_category = None
                for k, v in category.items():
                    if i.category_delivery == k:
                        icon_category = v
                try:
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
                    await bot.send_photo(callback.from_user.id, i[7])
                    await bot.send_message(callback.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{icon_category} "
                                           f"Категория - <b>{i.category_delivery}</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                           f"{config.KEYBOARD.get('INFORMATION')} "
                                           f"Название - <b>{i.title}</b>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{i.description}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена - <b>{i.price}</b>\n"
                                           f"{config.KEYBOARD.get('MONEY_BAG')} "
                                           f"Ценность вашего товара - <b>{i.order_worth}</b>\n"
                                           f"{config.KEYBOARD.get('WRENCH')} "
                                           f"В работе - <b>{bool(i.in_work)}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <b>{i.order_id}</b>\n"
                                           f"{icon} "
                                           f"Исполнитель - <b>{p_status}</b>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{i.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                           f"Действует до: <b>{i.order_expired}</b>\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n",
                                           disable_web_page_preview=True)
                    keyboard.add(f"{icon} {i.order_id} {icon_category}")
                except:
                    try:
                        await bot.send_video(callback.from_user.id, i.video)
                        await bot.send_message(callback.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"<b>Детали заказа</b>\n"
                                               f"{icon_category} "
                                               f"Категория - <b>{i.category_delivery}</b>\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                               f"{config.KEYBOARD.get('INFORMATION')} "
                                               f"Название - <b>{i.title}</b>\n"
                                               f"{config.KEYBOARD.get('CLIPBOARD')} "
                                               f"Описание - <b>{i.description}</b>\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} "
                                               f"Цена - <b>{i.price}</b>\n"
                                               f"{config.KEYBOARD.get('MONEY_BAG')} "
                                               f"Ценность вашего товара - <b>{i.order_worth}</b>\n"
                                               f"{config.KEYBOARD.get('WRENCH')} "
                                               f"В работе - <b>{bool(i.in_work)}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID заказа - <b>{i.order_id}</b>\n"
                                               f"{icon} "
                                               f"Исполнитель - <b>{p_status}</b>\n"
                                               f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                               f"Заказ создан: <b>{i.order_create}</b>\n"
                                               f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                               f"Действует до: <b>{i.order_expired}</b>\n"
                                               f"{config.KEYBOARD.get('BAR_CHART')} "
                                               f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}\n",
                                               disable_web_page_preview=True)
                        keyboard.add(f"{icon} {i.order_id} {icon_category}")
                    except:
                        await bot.send_message(callback.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"<b>Детали заказа</b>\n"
                                               f"{icon_category} "
                                               f"Категория - <b>{i.category_delivery}</b>\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                               f"{config.KEYBOARD.get('INFORMATION')} "
                                               f"Название - <b>{i.title}</b>\n"
                                               f"{config.KEYBOARD.get('CLIPBOARD')} "
                                               f"Описание - <b>{i.description}</b>\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} "
                                               f"Цена - <b>{i.price}</b>\n"
                                               f"{config.KEYBOARD.get('MONEY_BAG')} "
                                               f"Ценность вашего товара - <b>{i.order_worth}</b>\n"
                                               f"{config.KEYBOARD.get('WRENCH')} "
                                               f"В работе - <b>{bool(i.in_work)}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID заказа - <b>{i.order_id}</b>\n"
                                               f"{icon} "
                                               f"Исполнитель - <b>{p_status}</b>\n"
                                               f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                               f"Заказ создан: <b>{i.order_create}</b>\n"
                                               f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                               f"Действует до: <b>{i.order_expired}</b>\n"
                                               f"{config.KEYBOARD.get('BAR_CHART')} "
                                               f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}\n",
                                               disable_web_page_preview=True)
                        keyboard.add(f"{icon} {i.order_id} {icon_category}")
            keyboard.add("Вернуться в главное меню")
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
            CustomerDetailsTasks.register_customer_details_tasks(dp)

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
            months.append(datetime.strptime(i.order_end, '%d-%m-%Y, %H:%M:%S').month)
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
        if len(month) == 1:
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
            for i in res:
                try:
                    icon_category = None
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
                    await bot.send_photo(callback.from_user.id, i.photo)
                    await bot.send_message(callback.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{icon_category} "
                                           f"Категория - <b>{i.category_delivery}</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                           f"{config.KEYBOARD.get('INFORMATION')} "
                                           f"Название - <b>{i.title}</b>\n"
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
                                           f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                           f"Действует до: <b>{i.order_expired}</b>\n",
                                           disable_web_page_preview=True)
                    keyboard.add(f"{i.order_id}")
                    async with state.proxy() as data:
                        data[i.order_id] = {
                            'Откуда': i.geo_position_from,
                            'Куда': i.geo_position_to,
                            'Название': i.title,
                            'ID заказа': i.order_id,
                            'ID исполнителя': i.in_work,
                            'Бюджет': i.price,
                        }
                except:
                    try:
                        await bot.send_video(callback.from_user.id, i.video)
                        await bot.send_message(callback.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"<b>Детали заказа</b>\n"
                                               f"{icon_category} "
                                               f"Категория - <b>{i.category_delivery}</b>\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                               f"{config.KEYBOARD.get('INFORMATION')} "
                                               f"Название - <b>{i.title}</b>\n"
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
                                               f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                               f"Действует до: <b>{i.order_expired}</b>\n",
                                               disable_web_page_preview=True)
                        keyboard.add(f"{i.order_id}")
                        async with state.proxy() as data:
                            data[i.order_id] = {
                                'Откуда': i.geo_position_from,
                                'Куда': i.geo_position_to,
                                'Название': i.title,
                                'ID заказа': i.order_id,
                                'ID исполнителя': i.in_work,
                                'Бюджет': i.price,
                            }
                    except:
                        await bot.send_message(callback.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"<b>Детали заказа</b>\n"
                                               f"{icon_category} "
                                               f"Категория - <b>{i.category_delivery}</b>\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                               f"{config.KEYBOARD.get('INFORMATION')} "
                                               f"Название - <b>{i.title}</b>\n"
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
                                               f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                               f"Действует до: <b>{i.order_expired}</b>\n",
                                               disable_web_page_preview=True)
                        keyboard.add(f"{i.order_id}")
                        async with state.proxy() as data:
                            data[i.order_id] = {
                                'Откуда': i.geo_position_from,
                                'Куда': i.geo_position_to,
                                'Название': i.title,
                                'ID заказа': i.order_id,
                                'ID исполнителя': i.in_work,
                                'Бюджет': i.price,
                            }
            keyboard.add("Вернуться в главное меню")
            await bot.send_message(callback.from_user.id,
                                   "Выберите ID задачи чтобы войти в детали заказа",
                                   reply_markup=keyboard)
            await customer_states.CustomerHistory.enter_history.set()
            CustomerHistory.register_customer_history(dp)

    @staticmethod
    async def customer_approve(callback: types.CallbackQuery):
        res = callback.message.text.split()
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(res[-1],
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                               f"Заказчик <b>{callback.from_user.id}</b> одобрил ваш запрос по заказу <b>{res[2]}\n</b>"
                               f"Нажмите взять или откажитесь "
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}",
                               reply_markup=markup_customer.inline_approve())

    @staticmethod
    async def customer_decline(callback: types.CallbackQuery):
        res = callback.message.text.split()
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(res[-1],
                               f"{config.KEYBOARD.get('CROSS_MARK')} "
                               f"Заказчик <b>{callback.from_user.id}</b> не одобрил ваш запрос по заказу <b>{res[2]}</b>. "
                               f"Возможно ему не понравился ваш рейтинг "
                               f"{config.KEYBOARD.get('CROSS_MARK')}")

    @staticmethod
    async def proposal_from_performer_yes(callback: types.CallbackQuery):
        res = callback.message.text.split()
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(res[7],
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                               f"Заказчик <b>{callback.from_user.id}</b> "
                               f"одобрил ваше предложение о новой цене <b>{res[4]}</b>\n"
                               f"По заказу <b>{res[11]}</b>\n"
                               f"Нажмите взять или откажитесь"
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}",
                               reply_markup=markup_customer.inline_approve_proposal_with_new_price(res[4]))
        await bot.send_message(callback.from_user.id,
                               f"Вы отправили согласия о новой цене <b>{res[4]}</b>, "
                               f"для Исполнителя <b>{res[7]}</b> на ваш заказ <b>{res[11]}</b>")

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
    def register_customer_handler(dp: Dispatcher):
        dp.register_message_handler(CustomerMain.phone, content_types=['contact'],
                                    state=customer_states.CustomerPhone.phone)
        dp.register_callback_query_handler(CustomerMain.hi_customer, text='customer')
        dp.register_message_handler(CustomerMain.main, state=customer_states.CustomerStart.start)
        dp.register_message_handler(CustomerMain.customer_menu, state=customer_states.CustomerStart.customer_menu)
        dp.register_callback_query_handler(CustomerMain.customer_approve, state=["*"], text='customer_yes')
        dp.register_callback_query_handler(CustomerMain.customer_decline, state=["*"], text='customer_no')
        dp.register_callback_query_handler(CustomerMain.proposal_from_performer_yes, state=["*"], text='proposal_yes')
        dp.register_callback_query_handler(CustomerMain.proposal_from_performer_no, state=["*"], text='proposal_no')
        dp.register_callback_query_handler(CustomerMain.choose_month,
                                           state=customer_states.CustomerStart.customer_menu,
                                           text_contains='year_finish_')
        dp.register_callback_query_handler(CustomerMain.choose_day,
                                           state=customer_states.CustomerStart.customer_menu,
                                           text_contains='month_finish_')
        dp.register_callback_query_handler(CustomerMain.choose_job,
                                           state=customer_states.CustomerStart.customer_menu,
                                           text_contains='day_finish_')
        dp.register_callback_query_handler(CustomerMain.refresh,
                                           state=["*"], text='refresh')


class CustomerProfile:
    @staticmethod
    async def customer_profile(message: types.Message):
        if "Главное меню" in message.text:
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_customer.main_menu(),
                                   )
        if "Статистика по заказам" in message.text:
            count_orders = await customers_get.customer_count_orders(message.from_user.id)
            awaiting = int(count_orders[0]) - int(count_orders[3]) - int(count_orders[1]) - int(count_orders[2])
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} Всего заказов - <b>{count_orders[0]}</b>\n"
                                   f"{config.KEYBOARD.get('WRENCH')} В работе - <b>{count_orders[1]}</b>\n"
                                   f"{config.KEYBOARD.get('WRENCH')} "
                                   f"В ожидании - <b>{awaiting}</b>\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} Завершенных - "
                                   f"<b>{count_orders[2]}</b>\n"
                                   f"{config.KEYBOARD.get('CROSS_MARK')} Отмененных - "
                                   f"<b>{count_orders[3]}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}"
                                   )

    @staticmethod
    def register_customer_profile(dp):
        dp.register_message_handler(CustomerProfile.customer_profile,
                                    state=customer_states.CustomerProfile.my_profile)


class CustomerCreateTask:
    @staticmethod
    async def create_task(message: types.Message):
        if "С телефона" in message.text:
            await bot.send_message(message.from_user.id,
                                   "Выберите категорию доставки",
                                   reply_markup=markup_customer.category_delivery())
            await customer_states.CustomerCreateTask.next()
        if "С компьютера" in message.text:
            await bot.send_message(message.from_user.id,
                                   "Выберите категорию доставки",
                                   reply_markup=markup_customer.category_delivery())
            await customer_states.CustomerCreateTaskComp.category_delivery.set()
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    async def category_delivery(message: types.Message, state: FSMContext):
        category = [f"{KEYBOARD.get('BOUQUET')} Цветы",
                    f"{KEYBOARD.get('WRAPPED_GIFT')} Подарки",
                    f"{KEYBOARD.get('SHORTCAKE')} Кондитерка",
                    f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')} Документы",
                    f"{KEYBOARD.get('ARROWS_BUTTON')} Погрузка/Разгрузка",
                    f"{KEYBOARD.get('INPUT_LATIN_LETTERS')} Другое"]
        if message.text in category:
            await bot.send_message(message.from_user.id,
                                   f"Отлично! Вы выбрали категорию {message.text}")
            async with state.proxy() as data:
                data["category_delivery"] = message.text.split()[1]
            await bot.send_message(message.from_user.id,
                                   "Откуда забрать посылку ?\n"
                                   "Вы можете отправить своё местоположение\n"
                                   "Или отправить любое другое местоположение отправив геопозицию\n"
                                   "Нажмите на скрепку и далее найдите раздел Геопозиция\n"
                                   "На карте вы можете отправить точку откуда забрать посылку",
                                   reply_markup=markup_customer.send_my_geo())
            await customer_states.CustomerCreateTask.next()
        if message.text in f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    async def geo_position_from(message: types.Message, state: FSMContext):
        try:
            n = Nominatim(user_agent='User')
            loc = f"{message.location.latitude}, {message.location.longitude}"
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
                                   reply_markup=markup_customer.inline_approve_geo_from())
            async with state.proxy() as data:
                data["geo_data_from"] = f'{city}, ' \
                                        f'{address.raw.get("address").get("road")}, ' \
                                        f'{address.raw.get("address").get("house_number")}'
        except AttributeError:
            pass
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    async def approve_geo_from(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Теперь надо указать конечную точку доставки",
                               reply_markup=markup_customer.send_my_geo())
        await customer_states.CustomerCreateTask.geo_position_to.set()

    @staticmethod
    async def geo_position_to(message: types.Message, state: FSMContext):
        try:
            n = Nominatim(user_agent='User')
            loc = f"{message.location.latitude}, {message.location.longitude}"
            address = n.reverse(loc)
            city = address.raw.get("address").get("city")
            if city is None:
                city = address.raw.get("address").get("town")
            await bot.send_message(message.from_user.id,
                                   f'Город доставки: {city}\n'
                                   f'Адрес доставки: {address.raw.get("address").get("road")}, '
                                   f'{address.raw.get("address").get("house_number")}\n')
            await bot.send_message(message.from_user.id,
                                   "Проверьте пожалуйста координаты, если вы ошиблись "
                                   "вы можете еще раз отправить геопозицию. "
                                   "Если же все в порядке нажмите Все верно",
                                   reply_markup=markup_customer.inline_approve_geo_to())
            async with state.proxy() as data:
                data["geo_data_to"] = f'{city}, ' \
                                      f'{address.raw.get("address").get("road")}, ' \
                                      f'{address.raw.get("address").get("house_number")}'
        except AttributeError:
            pass
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    async def approve_geo_to(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Отлично! Введите название заказа",
                               reply_markup=markup_customer.cancel())
        await customer_states.CustomerCreateTask.title.set()

    @staticmethod
    async def title(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        else:
            if len(message.text) > 100:
                await bot.send_message(message.from_user.id,
                                       "Вы ввели слишком длинное название!"
                                       "Ограничение в названии заказа 100 символов!",
                                       reply_markup=markup_customer.cancel())
            else:
                async with state.proxy() as data:
                    data["title"] = message.text
                await customer_states.CustomerCreateTask.next()
                await bot.send_message(message.from_user.id,
                                       "Введите, что нужно сделать",
                                       reply_markup=markup_customer.cancel())

    @staticmethod
    async def description(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        else:
            if len(message.text) > 255:
                await bot.send_message(message.from_user.id,
                                       "Вы ввели слишком длинное название!"
                                       "Ограничение в названии заказа 255 символов!",
                                       reply_markup=markup_customer.cancel())
            else:
                async with state.proxy() as data:
                    data["description"] = message.text
                await customer_states.CustomerCreateTask.next()
                await bot.send_message(message.from_user.id,
                                       "Предложите цену исполнителю",
                                       reply_markup=markup_customer.cancel())

    @staticmethod
    async def price(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        if message.text.isdigit():
            async with state.proxy() as data:
                data["price"] = message.text
            await bot.send_message(message.from_user.id,
                                   "Выберите категорию Исполнителя",
                                   reply_markup=markup_customer.performer_category())
            await customer_states.CustomerCreateTask.next()
        elif message.text != f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await bot.send_message(message.from_user.id,
                                   "Надо ввести целое число")

    @staticmethod
    async def performer_category(message: types.Message, state: FSMContext):
        if "На машине" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "car"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.expired_data())
            await customer_states.CustomerCreateTask.next()
        if "На скутере" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "scooter"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.expired_data())
            await customer_states.CustomerCreateTask.next()
        if "Пешеход" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "pedestrian"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.expired_data())
            await customer_states.CustomerCreateTask.next()
        if "Любой" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "any"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.expired_data())
            await customer_states.CustomerCreateTask.next()

    @staticmethod
    async def expired_order(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        if message.text.isdigit():
            if 1 <= int(message.text) <= 12:
                await bot.send_message(message.from_user.id,
                                       f"Ваш заказ действует <b>{message.text} часа</b>")
                date = datetime.now() + timedelta(hours=int(message.text))
                async with state.proxy() as data:
                    data['order_expired'] = date
                await bot.send_message(message.from_user.id,
                                       "<b>Определите примерную ценность вашего товара</b>\n"
                                       "<b>Если ценности нет напишите 0</b>\n"
                                       "<b>(Допустим у вас категория 'Погрузка/Разгрузка)'</b>)",
                                       reply_markup=markup_customer.cancel())
                await customer_states.CustomerCreateTask.next()
            else:
                await bot.send_message(message.from_user.id,
                                       f"Введите от 1 до 12 часов")
        else:
            await bot.send_message(message.from_user.id,
                                   "Нужно ввести цифру\n"
                                   "Введите сколько часов действует ваш заказ")

    @staticmethod
    async def order_worth(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        if message.text.isdigit() and int(message.text) < 15001:
            await bot.send_message(message.from_user.id,
                                   f"Вы определили ценность вашего товара <b>{message.text} руб.</b>")
            async with state.proxy() as data:
                data['order_worth'] = message.text
            await bot.send_message(message.from_user.id,
                                   "Загрузите фото или видео",
                                   reply_markup=markup_customer.photo_or_video_create_task())
            await customer_states.CustomerCreateTask.next()
        elif not message.text.isdigit():
            await bot.send_message(message.from_user.id,
                                   "Нужно ввести цифру\n"
                                   "Определите примерную ценность вашего товара")
        else:
            await bot.send_message(message.from_user.id,
                                   "Максимальная ценность товара в 15000 рублей\n"
                                   "Определите примерную ценность вашего товара")

    @staticmethod
    async def photo_video(message: types.Message, state: FSMContext):
        order_id = f"{datetime.now().strftime('%m_%d')}_{randint(1, 99999)}"
        async with state.proxy() as data:
            data["order_id"] = order_id
        if message.text == "Без фото или видео":
            async with state.proxy() as data:
                await customers_set.customer_add_order(message.from_user.id,
                                                       data.get("geo_data_from"),
                                                       data.get("geo_data_to"),
                                                       data.get("title"),
                                                       int(data.get("price")),
                                                       data.get("description"),
                                                       "No Photo", "No Video",
                                                       order_id,
                                                       datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                       data.get("category_delivery"),
                                                       data.get("performer_category"),
                                                       data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                       int(data.get("order_worth")))
            await general_set.add_review(order_id)
            await state.finish()
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "<b>Отклик без фото или видео отправлен.</b>\n"
                                   "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>",
                                   reply_markup=markup_customer.back_main_menu())
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        if message.text == "Загрузить Фото":
            await customer_states.CustomerCreateTask.photo.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Загрузите фото",
                                   reply_markup=markup_customer.cancel())
        if message.text == "Загрузить Видео":
            await customer_states.CustomerCreateTask.video.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Загрузите видео",
                                   reply_markup=markup_customer.cancel())

    @staticmethod
    async def photo(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        else:
            try:
                async with state.proxy() as data:
                    data["photo"] = message.photo[2].file_id
                await customers_set.customer_add_order(message.from_user.id,
                                                       data.get("geo_data_from"),
                                                       data.get("geo_data_to"),
                                                       data.get("title"),
                                                       int(data.get("price")),
                                                       data.get("description"),
                                                       data.get("photo"), "No Video",
                                                       data.get("order_id"),
                                                       datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                       data.get("category_delivery"),
                                                       data.get("performer_category"),
                                                       data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                       int(data.get("order_worth")))
                await general_set.add_review(data.get("order_id"))
                await state.finish()
                await customer_states.CustomerStart.start.set()
                await bot.send_message(message.from_user.id,
                                       "<b>Отклик с фото отправлен.</b>\n"
                                       "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>",
                                       reply_markup=markup_customer.back_main_menu())
            except IndexError:
                pass

    @staticmethod
    async def video(message: types.Message, state: FSMContext):
        if message.text == "Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        else:
            async with state.proxy() as data:
                data["video"] = message.video.file_id
            await customers_set.customer_add_order(message.from_user.id,
                                                   data.get("geo_data_from"),
                                                   data.get("geo_data_to"),
                                                   data.get("title"),
                                                   int(data.get("price")),
                                                   data.get("description"),
                                                   "No Photo", data.get("video"),
                                                   data.get("order_id"),
                                                   datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                   data.get("category_delivery"),
                                                   data.get("performer_category"),
                                                   data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                   int(data.get("order_worth")))
            await general_set.add_review(data.get("order_id"))
            await state.finish()
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "<b>Отклик с видео отправлен.</b>\n"
                                   "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    def register_customer_create_task(dp: Dispatcher):
        dp.register_message_handler(CustomerCreateTask.create_task,
                                    state=customer_states.CustomerCreateTask.create)
        dp.register_message_handler(CustomerCreateTask.category_delivery,
                                    state=customer_states.CustomerCreateTask.category_delivery)
        dp.register_message_handler(CustomerCreateTask.geo_position_from,
                                    content_types=['location', 'text'],
                                    state=customer_states.CustomerCreateTask.geo_position_from)
        dp.register_callback_query_handler(CustomerCreateTask.approve_geo_from,
                                           text="approve_geo_from",
                                           state=customer_states.CustomerCreateTask.geo_position_from)
        dp.register_message_handler(CustomerCreateTask.geo_position_to,
                                    content_types=['location', 'text'],
                                    state=customer_states.CustomerCreateTask.geo_position_to)
        dp.register_callback_query_handler(CustomerCreateTask.approve_geo_to,
                                           text="approve_geo_to",
                                           state=customer_states.CustomerCreateTask.geo_position_to)
        dp.register_message_handler(CustomerCreateTask.title,
                                    state=customer_states.CustomerCreateTask.title)
        dp.register_message_handler(CustomerCreateTask.description,
                                    state=customer_states.CustomerCreateTask.description)
        dp.register_message_handler(CustomerCreateTask.price,
                                    state=customer_states.CustomerCreateTask.price)
        dp.register_message_handler(CustomerCreateTask.performer_category,
                                    state=customer_states.CustomerCreateTask.performer_category)
        dp.register_message_handler(CustomerCreateTask.photo_video,
                                    state=customer_states.CustomerCreateTask.photo_or_video)
        dp.register_message_handler(CustomerCreateTask.photo, content_types=['photo', 'text'],
                                    state=customer_states.CustomerCreateTask.photo)
        dp.register_message_handler(CustomerCreateTask.video, content_types=['video', 'text'],
                                    state=customer_states.CustomerCreateTask.video)
        dp.register_message_handler(CustomerCreateTask.expired_order,
                                    state=customer_states.CustomerCreateTask.expired_data)
        dp.register_message_handler(CustomerCreateTask.order_worth,
                                    state=customer_states.CustomerCreateTask.worth)


class CustomerCreateTaskComp:

    @staticmethod
    async def category_delivery_comp(message: types.Message, state: FSMContext):
        category = [f"{KEYBOARD.get('BOUQUET')} Цветы",
                    f"{KEYBOARD.get('WRAPPED_GIFT')} Подарки",
                    f"{KEYBOARD.get('SHORTCAKE')} Кондитерка",
                    f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')} Документы",
                    f"{KEYBOARD.get('ARROWS_BUTTON')} Погрузка/Разгрузка",
                    f"{KEYBOARD.get('INPUT_LATIN_LETTERS')} Другое"]
        if message.text in category:
            await bot.send_message(message.from_user.id,
                                   f"Отлично! Вы выбрали категорию {message.text}")
            async with state.proxy() as data:
                data["category_delivery"] = message.text.split()[1]
            await bot.send_message(message.from_user.id,
                                   "Выберите способ",
                                   reply_markup=markup_customer.choose())
            await customer_states.CustomerCreateTaskComp.next()
        if message.text in f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    async def choose(message: types.Message):
        if "Ввести координаты с карт" in message.text:
            await bot.send_message(message.from_user.id,
                                   "Введите координаты откуда забрать",
                                   reply_markup=markup_customer.open_site())
            await customer_states.CustomerCreateTaskComp.geo_position_from.set()
        if "Ввести адрес вручную" in message.text:
            await bot.send_message(message.from_user.id,
                                   "Введите адрес в таком формате:\n"
                                   "Город улица дом\n"
                                   "Пример:\n"
                                   "Москва Лобачевского 12",
                                   reply_markup=markup_customer.cancel())
            await customer_states.CustomerCreateTaskComp.geo_position_from_custom.set()
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    async def geo_position_from_custom(message: types.Message, state: FSMContext):
        if message.text != f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await bot.send_message(message.from_user.id,
                                   f'Город подачи: {message.text.split()[0]}\n'
                                   f'Адрес подачи: {message.text.split()[1]} - {message.text.split()[2]}')
            await bot.send_message(message.from_user.id,
                                   "Проверьте пожалуйста введенные данные, если вы ошиблись "
                                   "вы можете еще раз отправить адрес.\n"
                                   "Если же все в порядке нажмите Все верно",
                                   reply_markup=markup_customer.inline_approve_geo_from_custom())
            async with state.proxy() as data:
                data["geo_data_from_comp"] = message.text
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    async def approve_geo_from_custom(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Введите адрес конечной точки\n"
                               "Если у вас Разгрузка/Погрузка, введите тот же адрес",
                               reply_markup=markup_customer.cancel())
        await customer_states.CustomerCreateTaskComp.geo_position_to_custom.set()

    @staticmethod
    async def geo_position_to_custom(message: types.Message, state: FSMContext):
        if message.text != f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await bot.send_message(message.from_user.id,
                                   f'Город подачи: {message.text.split()[0]}\n'
                                   f'Адрес подачи: {message.text.split()[1]} - {message.text.split()[2]}')
            await bot.send_message(message.from_user.id,
                                   "Проверьте пожалуйста введенные данные, если вы ошиблись "
                                   "вы можете еще раз отправить адрес.\n"
                                   "Если же все в порядке нажмите Все верно",
                                   reply_markup=markup_customer.inline_approve_geo_to_custom())
            async with state.proxy() as data:
                data["geo_data_to_comp"] = message.text
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    async def approve_geo_to_custom(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Отлично! Введите название заказа",
                               reply_markup=markup_customer.cancel())
        await customer_states.CustomerCreateTaskComp.title.set()

    @staticmethod
    async def geo_position_from_comp(message: types.Message, state: FSMContext):
        if message.text != f"{KEYBOARD.get('CROSS_MARK')} Отмена":
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
                                       reply_markup=markup_customer.inline_approve_geo_from_comp())
                async with state.proxy() as data:
                    data["geo_data_from_comp"] = f'{city}, ' \
                                                 f'{address.raw.get("address").get("road")}, ' \
                                                 f'{address.raw.get("address").get("house_number")}'
            except AttributeError:
                pass
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    async def approve_geo_from_comp(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Введите координаты конечной точки",
                               reply_markup=markup_customer.open_site())
        await customer_states.CustomerCreateTaskComp.geo_position_to.set()

    @staticmethod
    async def geo_position_to_comp(message: types.Message, state: FSMContext):
        if message.text != f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            try:
                n = Nominatim(user_agent='User')
                loc = f"{message.text}"
                address = n.reverse(loc)
                city = address.raw.get("address").get("city")
                if city is None:
                    city = address.raw.get("address").get("town")
                await bot.send_message(message.from_user.id,
                                       f'Город доставки: {city}\n'
                                       f'Адрес доставки: {address.raw.get("address").get("road")}, '
                                       f'{address.raw.get("address").get("house_number")}\n')
                await bot.send_message(message.from_user.id,
                                       "Проверьте пожалуйста координаты, если вы ошиблись "
                                       "вы можете еще раз отправить геопозицию. "
                                       "Если же все в порядке нажмите Все верно",
                                       reply_markup=markup_customer.inline_approve_geo_to_comp())
                async with state.proxy() as data:
                    data["geo_data_to_comp"] = f'{city}, ' \
                                          f'{address.raw.get("address").get("road")}, ' \
                                          f'{address.raw.get("address").get("house_number")}'
            except AttributeError:
                pass
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    async def approve_geo_to_comp(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Отлично! Введите название заказа",
                               reply_markup=markup_customer.cancel())
        await customer_states.CustomerCreateTaskComp.title.set()

    @staticmethod
    async def title_comp(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        else:
            if len(message.text) > 100:
                await bot.send_message(message.from_user.id,
                                       "Вы ввели слишком длинное название!"
                                       "Ограничение в названии заказа 100 символов!",
                                       reply_markup=markup_customer.cancel())
            else:
                async with state.proxy() as data:
                    data["title"] = message.text
                await customer_states.CustomerCreateTaskComp.next()
                await bot.send_message(message.from_user.id,
                                       "Введите, что нужно сделать",
                                       reply_markup=markup_customer.cancel())

    @staticmethod
    async def description_comp(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        else:
            if len(message.text) > 255:
                await bot.send_message(message.from_user.id,
                                       "Вы ввели слишком длинное название!"
                                       "Ограничение в названии заказа 255 символов!",
                                       reply_markup=markup_customer.cancel())
            else:
                async with state.proxy() as data:
                    data["description"] = message.text
                await customer_states.CustomerCreateTaskComp.next()
                await bot.send_message(message.from_user.id,
                                       "Предложите цену исполнителю",
                                       reply_markup=markup_customer.cancel())

    @staticmethod
    async def price_comp(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        if message.text.isdigit():
            async with state.proxy() as data:
                data["price"] = message.text
            await bot.send_message(message.from_user.id,
                                   "Выберите категорию Исполнителя",
                                   reply_markup=markup_customer.performer_category())
            await customer_states.CustomerCreateTaskComp.next()
        elif message.text != f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await bot.send_message(message.from_user.id,
                                   "Надо ввести целое число")

    @staticmethod
    async def performer_category_comp(message: types.Message, state: FSMContext):
        if "На машине" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "car"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.expired_data())
            await customer_states.CustomerCreateTaskComp.next()
        if "На скутере" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "scooter"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.expired_data())
            await customer_states.CustomerCreateTaskComp.next()
        if "Пешеход" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "pedestrian"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.expired_data())
            await customer_states.CustomerCreateTaskComp.next()
        if "Любой" in message.text:
            async with state.proxy() as data:
                data['performer_category'] = "any"
            await bot.send_message(message.from_user.id,
                                   "<b>Сколько часов максимум актуален ваш заказ ?</b>",
                                   reply_markup=markup_customer.expired_data())
            await customer_states.CustomerCreateTaskComp.next()

    @staticmethod
    async def expired_order_comp(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        if message.text.isdigit():
            if 1 <= int(message.text) <= 12:
                await bot.send_message(message.from_user.id,
                                       f"Ваш заказ действует <b>{message.text} часа</b>")
                date = datetime.now() + timedelta(hours=int(message.text))
                async with state.proxy() as data:
                    data['order_expired'] = date
                await bot.send_message(message.from_user.id,
                                       "<b>Определите примерную ценность вашего товара</b>\n"
                                       "<b>Если ценности нет напишите 0</b>\n"
                                       "<b>(Допустим у вас категория 'Погрузка/Разгрузка)'</b>)",
                                       reply_markup=markup_customer.cancel())
                await customer_states.CustomerCreateTaskComp.next()
            else:
                await bot.send_message(message.from_user.id,
                                       f"Введите от 1 до 12 часов")
        else:
            await bot.send_message(message.from_user.id,
                                   "Нужно ввести цифру\n"
                                   "Введите сколько часов действует ваш заказ")

    @staticmethod
    async def order_worth_comp(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        if message.text.isdigit() and int(message.text) < 15001:
            await bot.send_message(message.from_user.id,
                                   f"Вы определили ценность вашего товара <b>{message.text} руб.</b>")
            async with state.proxy() as data:
                data['order_worth'] = message.text
            await bot.send_message(message.from_user.id,
                                   "Загрузите фото или видео",
                                   reply_markup=markup_customer.photo_or_video_create_task())
            await customer_states.CustomerCreateTaskComp.next()
        elif not message.text.isdigit():
            await bot.send_message(message.from_user.id,
                                   "Нужно ввести цифру\n"
                                   "Определите примерную ценность вашего товара")
        else:
            await bot.send_message(message.from_user.id,
                                   "Максимальная ценность товара в 15000 рублей\n"
                                   "Определите примерную ценность вашего товара")

    @staticmethod
    async def photo_video_comp(message: types.Message, state: FSMContext):
        order_id = f"{datetime.now().strftime('%m_%d')}_{randint(1, 99999)}"
        async with state.proxy() as data:
            data["order_id"] = order_id
        if message.text == "Без фото или видео":
            async with state.proxy() as data:
                await customers_set.customer_add_order(message.from_user.id,
                                                       data.get("geo_data_from_comp"),
                                                       data.get("geo_data_to_comp"),
                                                       data.get("title"),
                                                       int(data.get("price")),
                                                       data.get("description"),
                                                       "No Photo", "No Video",
                                                       order_id,
                                                       datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                       data.get("category_delivery"),
                                                       data.get("performer_category"),
                                                       data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                       int(data.get("order_worth")))
            await general_set.add_review(order_id)
            await state.finish()
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "<b>Отклик без фото или видео отправлен.</b>\n"
                                   "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>",
                                   reply_markup=markup_customer.back_main_menu())
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        if message.text == "Загрузить Фото":
            await customer_states.CustomerCreateTaskComp.photo.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Загрузите фото",
                                   reply_markup=markup_customer.cancel())
        if message.text == "Загрузить Видео":
            await customer_states.CustomerCreateTaskComp.video.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Загрузите видео",
                                   reply_markup=markup_customer.cancel())

    @staticmethod
    async def photo_comp(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('CROSS_MARK')} Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        else:
            try:
                async with state.proxy() as data:
                    data["photo"] = message.photo[2].file_id
                await customers_set.customer_add_order(message.from_user.id,
                                                       data.get("geo_data_from_comp"),
                                                       data.get("geo_data_to_comp"),
                                                       data.get("title"),
                                                       int(data.get("price")),
                                                       data.get("description"),
                                                       data.get("photo"), "No Video",
                                                       data.get("order_id"),
                                                       datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                       data.get("category_delivery"),
                                                       data.get("performer_category"),
                                                       data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                       int(data.get("order_worth")))
                await general_set.add_review(data.get("order_id"))
                await state.finish()
                await customer_states.CustomerStart.start.set()
                await bot.send_message(message.from_user.id,
                                       "<b>Отклик с фото отправлен.</b>\n"
                                       "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>",
                                       reply_markup=markup_customer.back_main_menu())
            except IndexError:
                pass

    @staticmethod
    async def video_comp(message: types.Message, state: FSMContext):
        if message.text == "Отмена":
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "Вы отменили создание заказа",
                                   reply_markup=markup_customer.back_main_menu())
        else:
            async with state.proxy() as data:
                data["video"] = message.video.file_id
            await customers_set.customer_add_order(message.from_user.id,
                                                   data.get("geo_data_from_comp"),
                                                   data.get("geo_data_to_comp"),
                                                   data.get("title"),
                                                   int(data.get("price")),
                                                   data.get("description"),
                                                   "No Photo", data.get("video"),
                                                   data.get("order_id"),
                                                   datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                   data.get("category_delivery"),
                                                   data.get("performer_category"),
                                                   data.get("order_expired").strftime('%d-%m-%Y, %H:%M:%S'),
                                                   int(data.get("order_worth")))
            await general_set.add_review(data.get("order_id"))
            await state.finish()
            await customer_states.CustomerStart.start.set()
            await bot.send_message(message.from_user.id,
                                   "<b>Отклик с видео отправлен.</b>\n"
                                   "<b>Ожидайте пока Исполнитель примет ваш заказ!</b>",
                                   reply_markup=markup_customer.back_main_menu())

    @staticmethod
    def register_customer_create_task_comp(dp: Dispatcher):
        dp.register_message_handler(CustomerCreateTaskComp.category_delivery_comp,
                                    state=customer_states.CustomerCreateTaskComp.category_delivery)
        dp.register_message_handler(CustomerCreateTaskComp.geo_position_from_comp,
                                    state=customer_states.CustomerCreateTaskComp.geo_position_from)
        dp.register_callback_query_handler(CustomerCreateTaskComp.approve_geo_from_comp,
                                           text="approve_geo_from_comp",
                                           state=customer_states.CustomerCreateTaskComp.geo_position_from)
        dp.register_message_handler(CustomerCreateTaskComp.geo_position_to_comp,
                                    state=customer_states.CustomerCreateTaskComp.geo_position_to)
        dp.register_callback_query_handler(CustomerCreateTaskComp.approve_geo_to_comp,
                                           text="approve_geo_to_comp",
                                           state=customer_states.CustomerCreateTaskComp.geo_position_to)
        dp.register_message_handler(CustomerCreateTaskComp.title_comp,
                                    state=customer_states.CustomerCreateTaskComp.title)
        dp.register_message_handler(CustomerCreateTaskComp.description_comp,
                                    state=customer_states.CustomerCreateTaskComp.description)
        dp.register_message_handler(CustomerCreateTaskComp.price_comp,
                                    state=customer_states.CustomerCreateTaskComp.price)
        dp.register_message_handler(CustomerCreateTaskComp.performer_category_comp,
                                    state=customer_states.CustomerCreateTaskComp.performer_category)
        dp.register_message_handler(CustomerCreateTaskComp.photo_video_comp,
                                    state=customer_states.CustomerCreateTaskComp.photo_or_video)
        dp.register_message_handler(CustomerCreateTaskComp.photo_comp, content_types=['photo', 'text'],
                                    state=customer_states.CustomerCreateTaskComp.photo)
        dp.register_message_handler(CustomerCreateTaskComp.video_comp, content_types=['video', 'text'],
                                    state=customer_states.CustomerCreateTaskComp.video)
        dp.register_message_handler(CustomerCreateTaskComp.expired_order_comp,
                                    state=customer_states.CustomerCreateTaskComp.expired_data)
        dp.register_message_handler(CustomerCreateTaskComp.order_worth_comp,
                                    state=customer_states.CustomerCreateTaskComp.worth)
        dp.register_message_handler(CustomerCreateTaskComp.choose,
                                    state=customer_states.CustomerCreateTaskComp.choose)
        dp.register_message_handler(CustomerCreateTaskComp.geo_position_from_custom,
                                    state=customer_states.CustomerCreateTaskComp.geo_position_from_custom)
        dp.register_callback_query_handler(CustomerCreateTaskComp.approve_geo_from_custom,
                                           text="approve_geo_from_custom",
                                           state=customer_states.CustomerCreateTaskComp.geo_position_from_custom)
        dp.register_message_handler(CustomerCreateTaskComp.geo_position_to_custom,
                                    state=customer_states.CustomerCreateTaskComp.geo_position_to_custom)
        dp.register_callback_query_handler(CustomerCreateTaskComp.approve_geo_to_comp,
                                           text="approve_geo_to_custom",
                                           state=customer_states.CustomerCreateTaskComp.geo_position_to_custom)


class CustomerDetailsTasks:
    @staticmethod
    async def customer_details(message: types.Message, state: FSMContext):
        if "Вернуться в главное меню" in message.text:
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_customer.main_menu())
        else:
            res = await customers_get.customer_all_orders(message.from_user.id)
            in_work = None
            try:
                async with state.proxy() as data:
                    msg = message.text.split()[1]
                    data["order_id"] = msg
                in_work = await customers_get.customer_in_work_order(data.get("order_id"))
                async with state.proxy() as data:
                    data["user_id"] = in_work
            except:
                pass
            if in_work:
                for i in res:
                    if i.order_id == msg:
                        await customer_states.CustomerDetailsTasks.enter_task.set()
                        await bot.send_message(message.from_user.id,
                                               "Вы вошли в детали этого заказа",
                                               reply_markup=markup_customer.details_task())
            elif in_work is None:
                await bot.send_message(message.from_user.id,
                                       "Откройте клавиатуру и нажмите на ID вашего заказа")
            else:
                for i in res:
                    if i.order_id == msg:
                        await customer_states.CustomerDetailsTasks.not_at_work.set()
                        await bot.send_message(message.from_user.id,
                                               "Ваш Заказ еще не взяли, но его можно отредактировать или отменить",
                                               reply_markup=markup_customer.details_task_not_at_work())

    @staticmethod
    async def detail_task(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            res_performer = await performers_get.performer_select(data.get("user_id"))
            res_order = await general_get.order_select(data.get("order_id"))
        if "Написать/Позвонить исполнителю" in message.text:
            res = await customers_get.customer_get_status_order(data.get("order_id"))
            if res is None:
                await customer_states.CustomerStart.customer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись в главное меню",
                                       reply_markup=markup_customer.main_menu())
            else:
                await bot.send_message(message.from_user.id,
                                       f"Вот его номер телефона {res_performer.telephone}\n"
                                       f"Или напишите ему в телеграм @{res_performer.username}")
        if "Детали заказа" in message.text:
            res = await customers_get.customer_get_status_order(data.get("order_id"))
            if res is None:
                await customer_states.CustomerStart.customer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись в главное меню",
                                       reply_markup=markup_customer.main_menu())
            else:
                try:
                    await bot.send_photo(message.from_user.id, res_order.photo)
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                           f"Категория - <b>{res_order.category_delivery}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <b>{res_order.order_id}</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(res_order.geo_position_from.split())}'>{res_order.geo_position_from}</a>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(res_order.geo_position_to.split())}'>{res_order.geo_position_to}</a>\n"
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
                except:
                    try:
                        await bot.send_video(message.from_user.id, res_order.video)
                        await bot.send_message(message.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"<b>Детали заказа</b>\n"
                                               f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                               f"Категория - <b>{res_order.category_delivery}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID заказа - <b>{res_order.order_id}</b>\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(res_order.geo_position_from.split())}'>{res_order.geo_position_from}</a>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(res_order.geo_position_to.split())}'>{res_order.geo_position_to}</a>\n"
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
                    except:
                        await bot.send_message(message.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"<b>Детали заказа</b>\n"
                                               f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                               f"Категория - <b>{res_order.category_delivery}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID заказа - <b>{res_order.order_id}</b>\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(res_order.geo_position_from.split())}'>{res_order.geo_position_from}</a>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(res_order.geo_position_to.split())}'>{res_order.geo_position_to}</a>\n"
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
                await customer_states.CustomerStart.customer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись в главное меню",
                                       reply_markup=markup_customer.main_menu())
            else:
                await bot.send_message(message.from_user.id,
                                       "Вы вошли в статус заказа, тут вы можете отменить заказ, "
                                       "Завершить заказ или проверить статус заказа для его закрытия",
                                       reply_markup=markup_customer.details_task_status())
                await customer_states.CustomerDetailsTasksStatus.enter_status.set()
                CustomerDetailsTasksStatus.register_customer_details_tasks_status(dp)
        if "Профиль исполнителя" in message.text:
            res = await customers_get.customer_get_status_order(data.get("order_id"))
            if res is None:
                await customer_states.CustomerStart.customer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись в главное меню",
                                       reply_markup=markup_customer.main_menu())
            else:
                await bot.send_message(message.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"Профиль <b>Исполнителя</b>:\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID : <b>{res_performer.user_id}</b>\n"
                                       f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                       f"Никнейм <b>@{res_performer.username}</b>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Номер <b>{res_performer.telephone}</b>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Имя <b>{res_performer.first_name}</b>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Фамилия <b>{res_performer.last_name}</b>\n"
                                       f"{config.KEYBOARD.get('BAR_CHART')} "
                                       f"Рейтинг <b>{str(res_performer.performer_rating)[0:5]}</b>\n"
                                       f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                       f"Заказов взял - <b>{res_performer.get_orders}</b>\n"
                                       f"{config.KEYBOARD.get('CROSS_MARK')} "
                                       f"Заказов отменил - <b>{res_performer.canceled_orders}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}",
                                       )
        if "Вернуться в главное меню" in message.text:
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_customer.main_menu())

    @staticmethod
    async def detail_task_not_at_work(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            res = await general_get.order_select(data.get("order_id"))
        if "Отменить заказ" in message.text:
            if res.in_work == 0:
                await bot.send_message(message.from_user.id,
                                       "Вы хотите отменить заказ ?",
                                       reply_markup=markup_customer.inline_cancel_task())
            else:
                await customer_states.CustomerStart.customer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Ваш заказ уже взяли!",
                                       reply_markup=markup_customer.main_menu())
        if "Редактировать заказ" in message.text:
            if res.in_work == 0:
                CustomerDetailsTasksChange.register_customer_details_tasks_change(dp)
                await bot.send_message(message.from_user.id,
                                       "Вы хотите редактировать заказ ?\n"
                                       "<b>Ваш заказ будет заблокирован до тех "
                                       "пор пока вы не закончите редактировать заказ!</b>",
                                       reply_markup=markup_customer.inline_change_task())
            else:
                await customer_states.CustomerStart.customer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Ваш заказ уже взяли!",
                                       reply_markup=markup_customer.main_menu())
        if "Вернуться в главное меню" in message.text:
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_customer.main_menu())

    @staticmethod
    async def cancel_order_not_at_work(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            await customers_set.customer_cancel_order(data.get("order_id"),
                                                      datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await customer_states.CustomerStart.customer_menu.set()
        await bot.send_message(callback.from_user.id,
                               "Вы отменили заказ!",
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
        await customer_states.CustomerDetailsTasks.not_at_work.set()
        await bot.send_message(callback.from_user.id,
                               "Ваш Заказ еще не взяли, но его можно отредактировать или отменить",
                               reply_markup=markup_customer.details_task_not_at_work())

    @staticmethod
    def register_customer_details_tasks(dp):
        dp.register_message_handler(CustomerDetailsTasks.customer_details,
                                    state=customer_states.CustomerDetailsTasks.my_tasks)
        dp.register_message_handler(CustomerDetailsTasks.detail_task,
                                    state=customer_states.CustomerDetailsTasks.enter_task)
        dp.register_message_handler(CustomerDetailsTasks.detail_task_not_at_work,
                                    state=customer_states.CustomerDetailsTasks.not_at_work)
        dp.register_callback_query_handler(CustomerDetailsTasks.cancel_order_not_at_work,
                                           text='cancel',
                                           state=customer_states.CustomerDetailsTasks.not_at_work)
        dp.register_callback_query_handler(CustomerDetailsTasks.no_cancel_order_not_at_work,
                                           text='no_cancel',
                                           state=customer_states.CustomerDetailsTasks.not_at_work)
        dp.register_callback_query_handler(CustomerDetailsTasks.no_change_order_not_at_work,
                                           text='no_change',
                                           state=customer_states.CustomerDetailsTasks.not_at_work)


class CustomerDetailsTasksChange:
    @staticmethod
    async def change_task_enter(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            await customers_set.customer_set_block_order(data.get("order_id"), 1)
        await bot.send_message(callback.from_user.id,
                               "<b>Ваш заказ временно заблокирован!</b>\n"
                               "Что будем менять ?",
                               reply_markup=markup_customer.details_task_change())
        await customer_states.CustomerChangeOrder.enter.set()

    @staticmethod
    async def change_task_main(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order_id = data.get("order_id")
            order = await customers_get.customer_view_order(order_id)
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
                                   f'Введите чтобы поменять "Точку А"',
                                   reply_markup=markup_customer.change_my_geo())
            await customer_states.CustomerChangeOrder.change_geo_from.set()
        if "Куда доставить" in message.text:
            await bot.send_message(message.from_user.id,
                                   f'Сейчас конечная "Точка Б" - "{order.geo_position_to}"')
            await bot.send_message(message.from_user.id,
                                   f'Введите чтобы поменять "Точку Б"',
                                   reply_markup=markup_customer.change_my_geo())
            await customer_states.CustomerChangeOrder.change_geo_to.set()
        if "Цену" in message.text:
            await bot.send_message(message.from_user.id,
                                   f'Цена заказа сейчас - "{order.price}"',
                                   reply_markup=markup_customer.markup_clean)
            await bot.send_message(message.from_user.id,
                                   f"Введите чтобы поменять Цену заказа",
                                   reply_markup=markup_customer.back())
            await customer_states.CustomerChangeOrder.change_money.set()
        if "Разблокировать заказ / Назад" in message.text:
            async with state.proxy() as data:
                await customers_set.customer_set_block_order(data.get("order_id"), 0)
            await customer_states.CustomerDetailsTasks.not_at_work.set()
            await bot.send_message(message.from_user.id,
                                   "<b>Ваш заказ снова доступен!</b>",
                                   reply_markup=markup_customer.details_task_not_at_work())

    @staticmethod
    async def change(message: types.Message, state: FSMContext):
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await bot.send_message(message.from_user.id,
                                   "Что будем менять ?",
                                   reply_markup=markup_customer.details_task_change())
            await customer_states.CustomerChangeOrder.enter.set()
        if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            async with state.proxy() as data:
                order_id = data.get("order_id")
                change_ = data.get("change")
                len_ = data.get("len")
            if len(message.text) < len_ and message.text != "Назад":
                await customers_set.customer_change_order(order_id, change_, message.text)
                await bot.send_message(message.from_user.id,
                                       f"Отлично! Мы поменяли {change_} заказа!",
                                       reply_markup=markup_customer.details_task_change())
                await customer_states.CustomerChangeOrder.enter.set()
            if len(message.text) > len_:
                await bot.send_message(message.from_user.id, "Слишком длинное предложение\n"
                                                             "Ограничение на название заказа - 100 символов\n"
                                                             "Ограничение на описание заказа - 255 символов")

    @staticmethod
    async def change_money(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order_id = data.get("order_id")
        if message.text.isdigit():
            await customers_set.customer_change_order(order_id, "price", message.text)
            await bot.send_message(message.from_user.id,
                                   "Отлично! Мы поменяли цену заказа!",
                                   reply_markup=markup_customer.details_task_change())
            await customer_states.CustomerChangeOrder.enter.set()
        if message.text != f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад" and not message.text.isdigit():
            await bot.send_message(message.from_user.id,
                                   "Надо ввести цифру!")
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerChangeOrder.enter.set()
            await bot.send_message(message.from_user.id,
                                   "Что будем менять ?",
                                   reply_markup=markup_customer.details_task_change())

    @staticmethod
    async def change_geo_position_from(message: types.Message, state: FSMContext):
        try:
            n = Nominatim(user_agent='User')
            loc = f"{message.location.latitude}, {message.location.longitude}"
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
                                   reply_markup=markup_customer.inline_approve_change_geo_from())
            async with state.proxy() as data:
                data["geo_data_from"] = f'{city}, ' \
                                        f'{address.raw.get("address").get("road")}, ' \
                                        f'{address.raw.get("address").get("house_number")}'
        except AttributeError:
            await bot.send_message(message.from_user.id,
                                   "Нужно отправить местоположение")
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerChangeOrder.enter.set()
            await bot.send_message(message.from_user.id,
                                   "Что будем менять ?",
                                   reply_markup=markup_customer.details_task_change())

    @staticmethod
    async def approve_change_geo_from(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            order_id = data.get("order_id")
            await customers_set.customer_change_order(order_id,
                                                      "geo_position_from",
                                                      data.get("geo_data_from"))
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Отлично! Мы изменили адрес Точки А",
                               reply_markup=markup_customer.details_task_change())
        await customer_states.CustomerChangeOrder.enter.set()

    @staticmethod
    async def change_geo_position_to(message: types.Message, state: FSMContext):
        try:
            n = Nominatim(user_agent='User')
            loc = f"{message.location.latitude}, {message.location.longitude}"
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
                                   reply_markup=markup_customer.inline_approve_change_geo_to())
            async with state.proxy() as data:
                data["geo_data_to"] = f'{city}, ' \
                                      f'{address.raw.get("address").get("road")}, ' \
                                      f'{address.raw.get("address").get("house_number")}'
        except AttributeError:
            await bot.send_message(message.from_user.id,
                                   "Нужно отправить местоположение")
        if message.text == f"{KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            await customer_states.CustomerChangeOrder.enter.set()
            await bot.send_message(message.from_user.id,
                                   "Что будем менять ?",
                                   reply_markup=markup_customer.details_task_change())

    @staticmethod
    async def approve_change_geo_to(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            order_id = data.get("order_id")
            await customers_set.customer_change_order(order_id,
                                                      "geo_position_to",
                                                      data.get("geo_data_to"))
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Отлично! Мы изменили адрес Точки Б",
                               reply_markup=markup_customer.details_task_change())
        await customer_states.CustomerChangeOrder.enter.set()

    @staticmethod
    def register_customer_details_tasks_change(dp):
        dp.register_callback_query_handler(CustomerDetailsTasksChange.change_task_enter,
                                           text='change',
                                           state=customer_states.CustomerDetailsTasks.not_at_work)
        dp.register_message_handler(CustomerDetailsTasksChange.change_task_main,
                                    state=customer_states.CustomerChangeOrder.enter)
        dp.register_message_handler(CustomerDetailsTasksChange.change,
                                    state=customer_states.CustomerChangeOrder.change)
        dp.register_message_handler(CustomerDetailsTasksChange.change_money,
                                    state=customer_states.CustomerChangeOrder.change_money)
        dp.register_message_handler(CustomerDetailsTasksChange.change_geo_position_from,
                                    content_types=['location', 'text'],
                                    state=customer_states.CustomerChangeOrder.change_geo_from)
        dp.register_callback_query_handler(CustomerDetailsTasksChange.approve_change_geo_from,
                                           text="approve_geo_from",
                                           state=customer_states.CustomerChangeOrder.change_geo_from)
        dp.register_message_handler(CustomerDetailsTasksChange.change_geo_position_to,
                                    content_types=['location', 'text'],
                                    state=customer_states.CustomerChangeOrder.change_geo_to)
        dp.register_callback_query_handler(CustomerDetailsTasksChange.approve_change_geo_to,
                                           text="approve_geo_to",
                                           state=customer_states.CustomerChangeOrder.change_geo_to)


class CustomerDetailsTasksStatus:
    @staticmethod
    async def details_status(message: types.Message, state: FSMContext):
        if "Отменить заказ" in message.text:
            async with state.proxy() as data:
                status = await general_get.check_details_status(data.get("order_id"))
            if status is None:
                await bot.send_message(message.from_user.id,
                                       "Заказ закрыт",
                                       reply_markup=markup_customer.main_menu())
                await customer_states.CustomerStart.customer_menu.set()
            if status:
                if status.customer_status:
                    await bot.send_message(message.from_user.id,
                                           "Вы уже не сможете отменить заказ так как вы его завершили",
                                           reply_markup=markup_customer.details_task_status())
                    await customer_states.CustomerDetailsTasksStatus.enter_status.set()
                else:
                    await bot.send_message(message.from_user.id,
                                           "Вы хотите отменить заказ ?",
                                           reply_markup=markup_customer.inline_cancel_task())
        if "Завершить заказ" in message.text:
            async with state.proxy() as data:
                status = await general_get.check_details_status(data.get("order_id"))
            if status is None:
                await bot.send_message(message.from_user.id,
                                       "Заказ закрыт",
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
                                       "Заказ закрыт",
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
                                                      datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CROSS_MARK') * 14}")
            await bot.send_message(data.get("user_id"),
                                   f"Ваша задача <b>{data.get('order_id')}</b> была отменёна заказчиком!")
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CROSS_MARK') * 14}")
        await customer_states.CustomerStart.customer_menu.set()
        await bot.send_message(callback.from_user.id,
                               "Вы отменили заказ!",
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
                                   f"была помечена заказчиком как ВЫПОЛНЕННАЯ!\n"
                                   f"Посмотрите в разделе 'Проверить статус заказа'\n"
                                   f"Если Заказчик и Исполнитель завершили заказ, "
                                   f"то заказ будет перемещен в раздел ВЫПОЛНЕННЫЕ")
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
        rate = ['1', '2', '3', '4', '5']
        if message.text in rate:
            async with state.proxy() as data:
                await customers_set.customer_set_rating_to_performer(data.get("user_id"), message.text)
                await customers_set.customer_set_rating_to_performer_in_review_db(data.get("order_id"), message.text)
            await bot.send_message(message.from_user.id,
                                   f"Вы поставили оценку Исполнителю - <b>{message.text}</b>\n"
                                   f"Спасибо за оценку!"
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

    @staticmethod
    def register_customer_details_tasks_status(dp):
        dp.register_message_handler(CustomerDetailsTasksStatus.details_status,
                                    state=customer_states.CustomerDetailsTasksStatus.enter_status)
        dp.register_callback_query_handler(CustomerDetailsTasksStatus.cancel_order,
                                           text="cancel",
                                           state=customer_states.CustomerDetailsTasksStatus.enter_status)
        dp.register_callback_query_handler(CustomerDetailsTasksStatus.no_cancel_order,
                                           text="no_cancel",
                                           state=customer_states.CustomerDetailsTasksStatus.enter_status)
        dp.register_callback_query_handler(CustomerDetailsTasksStatus.close_order,
                                           text="close_order",
                                           state=customer_states.CustomerDetailsTasksStatus.enter_status)
        dp.register_callback_query_handler(CustomerDetailsTasksStatus.no_close,
                                           text="no_close",
                                           state=customer_states.CustomerDetailsTasksStatus.enter_status)
        dp.register_message_handler(CustomerDetailsTasksStatus.rating,
                                    state=customer_states.CustomerDetailsTasksStatus.rating)
        dp.register_message_handler(CustomerDetailsTasksStatus.review,
                                    state=customer_states.CustomerDetailsTasksStatus.review)


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
                                   "Все сообщения в службу поддержки отправлены!",
                                   reply_markup=markup_customer.main_menu())
            await customer_states.CustomerStart.customer_menu.set()
        if message.text == "Вернуться главное меню":
            await bot.send_message(message.from_user.id,
                                   "Вы вошли в главное меню заказчика",
                                   reply_markup=markup_customer.main_menu())
            await customer_states.CustomerStart.customer_menu.set()
        if message.text != "Загрузить Фото" and message.text != "Загрузить Видео" \
                and message.text != "Завершить" and message.text != "Вернуться главное меню":
            await bot.send_message('@delivery_kerka_dev',
                                   f"Имя заказчика {message.from_user.first_name}\n"
                                   f"ID заказчика {message.from_user.id}\n"
                                   f"Сообщение от заказчика - <b>{message.text}</b>\n")
            await bot.send_message(message.from_user.id, "Сообщение досталено в техподдержку!")

    @staticmethod
    async def customer_upload_photo(message: types.Message):
        if message.content_type == "photo":
            CustomerHelp.logger.debug(f"Функция отправки фото от заказчика {message.from_user.id} в тех поддержку")
            await bot.send_message('@delivery_kerka_dev',
                                   f"Имя заказчика {message.from_user.first_name}\n"
                                   f"ID заказчика {message.from_user.id}\n"
                                   f"Фото заказчика {config.KEYBOARD.get('DOWNWARDS_BUTTON')}")
            await bot.send_photo('@delivery_kerka_dev',
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
            await bot.send_message('@delivery_kerka_dev',
                                   f"Имя заказчика {message.from_user.first_name}\n"
                                   f"ID заказчика {message.from_user.id}\n"
                                   f"Видео заказчика {config.KEYBOARD.get('DOWNWARDS_BUTTON')}")
            await bot.send_video('@delivery_kerka_dev',
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

    @staticmethod
    def register_customer_help(dp: Dispatcher):
        dp.register_message_handler(CustomerHelp.customer_help,
                                    content_types=['text'],
                                    state=customer_states.CustomerHelp.help)
        dp.register_message_handler(CustomerHelp.customer_upload_photo,
                                    content_types=['photo', 'text'],
                                    state=customer_states.CustomerHelp.upload_photo)
        dp.register_message_handler(CustomerHelp.customer_upload_video,
                                    content_types=['video', 'text'],
                                    state=customer_states.CustomerHelp.upload_video)


class CustomerHistory:
    @staticmethod
    async def history(message: types.Message, state: FSMContext):
        if "Вернуться в главное меню" in message.text:
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_customer.main_menu())
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
        if "Посмотреть детали заказа" in message.text:
            category = {f"Цветы": f"{KEYBOARD.get('BOUQUET')}",
                        f"Подарки": f"{KEYBOARD.get('WRAPPED_GIFT')}",
                        f"Кондитерка": f"{KEYBOARD.get('SHORTCAKE')}",
                        f"Документы": f"{KEYBOARD.get('PAGE_WITH_WITH_CURL')}",
                        f"Погрузка/Разгрузка": f"{KEYBOARD.get('ARROWS_BUTTON')}",
                        f"Другое": f"{KEYBOARD.get('INPUT_LATIN_LETTERS')}"}
            icon_category = None
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
                                   f"Откуда - <a href='https://yandex.ru/maps/?text={'+'.join(order.geo_position_from.split())}'>{order.geo_position_from}</a>\n"
                                   f"{config.KEYBOARD.get('B_BUTTON')} "
                                   f"Куда - <a href='https://yandex.ru/maps/?text={'+'.join(order.geo_position_to.split())}'>{order.geo_position_to}</a>\n"
                                   f"{config.KEYBOARD.get('INFORMATION')} "
                                   f"Название - <b>{order.title}</b>\n"
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
                                   f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                   f"Действует до: <b>{order.order_expired}</b>\n",
                                   reply_markup=markup_customer.details_task_history_details_order())
        if "Профиль исполнителя" in message.text:
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"Профиль <b>Исполнителя</b>:\n"
                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                   f"ID: <b>{performer_res.user_id}</b>\n"
                                   f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                   f"Никнейм <b>@{performer_res.username}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Номер <b>{performer_res.telephone}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Имя <b>{performer_res.first_name}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Фамилия <b>{performer_res.last_name}</b>\n"
                                   f"{config.KEYBOARD.get('BAR_CHART')} "
                                   f"Рейтинг <b>"
                                   f"{performer_res.performer_rating}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   )
        if "Вернуться в главное меню" in message.text:
            await customer_states.CustomerStart.customer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_customer.main_menu())

    @staticmethod
    async def order_details(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order = data.get(data.get("order_id"))
        if message.text == "Посмотреть фото":
            try:
                await bot.send_photo(message.from_user.id, order.photo)
            except:
                await bot.send_message(message.from_user.id, "В вашем заказе нет фото")
        if message.text == "Посмотреть видео":
            try:
                await bot.send_video(message.from_user.id, order.video)
            except:
                await bot.send_message(message.from_user.id, "В вашем заказе нет видео")
        if "Назад в детали заказа" in message.text:
            await customer_states.CustomerHistory.order_history.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в детали заказа",
                                   reply_markup=markup_customer.details_task_history())

    @staticmethod
    def register_customer_history(dp):
        dp.register_message_handler(CustomerHistory.history,
                                    state=customer_states.CustomerHistory.enter_history)
        dp.register_message_handler(CustomerHistory.order_history,
                                    state=customer_states.CustomerHistory.order_history)
        dp.register_message_handler(CustomerHistory.order_details,
                                    state=customer_states.CustomerHistory.order_history_details)

