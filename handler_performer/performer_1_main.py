import calendar
from collections import Counter
from datetime import datetime, timedelta
from random import randint
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from data.commands import performers_get, performers_set, general_get, general_set
from markups import markup_performer
from settings import config
from states import performer_states


class PerformerMain:
    @staticmethod
    async def hi_performer(callback: types.CallbackQuery, state: FSMContext):
        performer = await performers_get.performer_select(callback.from_user.id)
        performer_p_d = await performers_get.performer_select_personal_data(callback.from_user.id)
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
        elif performer_p_d:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await performer_states.PerformerStart.performer_menu.set()
            await bot.send_message(callback.from_user.id,
                                   "Спасибо что пользуетесь нашим ботом!")
            orders = await performers_get.performer_view_list_orders(callback.from_user.id)
            orders_loading = await performers_get.performer_loader_order(callback.from_user.id)
            promo = await performers_get.check_commission_promo(callback.from_user.id)
            await bot.send_message(callback.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu())
        elif performer_p_d is None:
            await performer_states.PerformerStart.info_about_performer.set()
            await bot.send_message(callback.from_user.id,
                                   f"{callback.from_user.first_name} Спасибо что пользуетесь нашим ботом!\n"
                                   f"Теперь пройдите короткую регистрацию")
            async with state.proxy() as data:
                data["list_info"] = []
            await bot.send_message(callback.from_user.id,
                                   "Введите Ваше реальное Имя\n"
                                   "Вводить только на русском языке.\n",
                                   reply_markup=markup_performer.markup_clean)
        else:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await bot.send_message(callback.from_user.id, "Вы заблокированы! Обратитесь в техподдержку!")

    @staticmethod
    async def phone(message: types.Message, state: FSMContext):
        if message.contact.user_id == message.from_user.id:
            res = message.contact.phone_number[-10:]
            await performers_set.performer_add(message.from_user.id,
                                               message.from_user.username,
                                               f'+7{res}',
                                               message.from_user.first_name,
                                               message.from_user.last_name)
            await performer_states.PerformerStart.info_about_performer.set()
            await bot.send_message(message.from_user.id,
                                   f"{message.from_user.first_name} Спасибо что пользуетесь нашим ботом!\n"
                                   f"Теперь пройдите короткую регистрацию")
            async with state.proxy() as data:
                data["list_info"] = []
            await bot.send_message(message.from_user.id,
                                   "Введите Ваше реальное Имя\n"
                                   "Вводить только на русском языке.\n",
                                   reply_markup=markup_performer.markup_clean)
        else:
            await bot.send_message(message.from_user.id,
                                   "Это не ваш номер телефона! \n"
                                   "Нажмите /start чтобы начать заново")

    @staticmethod
    async def info_about_performer_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.photo:
                data.get("list_info").append(message.photo[2].file_id)
            if not message.photo:
                data.get("list_info").append(message.text)
            if len(data.get("list_info")) == 1:
                await bot.send_message(message.from_user.id,
                                       "Введите вашу Фамилию\n"
                                       "Вводить только на русском языке.\n")
            if len(data.get("list_info")) == 2:
                await bot.send_message(message.from_user.id,
                                       "Сделайте селфи")
            if len(data.get("list_info")) == 3:
                await bot.send_message(message.from_user.id,
                                       "Все получилось!")
                performer = await performers_get.performer_select(message.from_user.id)
                await performers_set.performer_add_personal_data(message.from_user.id,
                                                                 performer.telephone,
                                                                 data.get("list_info")[0],
                                                                 data.get("list_info")[1],
                                                                 data.get("list_info")[2],)
                await performer_states.PerformerStart.performer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "Регистрация завершена!\n"
                                       "Вы находитесь в главном меню!",
                                       reply_markup=markup_performer.main_menu())

    @staticmethod
    async def main(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f"{message.from_user.first_name} Вы в главном меню Исполнителя")
        orders = await performers_get.performer_view_list_orders(message.from_user.id)
        orders_loading = await performers_get.performer_loader_order(message.from_user.id)
        promo = await performers_get.check_commission_promo(message.from_user.id)
        await bot.send_message(message.from_user.id,
                               f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                               reply_markup=markup_performer.main_menu())
        await performer_states.PerformerStart.performer_menu.set()

    @staticmethod
    async def performer_menu(message: types.Message, state: FSMContext):
        await state.finish()
        if "Мой профиль" in message.text:
            res = await performers_get.performer_select(message.from_user.id)
            status = None
            icon = None
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
            auto_send = await performers_get.performer_auto_send_check(message.from_user.id)
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
                                   f"{config.KEYBOARD.get('STAR')} "
                                   f"Ваш рейтинг: <b>{res.performer_rating}</b>\n"
                                   f"{icon} Ваша категория: <b>{status}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   reply_markup=markup_performer.performer_profile(auto_send))
        if "Доступные Задачи" in message.text:
            performer = await performers_get.performer_select(message.from_user.id)
            performer_money = performer.performer_money
            if performer_money < 50:
                await performer_states.PerformerProfile.my_profile.set()
                auto_send = await performers_get.performer_auto_send_check(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       "<b>Баланс должен быть не ниже 50 рублей!</b>\n"
                                       "<b>Пополните ваш баланс</b>",
                                       reply_markup=markup_performer.performer_profile(auto_send))
            if performer_money >= 50:
                await performer_states.PerformerTasks.check_all_orders.set()
                await bot.send_message(message.from_user.id,
                                       "Выберите тип Заказа",
                                       reply_markup=markup_performer.approve())
        if "Задачи в работе" in message.text:
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   "Выберите тип заказа",
                                   reply_markup=markup_performer.performer_type_orders(orders, orders_loading))
            await performer_states.PerformerStart.orders.set()
        if "Выполненные Задачи" in message.text:
            res = await performers_get.performer_all_completed_orders(message.from_user.id)
            if res:
                finished_orders = InlineKeyboardMarkup()
                year = []
                for i in res:
                    year.append(datetime.strptime(i.order_end, '%d-%m-%Y, %H:%M:%S').year)
                res_years = Counter(year)
                for k, v in res_years.items():
                    finished_orders.insert(InlineKeyboardButton(text=f"{k} ({v})",
                                                                callback_data=f"p_year_finish_{k}"))
                await bot.send_message(message.from_user.id,
                                       "<b>Выберите год</b>\n"
                                       "В скобках указано количество завершенных заказов",
                                       reply_markup=finished_orders)
                await performer_states.PerformerStart.performer_menu.set()
            else:
                await performer_states.PerformerStart.performer_menu.set()
                await bot.send_message(message.from_user.id,
                                       "У вас еще нет завершенных заказов!")
        if "Помощь" in message.text:
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
        if "Смены" in message.text:
            await performer_states.PerformerJobsOffers.enter.set()
            await bot.send_message(message.from_user.id,
                                   "Выберите нужную смену",
                                   reply_markup=markup_performer.jobs_offers())

    @staticmethod
    async def orders(message: types.Message):
        if "Заказы Доставки" in message.text:
            res = await performers_get.performer_view_list_orders(message.from_user.id)
            if res:
                await performer_states.PerformerDetailsTasks.details_tasks.set()
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for i in res:
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
                        await bot.send_photo(message.from_user.id, i.image)
                    if i.video:
                        await bot.send_video(message.from_user.id, i.video)
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"<b>Детали заказа</b>\n"
                                           f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                           f"Категория - <b>{i.category_delivery}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID заказа - <b>{i.order_id}</b>\n"
                                           f"{config.KEYBOARD.get('A_BUTTON')} "
                                           f"Откуда - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                           f"{config.KEYBOARD.get('B_BUTTON')} "
                                           f"Куда - <a href='https://yandex.ru/maps/?text="
                                           f"{'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
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
                                           f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
                                           f"Заказ взят: <b>{i.order_get}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n",
                                           disable_web_page_preview=True)
                    keyboard.add(f"{icon} {i.order_id} {icon}")
                keyboard.add(f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
                await bot.send_message(message.from_user.id,
                                       f"Всего в работе {len(res)} задач\n"
                                       f"Выберите ID задачи чтобы их просмотреть или завершить",
                                       reply_markup=keyboard)
            else:
                await performer_states.PerformerStart.orders.set()
                await bot.send_message(message.from_user.id, "У вас еще нет взятых заказов")
        if "Заказы Грузчика" in message.text:
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
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
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Грузчики: {' | '.join([k.username for k in loaders])}\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} "
                                           f"Рейтинг заказа | <b>{i.order_rating}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}\n",
                                           disable_web_page_preview=True)
                    keyboard.add(f"{config.KEYBOARD.get('ARROWS_BUTTON')} {i.order_id} "
                                 f"{config.KEYBOARD.get('ARROWS_BUTTON')}")
                keyboard.add(f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад")
                await bot.send_message(message.from_user.id,
                                       "Выберите ID задачи чтобы войти в детали заказа",
                                       reply_markup=keyboard)
                await performer_states.PerformerDetailsTasks.loading_tasks.set()
            else:
                await bot.send_message(message.from_user.id,
                                       "У вас нет взятых заказов для Грузчиков")
        if message.text == f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в главное меню":
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu())
            await performer_states.PerformerStart.performer_menu.set()

    @staticmethod
    async def choose_month(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        year = callback.data[14:]
        async with state.proxy() as data:
            data["year"] = year
        res = await performers_get.performer_get_finished_orders_year(callback.from_user.id,
                                                                      year)
        finished_orders = InlineKeyboardMarkup()
        months = []
        for i in res:
            months.append(calendar.month_name[datetime.strptime(i.order_end, '%d-%m-%Y, %H:%M:%S').month])
        res_months = Counter(months)
        for k, v in res_months.items():
            finished_orders.insert(InlineKeyboardButton(text=f"{k} ({v})",
                                                        callback_data=f"p_month_finish_{k}"))
        await bot.send_message(callback.from_user.id,
                               "<b>Выберите месяц</b>\n"
                               "В скобках указано кол-во завершенных заказов",
                               reply_markup=finished_orders)

    @staticmethod
    async def choose_day(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        month = callback.data[15:]
        months = {month: index for index, month in enumerate(calendar.month_name) if month}
        for k, v in months.items():
            if k == month:
                month = v
        if len(str(month)) == 1:
            month = f"0{month}"
        async with state.proxy() as data:
            data["month"] = month
        res = await performers_get.performer_get_finished_orders_month(callback.from_user.id,
                                                                       data.get("year"),
                                                                       month)
        finished_orders = InlineKeyboardMarkup()
        days = []
        for i in res:
            days.append(datetime.strptime(i.order_end, '%d-%m-%Y, %H:%M:%S').day)
        res_days = Counter(days)
        for k, v in res_days.items():
            finished_orders.insert(InlineKeyboardButton(text=f"{k} ({v})",
                                                        callback_data=f"p_day_finish_{k}"))
        await bot.send_message(callback.from_user.id,
                               "<b>Выберите день</b>\n"
                               "В скобках указано кол-во завершенных заказов",
                               reply_markup=finished_orders)

    @staticmethod
    async def choose_job(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        day = callback.data[13:]
        async with state.proxy() as data:
            data["day"] = day
        res = await performers_get.performer_get_finished_orders_day(callback.from_user.id,
                                                                     data.get("year"),
                                                                     data.get("month"),
                                                                     day)
        if res:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i in res:
                if i.image:
                    await bot.send_photo(callback.from_user.id, i.image)
                if i.video:
                    await bot.send_video(callback.from_user.id, i.video)
                await bot.send_message(callback.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"<b>Детали заказа</b>\n"
                                       f"{config.KEYBOARD.get('INPUT_LATIN_LETTERS')} "
                                       f"Категория - <b>{i.category_delivery}</b>\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID заказа - <b>{i.order_id}</b>\n"
                                       f"{config.KEYBOARD.get('A_BUTTON')} "
                                       f"Откуда - <a href='https://yandex.ru/maps/?text="
                                       f"{'+'.join(i.geo_position_from.split())}'>{i.geo_position_from}</a>\n"
                                       f"{config.KEYBOARD.get('B_BUTTON')} "
                                       f"Куда - <a href='https://yandex.ru/maps/?text="
                                       f"{'+'.join(i.geo_position_to.split())}'>{i.geo_position_to}</a>\n"
                                       f"{config.KEYBOARD.get('INFORMATION')} "
                                       f"Название - <b>{i.title}</b>\n"
                                       f"{config.KEYBOARD.get('CLIPBOARD')} "
                                       f"Описание - <b>{i.description}</b>\n"
                                       f"{config.KEYBOARD.get('DOLLAR')} "
                                       f"Цена - <b>{i.price}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}\n",
                                       disable_web_page_preview=True)
                keyboard.add(f"{i.order_id}")
                async with state.proxy() as data:
                    data[i.order_id] = {
                        'Название': i.title,
                        'ID заказа': i.order_id,
                        'ID исполнителя': i.in_work,
                        'Бюджет': i.price,
                    }
            keyboard.add("Вернуться в главное меню")
            await bot.send_message(callback.from_user.id,
                                   "Выберите ID задачи чтобы войти в детали заказа",
                                   reply_markup=keyboard)
            await performer_states.PerformerHistory.enter_history.set()

    @staticmethod
    async def jobs_offers(message: types.Message):
        if "12 часов" in message.text:
            job = await performers_get.check_job_sale("twelve")
            exist = await performers_get.performer_check_jobs_offers(message.from_user.id)
            if exist:
                await bot.send_message(message.from_user.id,
                                       f"<b>Внимание!</b>\n"
                                       f"<b>У вас уже есть смена!</b>\n"
                                       f"<b>Действует до <i>{exist.end}</i></b>\n"
                                       f"<b>Все равно хотите купить новую ?</b>",
                                       reply_markup=markup_performer.inline_jobs_offers(job.value, "twelve"))
            if not exist:
                await bot.send_message(message.from_user.id,
                                       "Вы покупаете смену на 12 часов\n"
                                       "За это время с вас не будет списываться комиссия",
                                       reply_markup=markup_performer.inline_jobs_offers(job.value, "twelve"))
        if "1 день" in message.text:
            job = await performers_get.check_job_sale("day")
            exist = await performers_get.performer_check_jobs_offers(message.from_user.id)
            if exist:
                await bot.send_message(message.from_user.id,
                                       f"<b>Внимание!</b>\n"
                                       f"<b>У вас уже есть смена!</b>\n"
                                       f"<b>Действует до <i>{exist.end}</i></b>\n"
                                       f"<b>Все равно хотите купить новую ?</b>",
                                       reply_markup=markup_performer.inline_jobs_offers(job.value, "day"))
            if not exist:
                await bot.send_message(message.from_user.id,
                                       "Вы покупаете смену на 1 день (24 часа)\n"
                                       "За это время с вас не будет списываться комиссия",
                                       reply_markup=markup_performer.inline_jobs_offers(job.value, "day"))
        if "3 дня" in message.text:
            job = await performers_get.check_job_sale("3_day")
            exist = await performers_get.performer_check_jobs_offers(message.from_user.id)
            if exist:
                await bot.send_message(message.from_user.id,
                                       f"<b>Внимание!</b>\n"
                                       f"<b>У вас уже есть смена!</b>\n"
                                       f"<b>Действует до <i>{exist.end}</i></b>\n"
                                       f"<b>Все равно хотите купить новую ?</b>",
                                       reply_markup=markup_performer.inline_jobs_offers(job.value, "3_day"))
            if not exist:
                await bot.send_message(message.from_user.id,
                                       "Вы покупаете смену на 3 дня (72 часа)\n"
                                       "За это время с вас не будет списываться комиссия",
                                       reply_markup=markup_performer.inline_jobs_offers(job.value, "3_day"))
        if "1 неделя" in message.text:
            job = await performers_get.check_job_sale("week")
            exist = await performers_get.performer_check_jobs_offers(message.from_user.id)
            if exist:
                await bot.send_message(message.from_user.id,
                                       f"<b>Внимание!</b>\n"
                                       f"<b>У вас уже есть смена!</b>\n"
                                       f"<b>Действует до <i>{exist.end}</i></b>\n"
                                       f"<b>Все равно хотите купить новую ?</b>",
                                       reply_markup=markup_performer.inline_jobs_offers(job.value, "week"))
            if not exist:
                await bot.send_message(message.from_user.id,
                                       "Вы покупаете смену на 1 неделю (168 часов)\n"
                                       "За это время с вас не будет списываться комиссия",
                                       reply_markup=markup_performer.inline_jobs_offers(job.value, "week"))
        if "Вернуться в главное меню" in message.text:
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu())
            await performer_states.PerformerStart.performer_menu.set()

    @staticmethod
    async def approve_jobs_offers(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        time = callback.data.split('-')[1]
        if time == "twelve":
            time = 12
        if time == "day":
            time = 24
        if time == "3_day":
            time = 72
        if time == "week":
            time = 168
        price = callback.data.split('-')[2]
        time_d = (datetime.now() + timedelta(hours=time)).strftime('%d-%m-%Y, %H:%M:%S')
        await performers_set.performer_jobs_pay(callback.from_user.id,
                                                datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                time_d,
                                                int(price))
        await bot.send_message(callback.from_user.id,
                               f"Вы купили смену на {time} часа")


class PerformerProfile:
    @staticmethod
    async def performer_profile(message: types.Message):
        if "Главное меню" in message.text:
            await performer_states.PerformerStart.performer_menu.set()
            orders = await performers_get.performer_view_list_orders(message.from_user.id)
            orders_loading = await performers_get.performer_loader_order(message.from_user.id)
            promo = await performers_get.check_commission_promo(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{markup_performer.text_menu(len(orders), len(orders_loading), promo)}",
                                   reply_markup=markup_performer.main_menu())
        if "Автоотправление предложений" in message.text:
            job = await performers_get.check_job_sale("auto_send")
            performer = await performers_get.performer_auto_send_check(message.from_user.id)
            if not performer:
                await bot.send_message(message.from_user.id,
                                       "Подключить платную услугу\n"
                                       "Автоотправление предложений о работе\n"
                                       f"Стоимость данной услуги {job.value} рублей за 24 часа",
                                       reply_markup=markup_performer.auto_send_pay(job.value))

            else:
                await bot.send_message(message.from_user.id,
                                       f"У вас уже действует <b>Автоотправление предложений</b>\n"
                                       f"Время окончания - <b>{performer.end}</b>")
        if "Статус категории" in message.text:
            res = await performers_get.performer_trying_change_self_category(message.from_user.id)
            if res:
                limit = datetime.strptime(res, '%d-%m-%Y, %H:%M:%S')
                limitation = str(datetime.now() - limit)[:1]
                if limitation == "-":
                    await bot.send_message(message.from_user.id,
                                           f"У вас еще действует ограничение на смену статуса\n"
                                           f"Ограничение снимется <b>{res}</b>")
                    await performer_states.PerformerProfile.my_profile.set()
                if limitation != "-":
                    await bot.send_message(message.from_user.id,
                                           "Здесь вы сможете сменить свой статус\n"
                                           "<b>Статус вы можете сменить только раз в 12 часов</b>",
                                           reply_markup=markup_performer.performer_profile_change_status())
                    await performer_states.PerformerProfile.change_status.set()
            else:
                await bot.send_message(message.from_user.id,
                                       "Здесь вы сможете сменить свой статус\n"
                                       "<b>Статус вы можете сменить только раз в 12 часов</b>",
                                       reply_markup=markup_performer.performer_profile_change_status())
                await performer_states.PerformerProfile.change_status.set()
        if "Пополнить баланс" in message.text:
            await general_set.get_payment_exists_and_delete(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   "Пополнение баланса должно быть не меньше <b>50</b> рублей!"
                                   "Введите сумму, на которую вы хотите пополнить баланс",
                                   reply_markup=markup_performer.back_user_profile())
            await performer_states.PerformerProfile.pay.set()
        if "Статистика" in message.text:
            performer = await performers_get.performer_count_orders(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"{config.KEYBOARD.get('MONEY_BAG')} "
                                   f"Вы внесли - <b>{performer[0].money_added}</b> руб.\n"
                                   f"{config.KEYBOARD.get('MONEY_BAG')} "
                                   f"Вы заработали - <b>{performer[0].money_earned}</b> руб.\n"
                                   f"{config.KEYBOARD.get('DOLLAR')} "
                                   f"Ваш текущий баланс: <b>{performer[0].performer_money}</b> руб.\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} Всего заказов вы взяли - "
                                   f"<b>{performer[0].get_orders}</b>\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} В работе - <b>{performer[1]}</b>\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} Выполненных - "
                                   f"<b>{performer[0].completed_orders}</b>\n"
                                   f"{config.KEYBOARD.get('CROSS_MARK')} Отменённых - "
                                   f"<b>{performer[0].canceled_orders}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   )

    @staticmethod
    async def auto_send_job_offer(callback: types.CallbackQuery):
        money = callback.data[14:]
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        time_d = (datetime.now() + timedelta(hours=24)).strftime('%d-%m-%Y, %H:%M:%S')
        await performers_set.performer_auto_send_pay(callback.from_user.id,
                                                     datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
                                                     time_d,
                                                     money)
        await performers_set.performer_change_auto_send(callback.from_user.id)
        auto_send = await performers_get.performer_auto_send_check(callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               "Вы активировали доп услугу\n"
                               "Теперь вы будете получать автоматически сообщения о новых заказах\n"
                               f"Действует до <b>{time_d}</b>",
                               reply_markup=markup_performer.performer_profile(auto_send))

    @staticmethod
    async def performer_profile_change_status(message: types.Message):
        if message.text == f"{config.KEYBOARD.get('PERSON_RUNNING')} Я пешеход":
            await performers_set.performer_set_self_status(message.from_user.id,
                                                           "pedestrian",
                                                           (datetime.now() + timedelta(hours=12)).strftime(
                                                               '%d-%m-%Y, %H:%M:%S'))
            await bot.send_message(message.from_user.id,
                                   "Теперь ты пешеход!")
            res = await performers_get.performer_select(message.from_user.id)
            status = "Пешеход"
            icon = f"{config.KEYBOARD.get('PERSON_RUNNING')}"
            await performer_states.PerformerProfile.my_profile.set()
            auto_send = await performers_get.performer_auto_send_check(message.from_user.id)
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
                                   f"{config.KEYBOARD.get('STAR')} "
                                   f"Ваш рейтинг: <b>{res.performer_rating}</b>\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                   f"Взял заказов: <b>{res.get_orders}</b>\n"
                                   f"{config.KEYBOARD.get('CROSS_MARK')} "
                                   f"Отменил заказов: <b>{res.canceled_orders}</b>\n"
                                   f"{icon} Ваша категория: <b>{status}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   reply_markup=markup_performer.performer_profile(auto_send))
        if message.text == f"{config.KEYBOARD.get('AUTOMOBILE')} Я на транспорте":
            await performer_states.PerformerProfile.change_status_transport.set()
            await bot.send_message(message.from_user.id,
                                   "Выберите ваш транспорт",
                                   reply_markup=markup_performer.performer_profile_change_status_transport())
        if message.text == f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            res = await performers_get.performer_select(message.from_user.id)
            status = None
            icon = None
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
            auto_send = await performers_get.performer_auto_send_check(message.from_user.id)
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
                                   f"{config.KEYBOARD.get('STAR')} "
                                   f"Ваш рейтинг: <b>{res.performer_rating}</b>\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                   f"Взял заказов: <b>{res.get_orders}</b>\n"
                                   f"{config.KEYBOARD.get('CROSS_MARK')} "
                                   f"Отменил заказов: <b>{res.canceled_orders}</b>\n"
                                   f"{icon} Ваша категория: <b>{status}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   reply_markup=markup_performer.performer_profile(auto_send))

    @staticmethod
    async def transport(message: types.Message):
        if message.text == f"{config.KEYBOARD.get('AUTOMOBILE')} Я на машине":
            await performers_set.performer_set_self_status(message.from_user.id,
                                                           "car",
                                                           (datetime.now() + timedelta(hours=12)).strftime(
                                                               '%d-%m-%Y, %H:%M:%S'))
            await bot.send_message(message.from_user.id,
                                   "Теперь ты на машине!")
            res = await performers_get.performer_select(message.from_user.id)
            status = "На машине"
            icon = f"{config.KEYBOARD.get('AUTOMOBILE')}"
            await performer_states.PerformerProfile.my_profile.set()
            auto_send = await performers_get.performer_auto_send_check(message.from_user.id)
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
                                   f"{config.KEYBOARD.get('STAR')} "
                                   f"Ваш рейтинг: <b>{res.performer_rating}</b>\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                   f"Взял заказов: <b>{res.get_orders}</b>\n"
                                   f"{config.KEYBOARD.get('CROSS_MARK')} "
                                   f"Отменил заказов: <b>{res.canceled_orders}</b>\n"
                                   f"{icon} Ваша категория: <b>{status}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   reply_markup=markup_performer.performer_profile(auto_send))
        if message.text == f"{config.KEYBOARD.get('KICK_SCOOTER')} Я на самокате":
            await performers_set.performer_set_self_status(message.from_user.id,
                                                           "scooter",
                                                           (datetime.now() + timedelta(hours=12)).strftime(
                                                               '%d-%m-%Y, %H:%M:%S'))
            await bot.send_message(message.from_user.id,
                                   "Теперь ты на самокате!")
            res = await performers_get.performer_select(message.from_user.id)
            status = "На самокате"
            icon = f"{config.KEYBOARD.get('KICK_SCOOTER')}"
            await performer_states.PerformerProfile.my_profile.set()
            auto_send = await performers_get.performer_auto_send_check(message.from_user.id)
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
                                   f"{config.KEYBOARD.get('STAR')} "
                                   f"Ваш рейтинг: <b>{res.performer_rating}</b>\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                   f"Взял заказов: <b>{res.get_orders}</b>\n"
                                   f"{config.KEYBOARD.get('CROSS_MARK')} "
                                   f"Отменил заказов: <b>{res.canceled_orders}</b>\n"
                                   f"{icon} Ваша категория: <b>{status}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   reply_markup=markup_performer.performer_profile(auto_send))
        if message.text == f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Назад":
            res = await performers_get.performer_select(message.from_user.id)
            status = None
            icon = None
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
            auto_send = await performers_get.performer_auto_send_check(message.from_user.id)
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
                                   f"{config.KEYBOARD.get('STAR')} "
                                   f"Ваш рейтинг: <b>{res.performer_rating}</b>\n"
                                   f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                   f"Взял заказов: <b>{res.get_orders}</b>\n"
                                   f"{config.KEYBOARD.get('CROSS_MARK')} "
                                   f"Отменил заказов: <b>{res.canceled_orders}</b>\n"
                                   f"{icon} Ваша категория: <b>{status}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   reply_markup=markup_performer.performer_profile(auto_send))

    @staticmethod
    async def pay(message: types.Message):
        if f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в Мой профиль" == message.text:
            await performer_states.PerformerProfile.my_profile.set()
            auto_send = await performers_get.performer_auto_send_check(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в Мой профиль",
                                   reply_markup=markup_performer.performer_profile(auto_send))
        if f"{config.KEYBOARD.get('RIGHT_ARROW_CURVING_LEFT')} Вернуться в Мой профиль" != message.text:
            if message.text.isdigit() and int(message.text) >= 50:
                try:
                    message_money = int(message.text)
                    if message_money >= 1:
                        comment = f"Выставлен счёт для {message.from_user.first_name}_{randint(1, 10000)}"
                        bill = config.P2P.bill(amount=message_money, lifetime=5, comment=comment)
                        await general_set.add_payment(message.from_user.id, message_money, bill.bill_id)
                        await bot.send_message(message.from_user.id,
                                               f"Вам нужно отправить <b>{message_money}</b> руб на наш счёт QIWI\n"
                                               f"{comment}",
                                               reply_markup=markup_performer.buy_menu(url=bill.pay_url,
                                                                                      bill=bill.bill_id))
                    else:
                        await bot.send_message(message.from_user.id,
                                               "Минимальная сумма для пополнения 1 руб.",
                                               reply_markup=markup_performer.cancel_pay())
                except ValueError:
                    await bot.send_message(message.from_user.id, "Введите целое число")
            else:
                await bot.send_message(message.from_user.id,
                                       "Пополнение баланса должно быть не меньше <b>50</b> рублей!")

    @staticmethod
    async def check(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        bill = str(callback.data[6:])
        async with state.proxy() as data:
            data['bill'] = bill
            data['user_id'] = callback.from_user.id
        info = await general_get.get_payment(bill)
        if info:
            if str(config.P2P.check(bill_id=bill).status) == "PAID":
                await performers_set.set_money(callback.from_user.id, int(info.money))
                await general_set.delete_payment(callback.from_user.id)
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
                auto_send = await performers_get.performer_auto_send_check(callback.from_user.id)
                await bot.send_message(callback.from_user.id,
                                       "Ваш счёт пополнен!\n",
                                       reply_markup=markup_performer.performer_profile(auto_send))
                await state.finish()
                res = await performers_get.performer_select(callback.from_user.id)
                if res.performer_category == "pedestrian":
                    status = "Пешеход"
                    icon = f"{config.KEYBOARD.get('PERSON_RUNNING')}"
                elif res.performer_category == "car":
                    status = "На машине"
                    icon = f"{config.KEYBOARD.get('AUTOMOBILE')}"
                else:
                    status = "На скутере"
                    icon = f"{config.KEYBOARD.get('KICK_SCOOTER')}"
                auto_send = await performers_get.performer_auto_send_check(callback.from_user.id)
                await bot.send_message(callback.from_user.id,
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
                                       f"{config.KEYBOARD.get('STAR')} "
                                       f"Ваш рейтинг: <b>{res.performer_rating}</b>\n"
                                       f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                       f"Взял заказов: <b>{res.get_orders}</b>\n"
                                       f"{config.KEYBOARD.get('CROSS_MARK')} "
                                       f"Отменил заказов: <b>{res.canceled_orders}</b>\n"
                                       f"{icon} Ваша категория: <b>{status}</b>\n"
                                       f"{config.KEYBOARD.get('DASH') * 14}",
                                       reply_markup=markup_performer.performer_profile(auto_send))
                await performer_states.PerformerProfile.my_profile.set()
            else:
                await bot.send_message(callback.from_user.id,
                                       "Платёж не прошел",
                                       reply_markup=markup_performer.buy_menu(False, bill=bill))
        else:
            await bot.send_message(callback.from_user.id, "Счёт не найден")
            await state.finish()

    @staticmethod
    async def cancel(callback: types.CallbackQuery, state: FSMContext):
        await general_set.delete_payment(callback.from_user.id)
        await state.finish()
        auto_send = await performers_get.performer_auto_send_check(callback.from_user.id)
        await bot.send_message(callback.from_user.id,
                               "Вы отменили пополнение баланса\n",
                               reply_markup=markup_performer.performer_profile(auto_send))
        await performer_states.PerformerProfile.my_profile.set()
