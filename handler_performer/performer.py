import logging
from collections import Counter
from datetime import datetime, timedelta
from random import randint

from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

from bot import dp, bot
from data.commands import performers_get, performers_set, customers_get, general_get
# from data.get_set_db import customer_get_db_obj, performer_get_db_obj, performer_set_db_obj, \
#     global_db_obj, global_set_db_obj
from markups import markup_performer
from settings import config
from states import performer_states


class PerformerMain:
    @staticmethod
    async def hi_performer(callback: types.CallbackQuery):
        performer = await performers_get.performer_select(callback.from_user.id)
        if performer is None:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button = types.KeyboardButton(text='Запрос телефона', request_contact=True)
            keyboard.add(button)
            await bot.send_message(callback.from_user.id,
                                   f"{callback.from_user.first_name}\n"
                                   f"Поделитесь с нами вашим номером телефона!\n",
                                   reply_markup=keyboard)
            await performer_states.PerformerPhone.phone.set()
        elif performer.ban == 0:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(callback.from_user.id,
                                   "Спасибо что пользуетесь нашим ботом!",
                                   reply_markup=markup_performer.main_menu())
        else:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await bot.send_message(callback.from_user.id, "Вы заблокированы! Обратитесь в техподдержку!")

    @staticmethod
    async def phone(message: types.Message):
        if message.contact.user_id == message.from_user.id:
            res = message.contact.phone_number[-10:]
            await performers_set.performer_add(message.from_user.id,
                                               message.from_user.username,
                                               f'+7{res}',
                                               message.from_user.first_name,
                                               message.from_user.last_name)
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Спасибо что пользуетесь нашим ботом!",
                                   reply_markup=markup_performer.main_menu())
        else:
            await bot.send_message(message.from_user.id,
                                   "Это не ваш номер телефона! \n"
                                   "Нажмите /start чтобы начать заново")

    @staticmethod
    async def main(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f"{message.from_user.first_name} Вы в главном меню Исполнителя",
                               reply_markup=markup_performer.main_menu())
        await performer_states.PerformerStart.performer_menu.set()

    @staticmethod
    async def performer_menu(message: types.Message, state: FSMContext):
        await state.finish()
        if "Мой профиль" in message.text:
            PerformerProfile.register_performer_profile(dp)
            res = await performers_get.performer_select(message.from_user.id)
            if res.performer_category == "pedestrian":
                status = "Пешеход"
                icon = f"{config.KEYBOARD.get('PERSON_RUNNING')}"
            if res.performer_category == "scooter":
                status = "На самокате"
                icon = f"{config.KEYBOARD.get('KICK_SCOOTER')}"
            elif res.performer_category == "car":
                status = "На машине"
                icon = f"{config.KEYBOARD.get('AUTOMOBILE')}"
            await performer_states.PerformerProfile.my_profile.set()
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"Ваш профиль <b>Исполнителя</b>:\n"
                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                   f"Ваш ID: <b>{res.user_id}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Ваш никнейм: <b>@{res.username}</b>\n"
                                   f"{config.KEYBOARD.get('TELEPHONE')} "
                                   f"Ваш номер: <b>{res.telephone}</b>\n"
                                   f"{config.KEYBOARD.get('DOLLAR')} "
                                   f"Ваш текущий баланс: <b>{res.performer_money}</b> руб.\n"
                                   f"{config.KEYBOARD.get('BAR_CHART')} "
                                   f"Ваш рейтинг: <b>{str(res.performer_rating)[0:5]}</b>\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                   f"Взял заказов: <b>{res.get_orders}</b>\n"
                                   f"{config.KEYBOARD.get('CROSS_MARK')} "
                                   f"Отменил заказов: <b>{res.canceled_orders}</b>\n"
                                   f"{icon} Ваша категория: <b>{status}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   reply_markup=markup_performer.performer_profile())
        if "Помощь" in message.text:
            PerformerHelp.register_performer_help(dp)
            await performer_states.PerformerHelp.help.set()
            user_status_chat = await performers_get.check_private_chat_status(message.from_user.id)
            if user_status_chat is None:
                user_status_chat = False
            else:
                async with state.proxy() as data:
                    data["user_status_chat"] = user_status_chat.user_id
            await bot.send_message(message.from_user.id,
                                   "Опишите вашу проблему, можете прикрепить фото или видео\n"
                                   "Когда закончите сможете вернуться в главное меню",
                                   reply_markup=markup_performer.photo_or_video_help(user_status_chat))
        if "Доступные Задачи" in message.text:
            performer = await performers_get.performer_select(message.from_user.id)
            performer_money = performer.performer_money
            if performer_money < 50:
                PerformerProfile.register_performer_profile(dp)
                await performer_states.PerformerProfile.my_profile.set()
                await bot.send_message(message.from_user.id,
                                       "<b>У вас отрицательный баланс!</b>\n"
                                       "<b>Пополните ваш баланс</b>",
                                       reply_markup=markup_performer.performer_profile())
            if performer_money >= 50:
                PerformerTasks.register_performer_tasks(dp)
                await performer_states.PerformerTasks.check_all_orders.set()
                await bot.send_message(message.from_user.id,
                                       "Посмотреть доступные задачи ?",
                                       reply_markup=markup_performer.approve())
        if "Задачи в работе" in message.text:
            res = await performers_get.performer_view_list_orders(message.from_user.id)
            if res:
                await performer_states.PerformerDetailsTasks.details_tasks.set()
                PerformerDetailsTasks.register_performer_details_tasks(dp)
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for i in res:
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
                        await bot.send_photo(message.from_user.id, i.image)
                        await bot.send_message(message.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"<b>Детали заказа</b>\n"
                                               f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                               f"Категория - <b>{i.category_delivery}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID заказа - <b>{i.order_id}</b>\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Откуда - <b>{i.geo_position_from}</b>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <b>{i.geo_position_to}</b>\n"
                                               f"{config.KEYBOARD.get('INFORMATION')} "
                                               f"Название - <b>{i.title}</b>\n"
                                               f"{config.KEYBOARD.get('CLIPBOARD')} "
                                               f"Описание - <b>{i.description}</b>\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} "
                                               f"Цена - <b>{i.price}</b>\n"
                                               f"{config.KEYBOARD.get('MONEY_BAG')} "
                                               f"Ценность этого товара - <b>{i.order_worth}</b>\n"
                                               f"{icon} "
                                               f"Исполнитель - <b>{p_status}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID заказа - <b>{i.order_id}</b>\n"
                                               f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                               f"Заказ создан: <b>{i.order_create}</b>\n"
                                               f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                               f"Действует до: <b>{i.order_expired}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}\n")
                        keyboard.add(f"{icon} {i.order_id} {icon}")
                    except:
                        try:
                            await bot.send_video(message.from_user.id, i.video)
                            await bot.send_message(message.from_user.id,
                                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                                   f"<b>Детали заказа</b>\n"
                                                   f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                                   f"Категория - <b>{i.category_delivery}</b>\n"
                                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                                   f"ID заказа - <b>{i.order_id}</b>\n"
                                                   f"{config.KEYBOARD.get('A_BUTTON')} "
                                                   f"Откуда - <b>{i.geo_position_from}</b>\n"
                                                   f"{config.KEYBOARD.get('B_BUTTON')} "
                                                   f"Куда - <b>{i.geo_position_to}</b>\n"
                                                   f"{config.KEYBOARD.get('INFORMATION')} "
                                                   f"Название - <b>{i.title}</b>\n"
                                                   f"{config.KEYBOARD.get('CLIPBOARD')} "
                                                   f"Описание - <b>{i.description}</b>\n"
                                                   f"{config.KEYBOARD.get('DOLLAR')} "
                                                   f"Цена - <b>{i.price}</b>\n"
                                                   f"{config.KEYBOARD.get('MONEY_BAG')} "
                                                   f"Ценность этого товара - <b>{i.order_worth}</b>\n"
                                                   f"{icon} "
                                                   f"Исполнитель - <b>{p_status}</b>\n"
                                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                                   f"ID заказа - <b>{i.order_id}</b>\n"
                                                   f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                                   f"Заказ создан: <b>{i.order_create}</b>\n"
                                                   f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                                   f"Действует до: <b>{i.order_expired}</b>\n"
                                                   f"{config.KEYBOARD.get('DASH') * 14}\n")
                            keyboard.add(f"{icon} {i.order_id} {icon}")
                        except:
                            await bot.send_message(message.from_user.id,
                                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                                   f"<b>Детали заказа</b>\n"
                                                   f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                                   f"Категория - <b>{i.category_delivery}</b>\n"
                                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                                   f"ID заказа - <b>{i.order_id}</b>\n"
                                                   f"{config.KEYBOARD.get('A_BUTTON')} "
                                                   f"Откуда - <b>{i.geo_position_from}</b>\n"
                                                   f"{config.KEYBOARD.get('B_BUTTON')} "
                                                   f"Куда - <b>{i.geo_position_to}</b>\n"
                                                   f"{config.KEYBOARD.get('INFORMATION')} "
                                                   f"Название - <b>{i.title}</b>\n"
                                                   f"{config.KEYBOARD.get('CLIPBOARD')} "
                                                   f"Описание - <b>{i.description}</b>\n"
                                                   f"{config.KEYBOARD.get('DOLLAR')} "
                                                   f"Цена - <b>{i.price}</b>\n"
                                                   f"{config.KEYBOARD.get('MONEY_BAG')} "
                                                   f"Ценность этого товара - <b>{i.order_worth}</b>\n"
                                                   f"{icon} "
                                                   f"Исполнитель - <b>{p_status}</b>\n"
                                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                                   f"ID заказа - <b>{i.order_id}</b>\n"
                                                   f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                                   f"Заказ создан: <b>{i.order_create}</b>\n"
                                                   f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                                   f"Действует до: <b>{i.order_expired}</b>\n"
                                                   f"{config.KEYBOARD.get('DASH') * 14}\n")
                            keyboard.add(f"{icon} {i.order_id} {icon}")
                keyboard.add("Вернуться в главное меню")
                await bot.send_message(message.from_user.id,
                                       f"Всего в работе {len(res)} задач\n"
                                       f"Выберите ID задачи чтобы их просмотреть или завершить",
                                       reply_markup=keyboard)
            else:
                await performer_states.PerformerStart.performer_menu.set()
                await bot.send_message(message.from_user.id, "У вас еще нет взятых заказов")

    #         if "Выполненные Задачи" in message.text:
    #             try:
    #                 res = performer_get_db_obj.performer_all_completed_orders(message.from_user.id)
    #                 if res:
    #                     finished_orders = InlineKeyboardMarkup()
    #                     year = []
    #                     for i in res:
    #                         year.append(i[15].strftime('%Y'))
    #                     res_years = Counter(year)
    #                     for k, v in res_years.items():
    #                         finished_orders.insert(InlineKeyboardButton(text=f"{k} ({v})",
    #                                                                     callback_data=f"p_year_finish_{k}"))
    #                     await bot.send_message(message.from_user.id,
    #                                            "Выберите год\n"
    #                                            "В скобках указано количество завершенных заказов",
    #                                            reply_markup=finished_orders)
    #                     await performer_states.PerformerStart.performer_menu.set()
    #                 else:
    #                     await performer_states.PerformerStart.performer_menu.set()
    #                     await bot.send_message(message.from_user.id,
    #                                            "У вас еще нет завершенных заказов!")
    #             except:
    #                 await performer_states.PerformerStart.performer_menu.set()
    #                 await bot.send_message(message.from_user.id,
    #                                        "У вас еще нет завершенных заказов!")
    #
    #     @staticmethod
    #     async def choose_month(callback: types.CallbackQuery, state: FSMContext):
    #         await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #         year = callback.data[14:]
    #         async with state.proxy() as data:
    #             data["year"] = year
    #         res = performer_get_db_obj.performer_get_finished_orders_year(callback.from_user.id,
    #                                                                       year)
    #         finished_orders = InlineKeyboardMarkup()
    #         months = []
    #         for i in res:
    #             months.append(i[15].strftime('%B'))
    #         res_months = Counter(months)
    #         for k, v in res_months.items():
    #             finished_orders.insert(InlineKeyboardButton(text=f"{k} ({v})",
    #                                                         callback_data=f"p_month_finish_{k}"))
    #         await bot.send_message(callback.from_user.id,
    #                                "Выберите месяц",
    #                                reply_markup=finished_orders)
    #
    #     @staticmethod
    #     async def choose_day(callback: types.CallbackQuery, state: FSMContext):
    #         await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #         months_dict = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    #                        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    #         month = callback.data[15:]
    #         month_number = None
    #         for k, v in months_dict.items():
    #             if k == month:
    #                 month_number = v
    #         async with state.proxy() as data:
    #             data["month"] = month_number
    #         res = performer_get_db_obj.performer_get_finished_orders_month(callback.from_user.id,
    #                                                                        data.get("year"),
    #                                                                        month_number)
    #         finished_orders = InlineKeyboardMarkup()
    #         days = []
    #         for i in res:
    #             days.append(i[15].strftime('%d'))
    #         res_days = Counter(days)
    #         for k, v in res_days.items():
    #             finished_orders.insert(InlineKeyboardButton(text=f"{k} ({v})",
    #                                                         callback_data=f"p_day_finish_{k}"))
    #         await bot.send_message(callback.from_user.id,
    #                                "Выберите день",
    #                                reply_markup=finished_orders)
    #
    #     @staticmethod
    #     async def choose_job(callback: types.CallbackQuery, state: FSMContext):
    #         await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #         day = callback.data[13:]
    #         async with state.proxy() as data:
    #             data["day"] = day
    #         res = performer_get_db_obj.performer_get_finished_orders_day(callback.from_user.id,
    #                                                                      data.get("year"),
    #                                                                      data.get("month"),
    #                                                                      day)
    #         if res:
    #             keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #             for i in res:
    #                 try:
    #                     await bot.send_photo(callback.from_user.id, i[7])
    #                     await bot.send_message(callback.from_user.id,
    #                                            f"{config.KEYBOARD.get('DASH') * 14}\n"
    #                                            f"<b>Детали заказа</b>\n"
    #                                            f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
    #                                            f"Категория - <b>{i[16]}</b>\n"
    #                                            f"{config.KEYBOARD.get('ID_BUTTON')} "
    #                                            f"ID заказа - <b>{i[11]}</b>\n"
    #                                            f"{config.KEYBOARD.get('A_BUTTON')} "
    #                                            f"Откуда - <b>{i[2]}</b>\n"
    #                                            f"{config.KEYBOARD.get('B_BUTTON')} "
    #                                            f"Куда - <b>{i[3]}</b>\n"
    #                                            f"{config.KEYBOARD.get('INFORMATION')} "
    #                                            f"Название - <b>{i[4]}</b>\n"
    #                                            f"{config.KEYBOARD.get('CLIPBOARD')} "
    #                                            f"Описание - <b>{i[6]}</b>\n"
    #                                            f"{config.KEYBOARD.get('DOLLAR')} "
    #                                            f"Цена - <b>{i[5]}</b>\n"
    #                                            f"{config.KEYBOARD.get('DASH') * 14}\n")
    #                     keyboard.add(f"{i[11]}")
    #                     async with state.proxy() as data:
    #                         data[i[11]] = {
    #                             'Название': i[4],
    #                             'ID заказа': i[11],
    #                             'ID исполнителя': i[9],
    #                             'Бюджет': i[5],
    #                         }
    #                 except:
    #                     try:
    #                         await bot.send_video(callback.from_user.id, i[8])
    #                         await bot.send_message(callback.from_user.id,
    #                                                f"{config.KEYBOARD.get('DASH') * 14}\n"
    #                                                f"<b>Детали заказа</b>\n"
    #                                                f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
    #                                                f"Категория - <b>{i[16]}</b>\n"
    #                                                f"{config.KEYBOARD.get('ID_BUTTON')} "
    #                                                f"ID заказа - <b>{i[11]}</b>\n"
    #                                                f"{config.KEYBOARD.get('A_BUTTON')} "
    #                                                f"Откуда - <b>{i[2]}</b>\n"
    #                                                f"{config.KEYBOARD.get('B_BUTTON')} "
    #                                                f"Куда - <b>{i[3]}</b>\n"
    #                                                f"{config.KEYBOARD.get('INFORMATION')} "
    #                                                f"Название - <b>{i[4]}</b>\n"
    #                                                f"{config.KEYBOARD.get('CLIPBOARD')} "
    #                                                f"Описание - <b>{i[6]}</b>\n"
    #                                                f"{config.KEYBOARD.get('DOLLAR')} "
    #                                                f"Цена - <b>{i[5]}</b>\n"
    #                                                f"{config.KEYBOARD.get('DASH') * 14}\n")
    #                         keyboard.add(f"{i[11]}")
    #                         async with state.proxy() as data:
    #                             data[i[11]] = {
    #                                 'Название': i[4],
    #                                 'ID заказа': i[11],
    #                                 'ID исполнителя': i[9],
    #                                 'Бюджет': i[5],
    #                             }
    #                     except:
    #                         await bot.send_message(callback.from_user.id,
    #                                                f"{config.KEYBOARD.get('DASH') * 14}\n"
    #                                                f"<b>Детали заказа</b>\n"
    #                                                f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
    #                                                f"Категория - <b>{i[16]}</b>\n"
    #                                                f"{config.KEYBOARD.get('ID_BUTTON')} "
    #                                                f"ID заказа - <b>{i[11]}</b>\n"
    #                                                f"{config.KEYBOARD.get('A_BUTTON')} "
    #                                                f"Откуда - <b>{i[2]}</b>\n"
    #                                                f"{config.KEYBOARD.get('B_BUTTON')} "
    #                                                f"Куда - <b>{i[3]}</b>\n"
    #                                                f"{config.KEYBOARD.get('INFORMATION')} "
    #                                                f"Название - <b>{i[4]}</b>\n"
    #                                                f"{config.KEYBOARD.get('CLIPBOARD')} "
    #                                                f"Описание - <b>{i[6]}</b>\n"
    #                                                f"{config.KEYBOARD.get('DOLLAR')} "
    #                                                f"Цена - <b>{i[5]}</b>\n"
    #                                                f"{config.KEYBOARD.get('DASH') * 14}\n")
    #                         keyboard.add(f"{i[11]}")
    #                         async with state.proxy() as data:
    #                             data[i[11]] = {
    #                                 'Название': i[4],
    #                                 'ID заказа': i[11],
    #                                 'ID исполнителя': i[9],
    #                                 'Бюджет': i[5],
    #                             }
    #             keyboard.add("Вернуться в главное меню")
    #             await bot.send_message(callback.from_user.id,
    #                                    "Выберите ID задачи чтобы войти в детали заказа",
    #                                    reply_markup=keyboard)
    #             await performer_states.PerformerHistory.enter_history.set()
    #             PerformerHistory.register_performer_history(dp)
    #
    @staticmethod
    def register_performer_handler(dp: Dispatcher):
        dp.register_message_handler(PerformerMain.phone, content_types=['contact'],
                                    state=performer_states.PerformerPhone.phone)
        dp.register_callback_query_handler(PerformerMain.hi_performer, text='performer')
        dp.register_message_handler(PerformerMain.performer_menu, state=performer_states.PerformerStart.performer_menu)
        # dp.register_callback_query_handler(PerformerMain.choose_month,
        #                                    state=performer_states.PerformerStart.performer_menu,
        #                                    text_contains='p_year_finish_')
        # dp.register_callback_query_handler(PerformerMain.choose_day,
        #                                    state=performer_states.PerformerStart.performer_menu,
        #                                    text_contains='p_month_finish_')
        # dp.register_callback_query_handler(PerformerMain.choose_job,
        #                                    state=performer_states.PerformerStart.performer_menu,
        #                                    text_contains='p_day_finish_')


class PerformerProfile:
    @staticmethod
    async def performer_profile(message: types.Message):
        if "Главное меню" in message.text:
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_performer.main_menu(),
                                   )
        if "Вывести средства" in message.text:
            await bot.send_message(message.from_user.id,
                                   "Здесь будет реализована функция вывода средств")
        # if "Статус категории" in message.text:
        #     try:
        #         res = performer_get_db_obj.performer_trying_change_self_category(message.from_user.id)[0]
        #         limitation = str(datetime.now() - datetime.strptime(str(res), '%Y-%m-%d %H:%M:%S'))[:1]
        #         if limitation == "-":
        #             await bot.send_message(message.from_user.id,
        #                                    f"У вас еще действует ограничение на смену статуса\n"
        #                                    f"Ограничение снимется {res.strftime('%d %B, %H:%M:%S')}")
        #             await performer_states.PerformerProfile.my_profile.set()
        #         if limitation != "-":
        #             await bot.send_message(message.from_user.id,
        #                                    "Здесь вы сможете сменить свой статус\n"
        #                                    "<b>Статус вы можете сменить только раз в 12 часов</b>",
        #                                    reply_markup=markup_performer.performer_profile_change_status())
        #             await performer_states.PerformerProfile.change_status.set()
        #     except:
        #         await bot.send_message(message.from_user.id,
        #                                "Здесь вы сможете сменить свой статус\n"
        #                                "<b>Статус вы можете сменить только раз в 12 часов</b>",
        #                                reply_markup=markup_performer.performer_profile_change_status())
        #         await performer_states.PerformerProfile.change_status.set()
        # if "Пополнить баланс" in message.text:
        #     pay_exists = global_db_obj.get_payment_exists(message.from_user.id)
        #     if pay_exists:
        #         global_set_db_obj.delete_payment_exists(message.from_user.id)
        #     await bot.send_message(message.from_user.id,
        #                            "Пополнение баланса должно быть не меньше <b>50</b> рублей!"
        #                            "Введите сумму, на которую вы хотите пополнить баланс",
        #                            reply_markup=markup_performer.back_user_profile())
        #     await performer_states.PerformerProfile.pay.set()
        if "Статистика по заказам" in message.text:
            count_orders = await performers_get.performer_count_orders(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} Всего заказов вы взяли - "
                                   f"<b>{count_orders[0]}</b>\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} В работе - <b>{count_orders[1]}</b>\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} Выполненных - "
                                   f"<b>{count_orders[2]}</b>\n"
                                   f"{config.KEYBOARD.get('CROSS_MARK')} Отменённых "
                                   f"<b>{count_orders[3]}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   )

    # @staticmethod
    # async def performer_profile_change_status(message: types.Message):
    #     if message.text == f"{config.KEYBOARD.get('PERSON_RUNNING')} Я пешеход":
    #         performer_set_db_obj.performer_set_self_status(message.from_user.id,
    #                                                        "pedestrian",
    #                                                        str(datetime.now() + timedelta(hours=12))[:19])
    #         await bot.send_message(message.from_user.id,
    #                                "Теперь ты пешеход!")
    #         res = performer_get_db_obj.performer_exists(message.from_user.id)
    #         status = "Пешеход"
    #         icon = f"{config.KEYBOARD.get('PERSON_RUNNING')}"
    #         await performer_states.PerformerProfile.my_profile.set()
    #         await bot.send_message(message.from_user.id,
    #                                f"{config.KEYBOARD.get('DASH') * 14}\n"
    #                                f"Ваш профиль <b>Исполнителя</b>:\n"
    #                                f"{config.KEYBOARD.get('ID_BUTTON')} "
    #                                f"Ваш ID: <b>{res[1]}</b>\n"
    #                                f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
    #                                f"Ваш никнейм: <b>@{res[2]}</b>\n"
    #                                f"{config.KEYBOARD.get('TELEPHONE')} "
    #                                f"Ваш номер: <b>{res[3]}</b>\n"
    #                                f"{config.KEYBOARD.get('DOLLAR')} "
    #                                f"Ваш текущий баланс: <b>{res[6]}</b> руб.\n"
    #                                f"{config.KEYBOARD.get('BAR_CHART')} Ваш рейтинг: <b>{str(res[7])[0:5]}</b>\n"
    #                                f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} Взял заказов: <b>{res[9]}</b>\n"
    #                                f"{config.KEYBOARD.get('CROSS_MARK')} Отменил заказов: <b>{res[10]}</b>\n"
    #                                f"{icon} Ваша категория: <b>{status}</b>\n"
    #                                f"{config.KEYBOARD.get('DASH') * 14}",
    #                                reply_markup=markup_performer.performer_profile())
    #     if message.text == f"{config.KEYBOARD.get('AUTOMOBILE')} Я на транспорте":
    #         await performer_states.PerformerProfile.change_status_transport.set()
    #         await bot.send_message(message.from_user.id,
    #                                "Выберите ваш транспорт",
    #                                reply_markup=markup_performer.performer_profile_change_status_transport())
    #     if message.text == f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
    #         res = performer_get_db_obj.performer_exists(message.from_user.id)
    #         if res[11] == "pedestrian":
    #             status = "Пешеход"
    #             icon = f"{config.KEYBOARD.get('PERSON_RUNNING')}"
    #         if res[11] == "scooter":
    #             status = "На самокате"
    #             icon = f"{config.KEYBOARD.get('KICK_SCOOTER')}"
    #         elif res[11] == "car":
    #             status = "На машине"
    #             icon = f"{config.KEYBOARD.get('AUTOMOBILE')}"
    #         await performer_states.PerformerProfile.my_profile.set()
    #         await bot.send_message(message.from_user.id,
    #                                f"{config.KEYBOARD.get('DASH') * 14}\n"
    #                                f"Ваш профиль <b>Исполнителя</b>:\n"
    #                                f"{config.KEYBOARD.get('ID_BUTTON')} "
    #                                f"Ваш ID: <b>{res[1]}</b>\n"
    #                                f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
    #                                f"Ваш никнейм: <b>@{res[2]}</b>\n"
    #                                f"{config.KEYBOARD.get('TELEPHONE')} "
    #                                f"Ваш номер: <b>{res[3]}</b>\n"
    #                                f"{config.KEYBOARD.get('DOLLAR')} "
    #                                f"Ваш текущий баланс: <b>{res[6]}</b> руб.\n"
    #                                f"{config.KEYBOARD.get('BAR_CHART')} Ваш рейтинг: <b>{str(res[7])[0:5]}</b>\n"
    #                                f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} Взял заказов: <b>{res[9]}</b>\n"
    #                                f"{config.KEYBOARD.get('CROSS_MARK')} Отменил заказов: <b>{res[10]}</b>\n"
    #                                f"{icon} Ваша категория: <b>{status}</b>\n"
    #                                f"{config.KEYBOARD.get('DASH') * 14}",
    #                                reply_markup=markup_performer.performer_profile())
    #
    # @staticmethod
    # async def transport(message: types.Message):
    #     if message.text == f"{config.KEYBOARD.get('AUTOMOBILE')} Я на машине":
    #         performer_set_db_obj.performer_set_self_status(message.from_user.id,
    #                                                        "car",
    #                                                        str(datetime.now() + timedelta(hours=12))[:19])
    #         await bot.send_message(message.from_user.id,
    #                                "Теперь ты на машине!")
    #         res = performer_get_db_obj.performer_exists(message.from_user.id)
    #         status = "На машине"
    #         icon = f"{config.KEYBOARD.get('AUTOMOBILE')}"
    #         await performer_states.PerformerProfile.my_profile.set()
    #         await bot.send_message(message.from_user.id,
    #                                f"{config.KEYBOARD.get('DASH') * 14}\n"
    #                                f"Ваш профиль <b>Исполнителя</b>:\n"
    #                                f"{config.KEYBOARD.get('ID_BUTTON')} "
    #                                f"Ваш ID: <b>{res[1]}</b>\n"
    #                                f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
    #                                f"Ваш никнейм: <b>@{res[2]}</b>\n"
    #                                f"{config.KEYBOARD.get('TELEPHONE')} "
    #                                f"Ваш номер: <b>{res[3]}</b>\n"
    #                                f"{config.KEYBOARD.get('DOLLAR')} "
    #                                f"Ваш текущий баланс: <b>{res[6]}</b> руб.\n"
    #                                f"{config.KEYBOARD.get('BAR_CHART')} Ваш рейтинг: <b>{str(res[7])[0:5]}</b>\n"
    #                                f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} Взял заказов: <b>{res[9]}</b>\n"
    #                                f"{config.KEYBOARD.get('CROSS_MARK')} Отменил заказов: <b>{res[10]}</b>\n"
    #                                f"{icon} Ваша категория: <b>{status}</b>\n"
    #                                f"{config.KEYBOARD.get('DASH') * 14}",
    #                                reply_markup=markup_performer.performer_profile())
    #     if message.text == f"{config.KEYBOARD.get('KICK_SCOOTER')} Я на самокате":
    #         performer_set_db_obj.performer_set_self_status(message.from_user.id,
    #                                                        "scooter",
    #                                                        str(datetime.now() + timedelta(hours=12))[:19])
    #         await bot.send_message(message.from_user.id,
    #                                "Теперь ты на самокате!")
    #         res = performer_get_db_obj.performer_exists(message.from_user.id)
    #         status = "На самокате"
    #         icon = f"{config.KEYBOARD.get('KICK_SCOOTER')}"
    #         await performer_states.PerformerProfile.my_profile.set()
    #         await bot.send_message(message.from_user.id,
    #                                f"{config.KEYBOARD.get('DASH') * 14}\n"
    #                                f"Ваш профиль <b>Исполнителя</b>:\n"
    #                                f"{config.KEYBOARD.get('ID_BUTTON')} "
    #                                f"Ваш ID: <b>{res[1]}</b>\n"
    #                                f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
    #                                f"Ваш никнейм: <b>@{res[2]}</b>\n"
    #                                f"{config.KEYBOARD.get('TELEPHONE')} "
    #                                f"Ваш номер: <b>{res[3]}</b>\n"
    #                                f"{config.KEYBOARD.get('DOLLAR')} "
    #                                f"Ваш текущий баланс: <b>{res[6]}</b> руб.\n"
    #                                f"{config.KEYBOARD.get('BAR_CHART')} Ваш рейтинг: <b>{str(res[7])[0:5]}</b>\n"
    #                                f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} Взял заказов: <b>{res[9]}</b>\n"
    #                                f"{config.KEYBOARD.get('CROSS_MARK')} Отменил заказов: <b>{res[10]}</b>\n"
    #                                f"{icon} Ваша категория: <b>{status}</b>\n"
    #                                f"{config.KEYBOARD.get('DASH') * 14}",
    #                                reply_markup=markup_performer.performer_profile())
    #     if message.text == f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
    #         res = performer_get_db_obj.performer_exists(message.from_user.id)
    #         if res[11] == "pedestrian":
    #             status = "Пешеход"
    #             icon = f"{config.KEYBOARD.get('PERSON_RUNNING')}"
    #         if res[11] == "scooter":
    #             status = "На самокате"
    #             icon = f"{config.KEYBOARD.get('KICK_SCOOTER')}"
    #         elif res[11] == "car":
    #             status = "На машине"
    #             icon = f"{config.KEYBOARD.get('AUTOMOBILE')}"
    #         await performer_states.PerformerProfile.my_profile.set()
    #         await bot.send_message(message.from_user.id,
    #                                f"{config.KEYBOARD.get('DASH') * 14}\n"
    #                                f"Ваш профиль <b>Исполнителя</b>:\n"
    #                                f"{config.KEYBOARD.get('ID_BUTTON')} "
    #                                f"Ваш ID: <b>{res[1]}</b>\n"
    #                                f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
    #                                f"Ваш никнейм: <b>@{res[2]}</b>\n"
    #                                f"{config.KEYBOARD.get('TELEPHONE')} "
    #                                f"Ваш номер: <b>{res[3]}</b>\n"
    #                                f"{config.KEYBOARD.get('DOLLAR')} "
    #                                f"Ваш текущий баланс: <b>{res[6]}</b> руб.\n"
    #                                f"{config.KEYBOARD.get('BAR_CHART')} Ваш рейтинг: <b>{str(res[7])[0:5]}</b>\n"
    #                                f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} Взял заказов: <b>{res[9]}</b>\n"
    #                                f"{config.KEYBOARD.get('CROSS_MARK')} Отменил заказов: <b>{res[10]}</b>\n"
    #                                f"{icon} Ваша категория: <b>{status}</b>\n"
    #                                f"{config.KEYBOARD.get('DASH') * 14}",
    #                                reply_markup=markup_performer.performer_profile())
    #
    # @staticmethod
    # async def pay(message: types.Message):
    #     if f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в Мой профиль" == message.text:
    #         await performer_states.PerformerProfile.my_profile.set()
    #         await bot.send_message(message.from_user.id,
    #                                "Вы вернулись в Мой профиль",
    #                                reply_markup=markup_performer.performer_profile())
    #     if f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в Мой профиль" != message.text:
    #         if message.text.isdigit() and int(message.text) >= 50:
    #             try:
    #                 message_money = int(message.text)
    #                 if message_money >= 1:
    #                     comment = f"Выставлен счёт для {message.from_user.first_name}_{randint(1, 10000)}"
    #                     bill = config.P2P.bill(amount=message_money, lifetime=5, comment=comment)
    #                     global_set_db_obj.add_payment(message.from_user.id, message_money, bill.bill_id)
    #                     await bot.send_message(message.from_user.id,
    #                                            f"Вам нужно отправить <b>{message_money}</b> руб на наш счёт QIWI\n"
    #                                            f"{comment}",
    #                                            reply_markup=markup_performer.buy_menu(url=bill.pay_url,
    #                                                                                   bill=bill.bill_id))
    #                 else:
    #                     await bot.send_message(message.from_user.id,
    #                                            "Минимальная сумма для пополнения 1 руб.",
    #                                            reply_markup=markup_performer.cancel_pay())
    #             except ValueError:
    #                 await bot.send_message(message.from_user.id, "Введите целое число")
    #         else:
    #             await bot.send_message(message.from_user.id,
    #                                    "Пополнение баланса должно быть не меньше <b>50</b> рублей!")
    #
    # @staticmethod
    # async def check(callback: types.CallbackQuery, state: FSMContext):
    #     bill = str(callback.data[6:])
    #     async with state.proxy() as data:
    #         data['bill'] = bill
    #     info = global_db_obj.get_payment(bill)
    #     if info:
    #         if str(config.P2P.check(bill_id=bill).status) == "PAID":
    #             user_money = performer_get_db_obj.performer_money(callback.from_user.id)
    #             money = int(info[2])
    #             performer_set_db_obj.set_money(callback.from_user.id, user_money + money)
    #             global_set_db_obj.delete_payment(bill_id=bill)
    #             await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #             await bot.send_message(callback.from_user.id,
    #                                    "Ваш счёт пополнен!\n",
    #                                    reply_markup=markup_performer.performer_profile())
    #             await state.finish()
    #             res = performer_get_db_obj.performer_exists(callback.from_user.id)
    #             if res[11] == "pedestrian":
    #                 status = "Пешеход"
    #                 icon = f"{config.KEYBOARD.get('PERSON_RUNNING')}"
    #             else:
    #                 status = "На машине"
    #                 icon = f"{config.KEYBOARD.get('AUTOMOBILE')}"
    #             await bot.send_message(callback.from_user.id,
    #                                    f"{config.KEYBOARD.get('DASH') * 14}\n"
    #                                    f"Ваш профиль <b>Исполнителя</b>:\n"
    #                                    f"{config.KEYBOARD.get('ID_BUTTON')} "
    #                                    f"Ваш ID: <b>{res[1]}</b>\n"
    #                                    f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
    #                                    f"Ваш никнейм: <b>@{res[2]}</b>\n"
    #                                    f"{config.KEYBOARD.get('TELEPHONE')} "
    #                                    f"Ваш номер: <b>{res[3]}</b>\n"
    #                                    f"{config.KEYBOARD.get('DOLLAR')} "
    #                                    f"Ваш текущий баланс: <b>{res[6]}</b> руб.\n"
    #                                    f"{config.KEYBOARD.get('BAR_CHART')} Ваш рейтинг: <b>{str(res[7])[0:5]}</b>\n"
    #                                    f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} Взял заказов: <b>{res[9]}</b>\n"
    #                                    f"{config.KEYBOARD.get('CROSS_MARK')} Отменил заказов: <b>{res[10]}</b>\n"
    #                                    f"{icon} Ваша категория: <b>{status}</b>\n"
    #                                    f"{config.KEYBOARD.get('DASH') * 14}",
    #                                    reply_markup=markup_performer.performer_profile())
    #             await performer_states.PerformerProfile.my_profile.set()
    #         else:
    #             await bot.send_message(callback.from_user.id,
    #                                    "Платёж не прошел",
    #                                    reply_markup=markup_performer.buy_menu(False, bill=bill))
    #     else:
    #         await bot.send_message(callback.from_user.id, "Счёт не найден")
    #         await state.finish()
    #
    # @staticmethod
    # async def cancel(callback: types.CallbackQuery, state: FSMContext):
    #     async with state.proxy() as data:
    #         global_set_db_obj.delete_payment(data.get('bill'))
    #     await state.finish()
    #     await bot.send_message(callback.from_user.id,
    #                            "Вы отменили пополнение баланса\n",
    #                            reply_markup=markup_performer.performer_profile())
    #     await performer_states.PerformerProfile.my_profile.set()

    @staticmethod
    def register_performer_profile(dp):
        dp.register_message_handler(PerformerProfile.performer_profile,
                                    state=performer_states.PerformerProfile.my_profile)
        # dp.register_message_handler(PerformerProfile.performer_profile_change_status,
        #                             state=performer_states.PerformerProfile.change_status)
        # dp.register_message_handler(PerformerProfile.transport,
        #                             state=performer_states.PerformerProfile.change_status_transport)
        # dp.register_message_handler(PerformerProfile.pay,
        #                             state=performer_states.PerformerProfile.pay)
        # dp.register_callback_query_handler(PerformerProfile.check,
        #                                    text_contains='check_',
        #                                    state=performer_states.PerformerProfile.pay)
        # dp.register_callback_query_handler(PerformerProfile.cancel,
        #                                    text='cancel_pay',
        #                                    state=performer_states.PerformerProfile.pay)


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
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню Исполнителя",
                                   reply_markup=markup_performer.main_menu())
        if "Подтверждаю" in message.text:
            performer_c = await performers_get.performer_select(message.from_user.id)
            performer_category = performer_c.performer_category
            async with state.proxy() as data:
                data["performer_category"] = performer_category
            if performer_category == "car":
                p_c = "Исполнителя на Машине"
            if performer_category == "scooter":
                p_c = "Исполнителя на Самокате"
            elif performer_category == "pedestrian":
                p_c = "Пешехода"
            res = await performers_get.performer_checks_all_orders(message.from_user.id, performer_category)
            await bot.send_message(message.from_user.id,
                                   f"Выводим весь список задач для <b>{p_c}</b>")
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
        if "Отмена" in message.text:
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню Исполнителя",
                                   reply_markup=markup_performer.main_menu())

    @staticmethod
    async def choose_category(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            res_category = callback.data[4:]
            res = await performers_get.performer_checks_all_orders_with_category(callback.from_user.id,
                                                                                 data.get("performer_category"),
                                                                                 res_category)
        for i in res:
            order_rating = await performers_get.performer_check_order_rating(i.order_id, callback.from_user.id)
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
                await bot.send_photo(callback.from_user.id, i.image)
                await bot.send_message(callback.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"<b>Детали заказа</b>\n"
                                       f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                       f"Категория - <b>{i.category_delivery}</b>\n"
                                       f"{config.KEYBOARD.get('A_BUTTON')} "
                                       f"Откуда - <b>{i.geo_position_from}</b>\n"
                                       f"{config.KEYBOARD.get('B_BUTTON')} "
                                       f"Куда - <b>{i.geo_position_to}</b>\n"
                                       f"{config.KEYBOARD.get('INFORMATION')} "
                                       f"Название - <b>{i.title}</b>\n"
                                       f"{config.KEYBOARD.get('CLIPBOARD')} "
                                       f"Описание - <b>{i.description}</b>\n"
                                       f"{config.KEYBOARD.get('DOLLAR')} "
                                       f"Цена - <b>{i.price}</b>\n"
                                       f"{config.KEYBOARD.get('MONEY_BAG')} "
                                       f"Ценность этого товара - <b>{i.order_worth}</b>\n"
                                       f"{icon} "
                                       f"Исполнитель - <b>{p_status}</b>\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID заказа - <b>{i.order_id}</b>\n"
                                       f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                       f"Заказ создан: <b>{i.order_create}</b>\n"
                                       f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                       f"Действует до: <b>{i.order_expired}</b>\n"
                                       f"{config.KEYBOARD.get('BAR_CHART')} "
                                       f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}\n")
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
                await bot.send_message(callback.from_user.id,
                                       f"Нажмите на ID -> `{i.order_id}` <- чтобы cкопировать",
                                       parse_mode=ParseMode.MARKDOWN)
            except:
                try:
                    await bot.send_video(callback.from_user.id, i.video)
                    await bot.send_message(callback.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                           f"Категория - <b>{i.category_delivery}</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <b>{i.geo_position_from}</b>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <b>{i.geo_position_to}</b>\n"
                                           f"{config.KEYBOARD.get('INFORMATION')} "
                                           f"Название - <b>{i.title}</b>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{i.description}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена - <b>{i.price}</b>\n"
                                           f"{config.KEYBOARD.get('MONEY_BAG')} "
                                           f"Ценность этого товара - <b>{i.order_worth}</b>\n"
                                           f"{icon} "
                                           f"Исполнитель - <b>{p_status}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <b>{i.order_id}</b>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{i.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                           f"Действует до: <b>{i.order_expired}</b>\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n")
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
                    await bot.send_message(callback.from_user.id,
                                           f"Нажмите на ID -> `{i.order_id}` <- чтобы cкопировать",
                                           parse_mode=ParseMode.MARKDOWN)
                except:
                    await bot.send_message(callback.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                           f"Категория - <b>{i.category_delivery}</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <b>{i.geo_position_from}</b>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <b>{i.geo_position_to}</b>\n"
                                           f"{config.KEYBOARD.get('INFORMATION')} "
                                           f"Название - <b>{i.title}</b>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{i.description}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена - <b>{i.price}</b>\n"
                                           f"{config.KEYBOARD.get('MONEY_BAG')} "
                                           f"Ценность этого товара - <b>{i.order_worth}</b>\n"
                                           f"{icon} "
                                           f"Исполнитель - <b>{p_status}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <b>{i.order_id}</b>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{i.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                           f"Действует до: <b>{i.order_expired}</b>\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n")
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
                    await bot.send_message(callback.from_user.id,
                                           f"Нажмите на ID -> `{i.order_id}` <- чтобы cкопировать",
                                           parse_mode=ParseMode.MARKDOWN)
        await bot.send_message(callback.from_user.id,
                               "Если хотите взять какой нибудь заказ\n"
                               "Нажмите 'Ввести ID задачи', а потом наберите ID задачи и отправьте мне",
                               reply_markup=markup_performer.get_order())

    @staticmethod
    async def get_order(message: types.Message, state: FSMContext):
        res = await performers_get.performer_view_order(message.text)
        if not res.in_work:
            async with state.proxy() as data:
                data["order_id"] = message.text
                data["price"] = res.price
            try:
                await bot.send_photo(message.from_user.id, res.image)
                await bot.send_message(message.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"<b>Детали заказа</b>\n"
                                       f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                       f"Категория - <b>{res.category_delivery}</b>\n"
                                       f"{config.KEYBOARD.get('A_BUTTON')} "
                                       f"Откуда - <b>{res.geo_position_from}</b>\n"
                                       f"{config.KEYBOARD.get('B_BUTTON')} "
                                       f"Куда - <b>{res.geo_position_to}</b>\n"
                                       f"{config.KEYBOARD.get('INFORMATION')} "
                                       f"Название - <b>{res.title}</b>\n"
                                       f"{config.KEYBOARD.get('CLIPBOARD')} "
                                       f"Описание - <b>{res.description}</b>\n"
                                       f"{config.KEYBOARD.get('DOLLAR')} "
                                       f"Цена - <b>{res.price}</b>\n"
                                       f"{config.KEYBOARD.get('MONEY_BAG')} "
                                       f"Ценность этого товара - <b>{res.order_worth}</b>\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID заказа - <b>{res.order_id}</b>\n"
                                       f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                       f"Заказ создан: <b>{res.order_create}</b>\n"
                                       f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                       f"Действует до: <b>{res.order_expired}</b>\n"
                                       f"{config.KEYBOARD.get('BAR_CHART')} "
                                       f"Рейтинг заказа | <b>{res.order_rating}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}\n")
            except:
                try:
                    await bot.send_video(message.from_user.id, res.video)
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                           f"Категория - <b>{res.category_delivery}</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <b>{res.geo_position_from}</b>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <b>{res.geo_position_to}</b>\n"
                                           f"{config.KEYBOARD.get('INFORMATION')} "
                                           f"Название - <b>{res.title}</b>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{res.description}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена - <b>{res.price}</b>\n"
                                           f"{config.KEYBOARD.get('MONEY_BAG')} "
                                           f"Ценность этого товара - <b>{res.order_worth}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <b>{res.order_id}</b>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{res.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                           f"Действует до: <b>{res.order_expired}</b>\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{res.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n")
                except:
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                           f"Категория - <b>{res.category_delivery}</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <b>{res.geo_position_from}</b>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <b>{res.geo_position_to}</b>\n"
                                           f"{config.KEYBOARD.get('INFORMATION')} "
                                           f"Название - <b>{res.title}</b>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{res.description}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена - <b>{res.price}</b>\n"
                                           f"{config.KEYBOARD.get('MONEY_BAG')} "
                                           f"Ценность этого товара - <b>{res.order_worth}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <b>{res.order_id}</b>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{res.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                           f"Действует до: <b>{res.order_expired}</b>\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{res.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n")
            await bot.send_message(message.from_user.id,
                                   "Вы хотите взять эту задачу ?",
                                   reply_markup=markup_performer.inline_approve())
            await performer_states.PerformerTasks.approve_or_decline.set()
        else:
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Заказа не существует! или его уже кто то взял!",
                                   reply_markup=markup_performer.main_menu())

    @staticmethod
    async def order_request(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            customer_id = await performers_get.performer_checks_customer_user_id(data['order_id'])
            performer = await performers_get.performer_select(callback.from_user.id)
        """Здесь надо придумать как оповестить по СМС заказчику о том что его заказ хотят взять"""
        await bot.send_message(customer_id, f"Ваш заказ <b>{data['order_id']}</b> хочет взять Исполнитель!\n"
                                            f"Его рейтинг - <b>{str(performer.performer_rating)[0:5]}</b>\n"
                                            f"Никнейм - <b>@{callback.from_user.username}</b>\n"
                                            f"Имя - <b>{callback.from_user.first_name}</b>\n"
                                            f"Фамилия - <b>{callback.from_user.last_name}</b>\n"
                                            f"ID Исполнителя - <b>{callback.from_user.id}</b>",
                               reply_markup=markup_performer.inline_approve_main())
        await performer_states.PerformerStart.performer_menu.set()
        await bot.send_message(callback.from_user.id,
                               f"Отклик отправлен! Ожидайте ответа Заказчика",
                               reply_markup=markup_performer.main_menu())

    @staticmethod
    async def approve_order(callback: types.CallbackQuery):
        order_id = callback.message.text.split()[8]
        customer_id = callback.message.text.split()[2]
        await performers_set.performer_set_order(callback.from_user.id,
                                                 order_id,
                                                 datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(customer_id,
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 8}\n"
                               f"Ваш заказ {order_id} взят Исполнителем {callback.from_user.id}\n"
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 8}\n")
        await bot.send_message(callback.from_user.id,
                               'Вы взяли задачу!',
                               reply_markup=markup_performer.main_menu())
        await performer_states.PerformerStart.performer_menu.set()

    @staticmethod
    async def approve_order_with_new_price(callback: types.CallbackQuery):
        res = callback.message.text.split()
        order_id, customer_id, new_price = res[12], res[2], res[9]
        await performers_set.performer_set_order(callback.from_user.id,
                                                 order_id,
                                                 datetime.now().strftime('%d-%m-%Y, %H:%M:%S'))
        await performers_set.add_new_price(order_id, new_price)
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(customer_id,
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 8}\n"
                               f"Ваш заказ {order_id} взят Исполнителем {callback.from_user.id}"
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 8}\n")
        await bot.send_message(callback.from_user.id,
                               'Вы взяли задачу!',
                               reply_markup=markup_performer.main_menu())
        await performer_states.PerformerStart.performer_menu.set()

    @staticmethod
    async def decline_order(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               'Вы отказались от задачи',
                               reply_markup=markup_performer.main_menu())
        await performer_states.PerformerStart.performer_menu.set()

    @staticmethod
    async def proposal(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Введите цену",
                               reply_markup=markup_performer.markup_clean)
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
                                   f"Предложение новой цены {message.text} от Исполнителя {message.from_user.id} "
                                   f"на ваш заказ {data.get('order_id')}\n"
                                   f"Ваша цена заказа - {data.get('price')}\n"
                                   f"{config.KEYBOARD.get('DOLLAR') * 10}\n",
                                   reply_markup=markup_performer.inline_approve_proposal())
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(message.from_user.id,
                                   f"Отклик отправлен! Ожидайте ответа Заказчика",
                                   reply_markup=markup_performer.main_menu())
        else:
            await bot.send_message(message.from_user.id, "Надо ввести целое число!")

    # @staticmethod
    # async def order_rating_plus(callback: types.CallbackQuery):
    #     await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #     global_set_db_obj.order_rating_change_plus(callback.data[5:])
    #     performer_set_db_obj.performer_set_order_rating(callback.data[5:], 1, callback.from_user.id)
    #     await bot.send_message(callback.from_user.id,
    #                            f"Вы поставили лайк заказу <b>{callback.data[5:]}</b>")
    #
    # @staticmethod
    # async def order_rating_minus(callback: types.CallbackQuery):
    #     await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #     global_set_db_obj.order_rating_change_minus(callback.data[6:])
    #     performer_set_db_obj.performer_set_order_rating(callback.data[6:], -1, callback.from_user.id)
    #     await bot.send_message(callback.from_user.id,
    #                            f"Вы поставили дизлайк заказу <b>{callback.data[6:]}</b>")

    @staticmethod
    def register_performer_tasks(dp: Dispatcher):
        dp.register_message_handler(PerformerTasks.check_all_orders,
                                    state=performer_states.PerformerTasks.check_all_orders)
        dp.register_message_handler(PerformerTasks.get_order,
                                    state=performer_states.PerformerTasks.get_order)
        dp.register_callback_query_handler(PerformerTasks.order_request,
                                           state=performer_states.PerformerTasks.approve_or_decline,
                                           text='performer_request')
        dp.register_callback_query_handler(PerformerTasks.approve_order, state=["*"],
                                           text='performer_get')
        dp.register_callback_query_handler(PerformerTasks.decline_order,
                                           state=["*"],
                                           text='performer_decline')
        dp.register_callback_query_handler(PerformerTasks.proposal,
                                           state=performer_states.PerformerTasks.approve_or_decline,
                                           text='performer_proposal')
        dp.register_message_handler(PerformerTasks.proposal_price,
                                    state=performer_states.PerformerTasks.proposal)
        dp.register_callback_query_handler(PerformerTasks.approve_order_with_new_price,
                                           state=["*"],
                                           text='performer_get_with_new_price')
        dp.register_callback_query_handler(PerformerTasks.choose_category,
                                           state=performer_states.PerformerTasks.check_all_orders,
                                           text_contains="cat_")
        # dp.register_callback_query_handler(PerformerTasks.order_rating_plus,
        #                                    state=performer_states.PerformerTasks.check_all_orders,
        #                                    text_contains="plus_")
        # dp.register_callback_query_handler(PerformerTasks.order_rating_minus,
        #                                    state=performer_states.PerformerTasks.check_all_orders,
        #                                    text_contains="minus_")


class PerformerDetailsTasks:
    @staticmethod
    async def performer_details(message: types.Message, state: FSMContext):
        if "Вернуться в главное меню" in message.text:
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_performer.main_menu())
        try:
            res = await performers_get.performer_view_list_orders(message.from_user.id)
            async with state.proxy() as data:
                try:
                    msg = message.text.split()[1]
                    data["order_id"] = msg
                    data["user_id"] = await performers_get.performer_checks_customer_user_id(msg)
                except IndexError:
                    await bot.send_message(message.from_user.id,
                                           "Откройте клавиатуру и нажмите на ID вашего заказа")
            for i in res:
                try:
                    if i.order_id == msg:
                        await performer_states.PerformerDetailsTasks.enter_task.set()
                        await bot.send_message(message.from_user.id,
                                               "Вы вошли в детали этого заказа",
                                               reply_markup=markup_performer.details_task())
                except UnboundLocalError:
                    pass
        except TypeError:
            pass

    @staticmethod
    async def detail_task(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            res_order = await performers_get.performer_view_order(data.get("order_id"))
            res_customer = await customers_get.customer_select(data.get("user_id"))
        if "Позвонить/написать заказчику" in message.text:
            res = await performers_get.performer_get_status_order(data.get("order_id"))
            if res is None:
                await performer_states.PerformerStart.performer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись в главное меню",
                                       reply_markup=markup_performer.main_menu())
            else:
                await bot.send_message(message.from_user.id,
                                       f"Вот его номер телефона {res_customer.telephone}\n"
                                       f"Или напишите ему в телеграм @{res_customer.username}")
        if "Детали заказа" in message.text:
            res = await performers_get.performer_get_status_order(data.get("order_id"))
            if res is None:
                await performer_states.PerformerStart.performer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись в главное меню",
                                       reply_markup=markup_performer.main_menu())
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
                                           f"Откуда - <b>{res_order.geo_position_from}</b>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <b>{res_order.geo_position_to}</b>\n"
                                           f"{config.KEYBOARD.get('INFORMATION')} "
                                           f"Название - <b>{res_order.title}</b>\n"
                                           f"{config.KEYBOARD.get('CLIPBOARD')} "
                                           f"Описание - <b>{res_order.description}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} "
                                           f"Цена - <b>{res_order.price}</b>\n"
                                           f"{config.KEYBOARD.get('MONEY_BAG')} "
                                           f"Ценность этого товара - <b>{res_order.order_worth}</b>\n"
                                           f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                           f"Заказ создан: <b>{res_order.order_create}</b>\n"
                                           f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                           f"Действует до: <b>{res_order.order_expired}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n")
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
                                               f"Откуда - <b>{res_order.geo_position_from}</b>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <b>{res_order.geo_position_to}</b>\n"
                                               f"{config.KEYBOARD.get('INFORMATION')} "
                                               f"Название - <b>{res_order.title}</b>\n"
                                               f"{config.KEYBOARD.get('CLIPBOARD')} "
                                               f"Описание - <b>{res_order.description}</b>\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} "
                                               f"Цена - <b>{res_order.price}</b>\n"
                                               f"{config.KEYBOARD.get('MONEY_BAG')} "
                                               f"Ценность этого товара - <b>{res_order.order_worth}</b>\n"
                                               f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                               f"Заказ создан: <b>{res_order.order_create}</b>\n"
                                               f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                               f"Действует до: <b>{res_order.order_expired}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}\n")
                    except:
                        await bot.send_message(message.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"<b>Детали заказа</b>\n"
                                               f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                               f"Категория - <b>{res_order.category_delivery}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID заказа - <b>{res_order.order_id}</b>\n"
                                               f"{config.KEYBOARD.get('A_BUTTON')} "
                                               f"Откуда - <b>{res_order.geo_position_from}</b>\n"
                                               f"{config.KEYBOARD.get('B_BUTTON')} "
                                               f"Куда - <b>{res_order.geo_position_to}</b>\n"
                                               f"{config.KEYBOARD.get('INFORMATION')} "
                                               f"Название - <b>{res_order.title}</b>\n"
                                               f"{config.KEYBOARD.get('CLIPBOARD')} "
                                               f"Описание - <b>{res_order.description}</b>\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} "
                                               f"Цена - <b>{res_order.price}</b>\n"
                                               f"{config.KEYBOARD.get('MONEY_BAG')} "
                                               f"Ценность этого товара - <b>{res_order.order_worth}</b>\n"
                                               f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                               f"Заказ создан: <b>{res_order.order_create}</b>\n"
                                               f"{config.KEYBOARD.get('RED_CIRCLE')} "
                                               f"Действует до: <b>{res_order.order_expired}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}\n")
        if "Статус заказа" in message.text:
            res = await performers_get.performer_get_status_order(data.get("order_id"))
            if res is None:
                await performer_states.PerformerStart.performer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись в главное меню",
                                       reply_markup=markup_performer.main_menu())
            else:
                await bot.send_message(message.from_user.id,
                                       "Вы вошли в статус заказа, тут вы можете отменить заказ, "
                                       "Завершить заказ или проверить статус заказа для его закрытия",
                                       reply_markup=markup_performer.details_task_status())
                await performer_states.PerformerDetailsTasksStatus.enter_status.set()
                PerformerDetailsTasksStatus.register_performer_details_tasks_status(dp)
        if "Профиль заказчика" in message.text:
            res = await performers_get.performer_get_status_order(data.get("order_id"))
            if res is None:
                await performer_states.PerformerStart.performer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись в главное меню",
                                       reply_markup=markup_performer.main_menu())
            else:
                await bot.send_message(message.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"Профиль <b>Заказчика</b>:\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID : <b>{res_customer.user_id}</b>\n"
                                       f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                       f"Никнейм <b>@{res_customer.username}</b>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Номер <b>{res_customer.telephone}</b>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Имя <b>{res_customer.first_name}</b>\n"
                                       f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                       f"Фамилия <b>{res_customer.last_name}</b>\n"
                                       f"{config.KEYBOARD.get('BAR_CHART')} "
                                       f"Рейтинг <b>{str(res_customer.customer_rating)[0:5]}</b>\n"
                                       f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                       f"Заказов создал - <b>{res_customer.create_orders}</b>\n"
                                       f"{config.KEYBOARD.get('CROSS_MARK')} "
                                       f"Заказов отменил - <b>{res_customer.canceled_orders}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}")
        if "Вернуться в главное меню" in message.text:
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_performer.main_menu())

    #     @staticmethod
    #     async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    #         async with state.proxy() as data:
    #             performer_set_db_obj.performer_cancel_order(data.get('order_id'))
    #         await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #         await performer_states.PerformerStart.performer_menu.set()
    #         await bot.send_message(callback.from_user.id,
    #                                "Вы отменили заказ!",
    #                                reply_markup=markup_performer.main_menu())
    #
    #     @staticmethod
    #     async def no_cancel(callback: types.CallbackQuery):
    #         await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #         await bot.send_message(callback.from_user.id,
    #                                "Отлично надеюсь вы сделаете свою работу",
    #                                reply_markup=markup_performer.details_task())
    #
    #     @staticmethod
    #     async def close_order(callback: types.CallbackQuery, state: FSMContext):
    #         await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #         async with state.proxy() as data:
    #             performer_set_db_obj.performer_set_order_status(data.get('order_id'))
    #         await bot.send_message(callback.from_user.id,
    #                                "Отлично! Вы установили статус заказа завершенным")
    #         await bot.send_message(callback.from_user.id,
    #                                "Оцените заказчика",
    #                                reply_markup=markup_performer.rating())
    #
    #     @staticmethod
    #     async def no_close(callback: types.CallbackQuery):
    #         await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #         await bot.send_message(callback.from_user.id,
    #                                "Сделайте до конца, а потом завершайте",
    #                                reply_markup=markup_performer.details_task())

    @staticmethod
    def register_performer_details_tasks(dp):
        dp.register_message_handler(PerformerDetailsTasks.performer_details,
                                    state=performer_states.PerformerDetailsTasks.details_tasks)
        dp.register_message_handler(PerformerDetailsTasks.detail_task,
                                    state=performer_states.PerformerDetailsTasks.enter_task)
        # dp.register_callback_query_handler(PerformerDetailsTasks.cancel_order, text="cancel_order",
        #                                    state=performer_states.PerformerDetailsTasks.enter_task)
        # dp.register_callback_query_handler(PerformerDetailsTasks.no_cancel, text="no_cancel",
        #                                    state=performer_states.PerformerDetailsTasks.enter_task)
        # dp.register_callback_query_handler(PerformerDetailsTasks.close_order, text="close_order",
        #                                    state=performer_states.PerformerDetailsTasks.enter_task)
        # dp.register_callback_query_handler(PerformerDetailsTasks.no_close, text="no_close",
        #                                    state=performer_states.PerformerDetailsTasks.enter_task)


class PerformerDetailsTasksStatus:
    @staticmethod
    async def details_status(message: types.Message, state: FSMContext):
        if "Отменить заказ" in message.text:
            async with state.proxy() as data:
                status = await general_get.check_details_status(data.get("order_id"))
            if status is None:
                await bot.send_message(message.from_user.id,
                                       "Заказ закрыт",
                                       reply_markup=markup_performer.main_menu())
                await performer_states.PerformerStart.performer_menu.set()
            if status:
                if status.performer_status:
                    await bot.send_message(message.from_user.id,
                                           "Вы уже не сможете отменить заказ так как вы его завершили",
                                           reply_markup=markup_performer.details_task_status())
                    await performer_states.PerformerDetailsTasksStatus.enter_status.set()
                else:
                    await bot.send_message(message.from_user.id,
                                           "Вы хотите отменить заказ ?\n"
                                           "С вас спишется 10% от стоимости заказа",
                                           reply_markup=markup_performer.inline_cancel_task())
        if "Завершить заказ" in message.text:
            async with state.proxy() as data:
                status = await general_get.check_details_status(data.get("order_id"))
            if status is None:
                await bot.send_message(message.from_user.id,
                                       "Заказ закрыт",
                                       reply_markup=markup_performer.main_menu())
                await performer_states.PerformerStart.performer_menu.set()
            if status:
                if status.performer_status:
                    await bot.send_message(message.from_user.id,
                                           "Вы уже завершали заказ",
                                           reply_markup=markup_performer.details_task_status())
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
                                       "Заказ закрыт",
                                       reply_markup=markup_performer.main_menu())
                await performer_states.PerformerStart.performer_menu.set()
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
            commission = price / 10
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
                               "Вы отменили заказ!",
                               reply_markup=markup_performer.main_menu())

    @staticmethod
    async def no_cancel_order(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Хорошо что передумали, заказ будет сделан!",
                               reply_markup=markup_performer.details_task_status())

    @staticmethod
    async def close_order(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 14}")
            await bot.send_message(data.get("user_id"),
                                   f"Ваша задача <b>{data.get('order_id')}</b> "
                                   f"была помечена исполнителем как ВЫПОЛНЕННАЯ!\n"
                                   f"Посмотрите в разделе 'Проверить статус заказа'"
                                   f"Если Заказчик и Исполнитель завершили заказ, "
                                   f"то заказ будет перемещен в раздел ВЫПОЛНЕННЫЕ")
            await bot.send_message(data.get("user_id"),
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 14}")
            await performers_set.performer_set_order_status(data.get("order_id"))
        await bot.send_message(callback.from_user.id,
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 14}")
        await bot.send_message(callback.from_user.id,
                               "Отлично! Вы установили статус заказа завершенным")
        await bot.send_message(callback.from_user.id,
                               f"{config.KEYBOARD.get('CHECK_MARK_BUTTON') * 14}")
        await bot.send_message(callback.from_user.id,
                               "Оцените заказчика",
                               reply_markup=markup_performer.rating())
        await performer_states.PerformerDetailsTasksStatus.rating.set()

    @staticmethod
    async def no_close(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id,
                               "Сделайте до конца, а потом завершайте",
                               reply_markup=markup_performer.details_task_status())

    @staticmethod
    async def rating(message: types.Message, state: FSMContext):
        rate = ['1', '2', '3', '4', '5']
        if message.text in rate:
            async with state.proxy() as data:
                await performers_set.performer_set_rating_to_customer(data.get("user_id"),
                                                                      message.text)
                await performers_set.performer_set_rating_to_customer_in_review_db(data.get("order_id"), message.text)
            await bot.send_message(message.from_user.id,
                                   f"Вы поставили оценку Заказчику - <b>{message.text}</b>\n"
                                   f"Спасибо за оценку!"
                                   f"Вы можете оставить отзыв, или войти в детали заказа",
                                   reply_markup=markup_performer.details_task_status_review())
            await performer_states.PerformerDetailsTasksStatus.review.set()
        else:
            await bot.send_message(message.from_user.id, "Надо поставить оценку 1,2,3,4,5")

    @staticmethod
    async def review(message: types.Message, state: FSMContext):
        if "Войти в детали заказа" in message.text:
            await bot.send_message(message.from_user.id,
                                   "Вы вошли в детали заказа",
                                   reply_markup=markup_performer.details_task_status())
            await performer_states.PerformerDetailsTasksStatus.enter_status.set()
        else:
            async with state.proxy() as data:
                await performers_set.performer_set_review_to_customer_in_review_db(data.get("order_id"),
                                                                                   message.text)
                await bot.send_message(message.from_user.id,
                                       "Отзыв отправлен!",
                                       reply_markup=markup_performer.details_task_status())
                await performer_states.PerformerDetailsTasksStatus.enter_status.set()

    @staticmethod
    def register_performer_details_tasks_status(dp):
        dp.register_message_handler(PerformerDetailsTasksStatus.details_status,
                                    state=performer_states.PerformerDetailsTasksStatus.enter_status)
        dp.register_callback_query_handler(PerformerDetailsTasksStatus.cancel_order,
                                           text="cancel",
                                           state=performer_states.PerformerDetailsTasksStatus.enter_status)
        dp.register_callback_query_handler(PerformerDetailsTasksStatus.no_cancel_order,
                                           text="no_cancel",
                                           state=performer_states.PerformerDetailsTasksStatus.enter_status)
        dp.register_callback_query_handler(PerformerDetailsTasksStatus.close_order,
                                           text="close_order",
                                           state=performer_states.PerformerDetailsTasksStatus.enter_status)
        dp.register_callback_query_handler(PerformerDetailsTasksStatus.no_close,
                                           text="no_close",
                                           state=performer_states.PerformerDetailsTasksStatus.enter_status)
        dp.register_message_handler(PerformerDetailsTasksStatus.rating,
                                    state=performer_states.PerformerDetailsTasksStatus.rating)
        dp.register_message_handler(PerformerDetailsTasksStatus.review,
                                    state=performer_states.PerformerDetailsTasksStatus.review)


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
                                   "Все сообщения в службу поддержки отправлены!",
                                   reply_markup=markup_performer.main_menu())
            await performer_states.PerformerStart.performer_menu.set()
        if message.text == "Вернуться главное меню":
            await bot.send_message(message.from_user.id,
                                   "Вы вошли в главное меню заказчика",
                                   reply_markup=markup_performer.main_menu())
            await performer_states.PerformerStart.performer_menu.set()
        if message.text != "Загрузить Фото" and message.text != "Загрузить Видео" \
                and message.text != "Завершить" and message.text != "Вернуться главное меню" \
                and message.text != "Закрытый чат курьеров":
            await bot.send_message('@delivery_kerka_dev',
                                   f"Имя исполнителя {message.from_user.first_name}\n"
                                   f"ID исполнителя {message.from_user.id}\n"
                                   f"Сообщение от исполнителя - <b>{message.text}</b>\n")
            await bot.send_message(message.from_user.id, "Сообщение досталено в техподдержку!")

    @staticmethod
    async def performer_upload_photo(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            user_status_chat = data.get("user_status_chat")
        PerformerHelp.logger.debug(f"Функция отправки фото от исполнителя {message.from_user.id} в тех поддержку")
        if message.content_type == "photo":
            await bot.send_message('@delivery_kerka_dev',
                                   f"Имя исполнителя {message.from_user.first_name}\n"
                                   f"ID исполнителя {message.from_user.id}\n"
                                   f"Фото исполнителя {config.KEYBOARD.get('DOWNWARDS_BUTTON')}")
            await bot.send_photo('@delivery_kerka_dev',
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
            await bot.send_message('@delivery_kerka_dev',
                                   f"Имя исполнителя {message.from_user.first_name}\n"
                                   f"ID исполнителя {message.from_user.id}\n"
                                   f"Видео исполнителя {config.KEYBOARD.get('DOWNWARDS_BUTTON')}")
            await bot.send_video('@delivery_kerka_dev',
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

    # @staticmethod
    # async def performer_private_chat(callback: types.CallbackQuery):
    #     await bot.delete_message(callback.from_user.id, callback.message.message_id)
    #     global_set_db_obj.private_chat_money(callback.from_user.id)
    #     res = performer_get_db_obj.performer_exists(callback.from_user.id)
    #     await bot.send_message(callback.from_user.id,
    #                            "<b>С вас списалось 300 рублей!</b>")
    #     # await bot.send_message('@delivery_kerka_dev',
    #     #                        f"{config.KEYBOARD.get('DOLLAR') * 10}\n"
    #     #                        f"<b>Вступил в закрытый чат:</b>\n"
    #     #                        f"Имя исполнителя {callback.from_user.first_name}\n"
    #     #                        f"ID исполнителя {callback.from_user.id}\n"
    #     #                        f"Username @{res[2]}\n"
    #     #                        f"Телефон {res[3]}\n"
    #     #                        f"{config.KEYBOARD.get('DOLLAR') * 10}")
    #     await bot.send_message(callback.from_user.id,
    #                            "<b>Перейдите по ссылке ниже</b>\n"
    #                            "https://t.me/+XjgtXkbTgKA4YzZi")

    @staticmethod
    def register_performer_help(dp: Dispatcher):
        dp.register_message_handler(PerformerHelp.performer_help,
                                    content_types=['text'],
                                    state=performer_states.PerformerHelp.help)
        dp.register_message_handler(PerformerHelp.performer_upload_photo,
                                    content_types=['photo', 'text'],
                                    state=performer_states.PerformerHelp.upload_photo)
        dp.register_message_handler(PerformerHelp.performer_upload_video,
                                    content_types=['video', 'text'],
                                    state=performer_states.PerformerHelp.upload_video)
        # dp.register_callback_query_handler(PerformerHelp.performer_private_chat,
        #                                    text='private_chat',
        #                                    state=performer_states.PerformerHelp.help)
#
#
# class PerformerHistory:
#     @staticmethod
#     async def history(message: types.Message, state: FSMContext):
#         if "Вернуться в главное меню" in message.text:
#             await performer_states.PerformerStart.performer_menu.set()
#             await bot.send_message(message.from_user.id,
#                                    "Вы вернулись в главное меню",
#                                    reply_markup=markup_performer.main_menu())
#         else:
#             completed = performer_get_db_obj.performer_get_complete_order(message.text)
#             async with state.proxy() as data:
#                 data["order_id"] = completed[11]
#                 data[completed[11]] = completed
#             await performer_states.PerformerHistory.order_history.set()
#             await bot.send_message(message.from_user.id,
#                                    "Вы вошли в исторю заказа",
#                                    reply_markup=markup_performer.details_task_history())
#
#     @staticmethod
#     async def order_history(message: types.Message, state: FSMContext):
#         async with state.proxy() as data:
#             order = data.get(data.get("order_id"))
#         customer_res = customer_get_db_obj.customer_exists(order[1])
#         if "Позвонить Заказчику" in message.text:
#             await bot.send_message(message.from_user.id,
#                                    f"Позвоните заказчику {customer_res[3]}")
#         if "Написать Заказчику" in message.text:
#             await bot.send_message(message.from_user.id,
#                                    f"Напишите через телеграмм вот его никнейм @{customer_res[2]}")
#         if "Посмотреть детали заказа" in message.text:
#             await performer_states.PerformerHistory.order_history_details.set()
#             await bot.send_message(message.from_user.id,
#                                    f"{config.KEYBOARD.get('DASH') * 14}\n"
#                                    f"<b>Детали заказа</b>\n"
#                                    f"{config.KEYBOARD.get('ID_BUTTON')} "
#                                    f"ID заказа <b>{order[11]}</b>\n"
#                                    f"{config.KEYBOARD.get('A_BUTTON')} "
#                                    f"Откуда <b>{order[2]}</b>\n"
#                                    f"{config.KEYBOARD.get('B_BUTTON')} "
#                                    f"Куда <b>{order[3]}</b>\n"
#                                    f"{config.KEYBOARD.get('INFORMATION')} "
#                                    f"Название <b>{order[4]}</b>\n"
#                                    f"{config.KEYBOARD.get('CLIPBOARD')} "
#                                    f"Описание <b>{order[6]}</b>\n"
#                                    f"{config.KEYBOARD.get('DOLLAR')} "
#                                    f"Цена <b>{order[5]}</b>\n"
#                                    f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
#                                    f"Создан <b>{order[12]}</b>\n"
#                                    f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
#                                    f"Взят <b>{order[13]}</b>\n"
#                                    f"{config.KEYBOARD.get('BLUE_CIRCLE')} "
#                                    f"Завершен <b>{order[15]}</b>\n"
#                                    f"{config.KEYBOARD.get('DASH') * 14}\n",
#                                    reply_markup=markup_performer.details_task_history_details_order())
#         if "Профиль Заказчика" in message.text:
#             await bot.send_message(message.from_user.id,
#                                    f"{config.KEYBOARD.get('DASH') * 14}\n"
#                                    f"Профиль <b>Заказчика</b>:\n"
#                                    f"{config.KEYBOARD.get('ID_BUTTON')} "
#                                    f"ID : <b>{customer_res[1]}</b>\n"
#                                    f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
#                                    f"Никнейм <b>@{customer_res[2]}</b>\n"
#                                    f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
#                                    f"Номер <b>{customer_res[3]}</b>\n"
#                                    f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
#                                    f"Имя <b>{customer_res[4]}</b>\n"
#                                    f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
#                                    f"Фамилия <b>{customer_res[5]}</b>\n"
#                                    f"{config.KEYBOARD.get('BAR_CHART')} "
#                                    f"Рейтинг <b>"
#                                    f"{str(customer_res[7])[0:5]}</b>\n"
#                                    f"{config.KEYBOARD.get('DASH') * 14}",
#                                    )
#         if "Вернуться в главное меню" in message.text:
#             await performer_states.PerformerStart.performer_menu.set()
#             await bot.send_message(message.from_user.id,
#                                    "Вы вернулись в главное меню",
#                                    reply_markup=markup_performer.main_menu())
#
#     @staticmethod
#     async def order_details(message: types.Message, state: FSMContext):
#         async with state.proxy() as data:
#             order = data.get(data.get("order_id"))
#         if "Посмотреть фото" in message.text:
#             try:
#                 await bot.send_photo(message.from_user.id, order[7])
#             except:
#                 await bot.send_message(message.from_user.id, "В этом заказе нет фото")
#         if "Посмотреть видео" in message.text:
#             try:
#                 await bot.send_video(message.from_user.id, order[8])
#             except:
#                 await bot.send_message(message.from_user.id, "В этом заказе нет видео")
#         if "Назад в детали заказа" in message.text:
#             await performer_states.PerformerHistory.order_history.set()
#             await bot.send_message(message.from_user.id,
#                                    "Вы вернулись в детали заказа",
#                                    reply_markup=markup_performer.details_task_history())
#
#     @staticmethod
#     def register_performer_history(dp):
#         dp.register_message_handler(PerformerHistory.history, state=performer_states.PerformerHistory.enter_history)
#         dp.register_message_handler(PerformerHistory.order_history,
#                                     state=performer_states.PerformerHistory.order_history)
#         dp.register_message_handler(PerformerHistory.order_details,
#                                     state=performer_states.PerformerHistory.order_history_details)