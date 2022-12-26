from collections import Counter
import csv
from datetime import datetime, timedelta

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, ParseMode

from bot import bot, dp
# from data.get_set_db import global_db_obj, global_set_db_obj, admin_get_db_obj, admin_set_db_obj
from data.commands import general_get, general_get, admins_get, admins_set
from handler_customer.customer import CustomerMain
from handler_performer.performer import PerformerMain
from markups import markup_start, markup_admin
from settings import config
from states import states


class AdminMain:
    @staticmethod
    async def admin_main(message: types.Message, state: FSMContext):
        if message.text == "Комиссия":
            await bot.send_message(message.from_user.id,
                                   "Здесь вы сможете изменить комиссию для Заказчиков и для Исполнителей "
                                   "а так же для разных видов деятельности",
                                   reply_markup=markup_admin.commission())
            await states.Commission.commission.set()
            AdminCommission.register_commission_handler(dp)
        if message.text == "Просмотр Заказов":
            await bot.send_message(message.from_user.id,
                                   "Здесь вы сможете просмотреть все заказы, статистику, и отзывы",
                                   reply_markup=markup_admin.orders_stat())
            await states.AdminStates.orders.set()
        if message.text == "Выгрузка БД Заказчиков и Исполнителей":
            await bot.send_message(message.from_user.id,
                                   "Выгрузка БД Заказчиков и Исполнителей",
                                   reply_markup=markup_admin.loading_db())
            await states.AdminStates.loading_db.set()
        if message.text == "Управление Заказчиками":
            await bot.send_message(message.from_user.id,
                                   "Здесь вы сможете посмотреть информацию о Заказчике",
                                   reply_markup=markup_admin.about_customers())
            await states.AboutUsers.enter.set()
            async with state.proxy() as data:
                data["type_user"] = "customers"
            AdminControl.register_control_handler(dp)
        if message.text == "Управление Исполнителями":
            await bot.send_message(message.from_user.id,
                                   "Здесь вы сможете посмотреть информацию о Исполнителе",
                                   reply_markup=markup_admin.about_performers())
            await states.AboutUsers.enter.set()
            async with state.proxy() as data:
                data["type_user"] = "performers"
            AdminControl.register_control_handler(dp)
        if message.text == "Выход":
            await bot.send_message(message.from_user.id,
                                   f'Добро пожаловать в Telegram Bot который поможет найти исполнителя '
                                   f'или подзаработать', reply_markup=markup_start.markup_clean)
            await state.finish()
            await bot.send_message(message.from_user.id,
                                   f'Ты заказчик или исполнитель {message.from_user.first_name} ?',
                                   reply_markup=markup_start.inline_start)
            CustomerMain.register_customer_handler(dp)
            PerformerMain.register_performer_handler(dp)

    @staticmethod
    async def orders(message: types.Message):
        if message.text == "Просмотр заказов":
            await bot.send_message(message.from_user.id,
                                   "Здесь вы можете просмотреть заказ, отзывы и информацию об участниках",
                                   reply_markup=markup_admin.enter_ID())
            await states.Orders.enter.set()
            AdminOrders.register_orders_handler(dp)
        if message.text == "Статистика":
            await bot.send_message(message.from_user.id,
                                   "Здесь вы можете просмотреть статистику",
                                   reply_markup=markup_admin.statistics())
            await states.Statistics.enter.set()
            AdminStats.register_orders_handler(dp)
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню Администратора",
                                   reply_markup=markup_admin.admin_main())
            await states.AdminStates.enter.set()

    @staticmethod
    async def loading_db(message: types.Message):
        if message.text == "Загрузить БД Заказчиков":
            all_customers = await general_get.all_customers()
            with open("logs/table_customers.csv", "w", newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["id", "user_id", "username", "telephone", "firstname",
                                 "lastname", "rating", "ban"])
                for i in all_customers:
                    writer.writerow([i.id, i.user_id, i.username, i.telephone, i.first_name, i.last_name,
                                     i.customer_rating, i.ban])
            table_customers = InputFile("logs/table_customers.csv")
            await bot.send_document(chat_id=message.from_user.id, document=table_customers)
        if message.text == "Загрузить БД Исполнителей":
            all_performers = await general_get.all_performers()
            with open("logs/table_performers.csv", "w", newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["id", "user_id", "username", "telephone", "firstname",
                                 "lastname", "rating", "ban"])
                for i in all_performers:
                    writer.writerow([i.id, i.user_id, i.username, i.telephone, i.first_name, i.last_name,
                                     i.performer_rating, i.ban])
            table_performers = InputFile("logs/table_performers.csv")
            await bot.send_document(chat_id=message.from_user.id, document=table_performers)
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню Администратора",
                                   reply_markup=markup_admin.admin_main())
            await states.AdminStates.enter.set()

    @staticmethod
    async def register_admin_handler(dp: Dispatcher):
        dp.register_message_handler(AdminMain.admin_main, state=states.AdminStates.enter)
        dp.register_message_handler(AdminMain.loading_db, state=states.AdminStates.loading_db)
        dp.register_message_handler(AdminMain.orders, state=states.AdminStates.orders)


class AdminOrders:
    @staticmethod
    async def enter_orders(message: types.Message):
        if message.text == "Введите ID заказа":
            await states.Orders.order.set()
            await bot.send_message(message.from_user.id,
                                   "Введите ID заказа!",
                                   reply_markup=markup_admin.markup_clean)
        if message.text == "Выгрузить БД заказов":
            res = await general_get.all_orders()
            with open("logs/table_orders.csv", "w", newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["id", "user_id", "geo_position_from", "geo_position_to", "title", "price", "description",
                                 "image", "video", "performer_id", "completed", "order_id", "order_create", "order_get",
                                 "order_cancel", "order_end", "category_delivery", "block", "performer_category",
                                 "order_expired", "order_worth", "order_rating"])
                for i in res:
                    writer.writerow([i.id, i.user_id, i.geo_position_from, i.geo_position_to, i.title, i.price,
                                     i.description, i.image, i.video, i.in_work, i.completed, i.order_id,
                                     i.order_create, i.order_get, i.order_cancel, i.order_end, i.category_delivery,
                                     i.block, i.performer_category, i.order_expired, i.order_worth, i.order_rating])
            table_orders = InputFile("logs/table_orders.csv")
            await bot.send_document(chat_id=message.from_user.id, document=table_orders)
        if message.text == "Выгрузить БД отзывов":
            res = await general_get.all_orders_reviews()
            with open("logs/table_reviews.csv", "w", newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["id", "review_from_customer", "review_from_performer",
                                 "rating_from_customer", "rating_from_performer", "order_id"])
                for i in res:
                    writer.writerow([i.id, i.review_from_customer, i.review_from_performer, i.rating_from_customer,
                                     i.rating_from_performer, i.order_id])
            table_reviews = InputFile("logs/table_reviews.csv")
            await bot.send_document(chat_id=message.from_user.id, document=table_reviews)
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы в главном меню",
                                   reply_markup=markup_admin.orders_stat())
            await states.AdminStates.orders.set()

    @staticmethod
    async def order(message: types.Message, state: FSMContext):
        res = await admins_get.admin_check_order(message.text)
        if res:
            await bot.send_message(message.from_user.id,
                                   f"Просматриваем заказ {message.text}\n")
            async with state.proxy() as data:
                data["order_id"] = res.order_id
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"<b>Детали заказа</b>\n"
                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                   f"ID заказа <b>{res.order_id}</b>\n"
                                   f"{config.KEYBOARD.get('A_BUTTON')} "
                                   f"Откуда <b>{res.geo_position_from}</b>\n"
                                   f"{config.KEYBOARD.get('B_BUTTON')} "
                                   f"Куда <b>{res.geo_position_to}</b>\n"
                                   f"{config.KEYBOARD.get('INFORMATION')} "
                                   f"Название <b>{res.title}</b>\n"
                                   f"{config.KEYBOARD.get('CLIPBOARD')} "
                                   f"Описание <b>{res.description}</b>\n"
                                   f"{config.KEYBOARD.get('DOLLAR')} "
                                   f"Цена <b>{res.price}</b>\n"
                                   f"{config.KEYBOARD.get('WHITE_CIRCLE')} "
                                   f"Создан <b>{res.order_create}</b>\n"
                                   f"{config.KEYBOARD.get('GREEN_CIRCLE')} "
                                   f"Взят <b>{res.order_get}</b>\n"
                                   f"{config.KEYBOARD.get('BLUE_CIRCLE')} "
                                   f"Завершен <b>{res.order_end}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}\n",
                                   reply_markup=markup_admin.order())
            await states.Orders.detail_order.set()
        else:
            await bot.send_message(message.from_user.id,
                                   f"Такой заказ {message.text} не найден! \n",
                                   reply_markup=markup_admin.enter_ID())
            await states.Orders.enter.set()

    @staticmethod
    async def order_details(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            order = await admins_get.admin_check_order(data.get("order_id"))
            customer_res = await admins_get.admin_check_users('customers', order.user_id)
            performer_res = await admins_get.admin_check_users('performers', order.in_work)
            review_res = await admins_get.admin_check_review(order.order_id)
        if message.text == "Просмотр Заказчика":
            await bot.send_message(message.from_user.id,
                                   f"Просматриваем Заказчика")
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 14}\n"
                                   f"Профиль <b>Заказчика</b>:\n"
                                   f"{config.KEYBOARD.get('ID_BUTTON')} "
                                   f"ID : <b>{customer_res.user_id}</b>\n"
                                   f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                   f"Никнейм <b>@{customer_res.username}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Номер <b>{customer_res.telephone}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Имя <b>{customer_res.first_name}</b>\n"
                                   f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                   f"Фамилия <b>{customer_res.last_name}</b>\n"
                                   f"{config.KEYBOARD.get('BAR_CHART')} "
                                   f"Рейтинг <b>"
                                   f"{customer_res.customer_rating}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 14}",
                                   )
        if message.text == "Просмотр Исполнителя":
            await bot.send_message(message.from_user.id,
                                   f"Просматриваем Исполнителя")
            if performer_res:
                await bot.send_message(message.from_user.id,
                                       f"{config.KEYBOARD.get('DASH') * 14}\n"
                                       f"Профиль <b>Исполнителя</b>:\n"
                                       f"{config.KEYBOARD.get('ID_BUTTON')} "
                                       f"ID : <b>{performer_res.user_id}</b>\n"
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
            else:
                await bot.send_message(message.from_user.id, "Исполнителя еще нет!")
        if message.text == "Просмотр Отзывов":
            await bot.send_message(message.from_user.id,
                                   f"Просматриваем Отзывы")
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 10}\n"
                                   f"Отзыв от <b>Заказчика</b>:\n"
                                   f"<b>{review_res.review_from_customer}</b>\n"
                                   f"Оценка от Заказчика - <b>{review_res.rating_from_customer}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 10}")
            await bot.send_message(message.from_user.id,
                                   f"{config.KEYBOARD.get('DASH') * 10}\n"
                                   f"Отзыв от <b>Исполнителя</b>:\n"
                                   f"<b>{review_res.review_from_performer}</b>\n"
                                   f"Оценка от <b>Исполнителя</b> - <b>{review_res.rating_from_performer}</b>\n"
                                   f"{config.KEYBOARD.get('DASH') * 10}")
        if message.text == "Выгрузить БД этого заказа":
            await bot.send_message(message.from_user.id,
                                   f"Подготавливаем документ")
            with open(f"logs/table_order_{order.order_id}.csv", "w", newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(['Table order'])
                writer.writerow(["id", "user_id", "geo_position_from", "geo_position_to", "title", "price",
                                 "description", "image", "video", "performer_id", "completed", "order_id",
                                 "order_create", "order_get", "order_cancel", "order_end", "category_delivery",
                                 "performer_category", "order_expired", "order_worth", "order_rating"])
                writer.writerow([order.id, order.user_id, order.geo_position_from, order.geo_position_to,
                                 order.title, order.price, order.description, order.image, order.video,
                                 order.in_work, order.completed, order.order_id, order.order_create,
                                 order.order_get, order.order_cancel, order.order_end, order.category_delivery,
                                 order.performer_category, order.order_expired, order.order_worth,
                                 order.order_rating])
                writer.writerow(['Table review'])
                writer.writerow(["id", "review_from_customer", "review_from_performer",
                                 "rating_from_customer", "rating_from_performer"])
                writer.writerow([review_res.id, review_res.review_from_customer, review_res.review_from_performer,
                                 review_res.rating_from_customer, review_res.rating_from_performer])
                writer.writerow(['Table customer'])
                writer.writerow(["id", "user_id", "username", "telephone", "first_name", "last_name",
                                 "customer_rating", "ban", "create_orders", "canceled_orders"])
                writer.writerow([customer_res.id, customer_res.username, customer_res.telephone,
                                 customer_res.first_name, customer_res.last_name, customer_res.customer_rating,
                                 customer_res.create_orders, customer_res.canceled_orders])
                writer.writerow(['Table performer'])
                writer.writerow(["id", "user_id", "username", "telephone", "first_name", "last_name",
                                 "performer_rating", "get_orders", "canceled_orders"])
                writer.writerow([performer_res.id, performer_res.user_id, performer_res.username,
                                 performer_res.first_name, performer_res.last_name, performer_res.performer_rating,
                                 performer_res.get_orders, performer_res.canceled_orders])
            table_reviews = InputFile(f"logs/table_order_{order.order_id}.csv")
            await bot.send_document(chat_id=message.from_user.id, document=table_reviews)
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Здесь вы сможете просмотреть все заказы, статистику, и отзывы",
                                   reply_markup=markup_admin.enter_ID())
            await states.Orders.enter.set()

    @staticmethod
    def register_orders_handler(dp: Dispatcher):
        dp.register_message_handler(AdminOrders.enter_orders, state=states.Orders.enter)
        dp.register_message_handler(AdminOrders.order, state=states.Orders.order)
        dp.register_message_handler(AdminOrders.order_details, state=states.Orders.detail_order)


class AdminStats:
    @staticmethod
    async def stat_main(message: types.Message):
        res_orders = await general_get.all_orders()
        if message.text == "По заказчикам":
            await bot.send_message(message.from_user.id, "Выгружаем статистику по Заказчикам")
            res_customers = await general_get.all_customers()
            await bot.send_message(message.from_user.id,
                                   f"Всего Заказчиков: {len(res_customers)}\n"
                                   f"Всего заказов было создано {len(res_orders)}")
        if message.text == "По исполнителям":
            await bot.send_message(message.from_user.id, "Выгружаем статистику по Исполнителям")
            res_performers = await general_get.all_performers()
            res_completed = await general_get.all_completed_orders()
            await bot.send_message(message.from_user.id,
                                   f"Всего Исполнителей: {len(res_performers)}\n"
                                   f"Всего заказов выполнено: {len(res_completed)}")
        if message.text == "По категориям":
            await bot.send_message(message.from_user.id, "Выгружаем статистику по категориям")

            res_orders_category = Counter([i.category_delivery for i in res_orders]).most_common()
            await bot.send_message(message.from_user.id,
                                   f"Созданные заказы по категориям:")
            for i in res_orders_category:
                await bot.send_message(message.from_user.id,
                                       f"{i[0]} - {i[1]}")
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Здесь вы можете просмотреть заказ, отзывы и информацию об участниках",
                                   reply_markup=markup_admin.orders_stat())
            await states.AdminStates.orders.set()

    @staticmethod
    def register_orders_handler(dp: Dispatcher):
        dp.register_message_handler(AdminStats.stat_main, state=states.Statistics.enter)


class AdminCommission:
    CATEGORY_DICT = {"Цветы": "flowers", "Подарки": "gifts", "Кондитерка": "confection",
                     "Документы": "documents", "Погрузка/Разгрузка": "loading", "Другое": "other"}

    @staticmethod
    async def commission(message: types.Message):
        if message.text == "Просмотр комиссии":
            res = await admins_get.admin_check_commission()
            await bot.send_message(message.from_user.id,
                                   "Выводим информацию о комиссии")
            await bot.send_message(message.from_user.id,
                                   f"Для Заказчика - {res[0].commission}\n"
                                   f"Цветы - {res[1].commission}\n"
                                   f"Подарки - {res[2].commission}\n"
                                   f"Кондитерка - {res[3].commission}\n"
                                   f"Документы - {res[4].commission}\n"
                                   f"Погрузка/Загрузка - {res[5].commission}\n"
                                   f"Другое - {res[6].commission}")
        if message.text == "Установить комиссию":
            await bot.send_message(message.from_user.id,
                                   "Здесь вы сможете изменить комиссию для Исполнителей "
                                   "а так же для разных видов деятельности",
                                   reply_markup=markup_admin.commission_set())
            await states.Commission.commission_set.set()
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню Администратора",
                                   reply_markup=markup_admin.admin_main())
            await states.AdminStates.enter.set()

    @staticmethod
    async def commission_set(message: types.Message):
        if message.text == "Для Исполнителя":
            await bot.send_message(message.from_user.id,
                                   "Установите комиссию для исполнителя",
                                   reply_markup=markup_admin.back()
                                   )
            await states.Commission.commission_for_performer.set()
        if message.text == "Для категорий доставок":
            await bot.send_message(message.from_user.id,
                                   "Установите комиссию для категорий доставок",
                                   reply_markup=markup_admin.commission_for_categories()
                                   )
            await states.CommissionForCategories.commission_for_categories.set()
        if message.text == "Промо":
            await bot.send_message(message.from_user.id,
                                   "Временное отсутствие комиссии",
                                   reply_markup=markup_admin.commission_promo())
            await states.Commission.commission_promo.set()
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в раздел комиссий",
                                   reply_markup=markup_admin.commission())
            await states.Commission.commission.set()

    @staticmethod
    async def commission_for_performer(message: types.Message):
        try:
            res = float(message.text)
        except ValueError:
            res = message.text
        if isinstance(res, float) and 0 <= res <= 20:
            await admins_set.admin_set_commission_for_performer(message.text)
            await bot.send_message(message.from_user.id,
                                   f"Отлично! Вы установили комиссию для Исполнителя в размере {res}",
                                   reply_markup=markup_admin.commission())
            await states.Commission.commission.set()
        if isinstance(res, float) and res > 20:
            await bot.send_message(message.from_user.id, "Комиссия не может составлять больше 20%")
        if isinstance(res, float) and res < 0:
            await bot.send_message(message.from_user.id, "Комиссия не может составлять меньше 0%")
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад",
                                   reply_markup=markup_admin.commission_set())
            await states.Commission.commission_set.set()
        if not isinstance(res, float) and message.text != "Назад":
            await bot.send_message(message.from_user.id, "Надо ввести целое число")

    @staticmethod
    async def commission_for_categories(message: types.Message, state: FSMContext):
        if message.text == "Цветы":
            async with state.proxy() as data:
                data["category"] = message.text
            await bot.send_message(message.from_user.id,
                                   "Установите комиссию для Цветов",
                                   reply_markup=markup_admin.back()
                                   )
            await states.CommissionForCategories.commission_for_category.set()
        if message.text == "Подарки":
            async with state.proxy() as data:
                data["category"] = message.text
            await bot.send_message(message.from_user.id,
                                   "Установите комиссию для Подарков",
                                   reply_markup=markup_admin.back()
                                   )
            await states.CommissionForCategories.commission_for_category.set()
        if message.text == "Кондитерка":
            async with state.proxy() as data:
                data["category"] = message.text
            await bot.send_message(message.from_user.id,
                                   "Установите комиссию для Кондитерки",
                                   reply_markup=markup_admin.back()
                                   )
            await states.CommissionForCategories.commission_for_category.set()
        if message.text == "Документы":
            async with state.proxy() as data:
                data["category"] = message.text
            await bot.send_message(message.from_user.id,
                                   "Установите комиссию для Документов",
                                   reply_markup=markup_admin.back()
                                   )
            await states.CommissionForCategories.commission_for_category.set()
        if message.text == "Погрузка/Разгрузка":
            async with state.proxy() as data:
                data["category"] = message.text
            await bot.send_message(message.from_user.id,
                                   "Установите комиссию для Позгрузки/Разгрузки",
                                   reply_markup=markup_admin.back()
                                   )
            await states.CommissionForCategories.commission_for_category.set()
        if message.text == "Другое":
            async with state.proxy() as data:
                data["category"] = message.text
            await bot.send_message(message.from_user.id,
                                   "Установите комиссию для Других видов деятельности",
                                   reply_markup=markup_admin.back()
                                   )
            await states.CommissionForCategories.commission_for_category.set()
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад",
                                   reply_markup=markup_admin.commission_set())
            await states.Commission.commission_set.set()

    @staticmethod
    async def commission_for(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            category = data.get("category")
        try:
            res_text = float(message.text)
        except ValueError:
            res_text = message.text
        if isinstance(res_text, float) and 0 <= res_text <= 10:
            await admins_set.admin_set_commission_for_categories(category, res_text)
            await bot.send_message(message.from_user.id,
                                   f"Отлично! Вы установили комиссию для Категории {category} в размере {res_text}",
                                   reply_markup=markup_admin.commission())
            await states.Commission.commission.set()
        if isinstance(res_text, float) and res_text > 10:
            await bot.send_message(message.from_user.id, "Комиссия не может составлять больше 10%")
        if isinstance(res_text, float) and res_text < 0:
            await bot.send_message(message.from_user.id, "Комиссия не может составлять меньше 0%")
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись на шаг назад",
                                   reply_markup=markup_admin.commission_for_categories())
            await states.CommissionForCategories.commission_for_categories.set()
        if not isinstance(res_text, float) and message.text != "Назад":
            await bot.send_message(message.from_user.id, "Надо ввести целое число")

    @staticmethod
    async def commission_promo(message: types.Message):
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в раздел Установки комиссий",
                                   reply_markup=markup_admin.commission_set())
            await states.Commission.commission_set.set()
        if message.text == "Введите ID Исполнителя":
            await bot.send_message(message.from_user.id,
                                   "Введите ID Исполнителя чтобы найти его",
                                   reply_markup=markup_admin.back())
            await states.Commission.commission_promo_find_id.set()

    @staticmethod
    async def commission_promo_find_id(message: types.Message, state: FSMContext):
        if message.text.isdigit():
            res = admin_get_db_obj.admin_check_users("performers", message.text)
            try:
                if not bool(res[8]):
                    await bot.send_message(message.from_user.id, "Пользователь найден!")
                    await bot.send_message(message.from_user.id, f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                                                 f"Пользователь НЕ заблокирован! "
                                                                 f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}",
                                           reply_markup=markup_admin.commission_promo_discount())
                    async with state.proxy() as data:
                        data["user"] = res
                    await states.Commission.commission_promo_set_discount.set()
            except TypeError:
                await bot.send_message(message.from_user.id, "Пользователь не найден!")
        if not message.text.isdigit() and message.text != "Назад":
            await bot.send_message(message.from_user.id, "Надо ввести целое число!")
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в раздел поиска ID",
                                   reply_markup=markup_admin.commission_promo())
            await states.Commission.commission_promo.set()

    @staticmethod
    async def commission_promo_set_discount(callback: types.CallbackQuery, state: FSMContext):
        if callback.data == "commission_back":
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await bot.send_message(callback.from_user.id,
                                   f"Вы вернулись в раздел Установки комиссий",
                                   reply_markup=markup_admin.commission_set())
            await states.Commission.commission_set.set()
        else:
            res = callback.data[11:]
            async with state.proxy() as data:
                data["commission"] = res
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await bot.send_message(callback.from_user.id,
                                   "Отлично! Теперь настройте время",
                                   reply_markup=markup_admin.commission_promo_set_time())

    @staticmethod
    async def commission_promo_set_time(callback: types.CallbackQuery, state: FSMContext):
        if callback.data == "time_back":
            await bot.send_message(callback.from_user.id, "Пользователь найден!")
            await bot.send_message(callback.from_user.id, f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                                         f"Пользователь НЕ заблокирован! "
                                                         f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}",
                                   reply_markup=markup_admin.commission_promo_discount())
            await states.Commission.commission_promo_set_discount.set()
        else:
            res = callback.data[5:]
            async with state.proxy() as data:
                data["time"] = res
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            comm = data.get('commission')
            if comm == "free":
                comm = "0.0"
            date = datetime.now() + timedelta(hours=int(data.get('time')))
            exists = global_db_obj.check_commission_promo(data.get('user')[1])
            if exists:
                date_promo, percent_promo = str(exists[1]), exists[0]
                limitation = str(datetime.now() - datetime.strptime(date_promo, '%Y-%m-%d %H:%M:%S'))[:1]
                if limitation == "-":
                    await bot.send_message(callback.from_user.id,
                                           f"Вы уже установили промо!\n"
                                           f"Сейчас действует <b>{exists[0]}</b> "
                                           f"до <b>{exists[1]}</b>",
                                           reply_markup=markup_admin.commission_set())
                    await states.Commission.commission_set.set()
                if limitation != "-":
                    await bot.send_message(callback.from_user.id,
                                           f"Отлично! Теперь у пользователя <b>{data.get('user')[1]}</b> "
                                           f"Комиссия <b>{comm}</b> "
                                           f"на время <b>{data.get('time')}</b> часа",
                                           reply_markup=markup_admin.commission_set())
                    global_set_db_obj.set_commission_for_promo(data.get('user')[1], comm, str(date)[:19])
                    await states.Commission.commission_set.set()
            if exists is None:
                await bot.send_message(callback.from_user.id,
                                       f"Отлично! Теперь у пользователя <b>{data.get('user')[1]}</b> "
                                       f"Комиссия <b>{comm}</b> "
                                       f"на время <b>{data.get('time')}</b> часа",
                                       reply_markup=markup_admin.commission_set())
                global_set_db_obj.set_commission_for_promo(data.get('user')[1], comm, str(date)[:19])
                await states.Commission.commission_set.set()

    @staticmethod
    def register_commission_handler(dp: Dispatcher):
        dp.register_message_handler(AdminCommission.commission, state=states.Commission.commission)
        dp.register_message_handler(AdminCommission.commission_set, state=states.Commission.commission_set)
        dp.register_message_handler(AdminCommission.commission_for_performer,
                                    state=states.Commission.commission_for_performer)
        dp.register_message_handler(AdminCommission.commission_for_categories,
                                    state=states.CommissionForCategories.commission_for_categories)
        dp.register_message_handler(AdminCommission.commission_for,
                                    state=states.CommissionForCategories.commission_for_category)
        dp.register_message_handler(AdminCommission.commission_promo,
                                    state=states.Commission.commission_promo)
        dp.register_message_handler(AdminCommission.commission_promo_find_id,
                                    state=states.Commission.commission_promo_find_id)
        dp.register_callback_query_handler(AdminCommission.commission_promo_set_discount,
                                           state=states.Commission.commission_promo_set_discount,
                                           text_contains='commission_')
        dp.register_callback_query_handler(AdminCommission.commission_promo_set_time,
                                           state=states.Commission.commission_promo_set_discount,
                                           text_contains='time_')


class AdminControlChange:
    @staticmethod
    async def change_main(message: types.Message, state: FSMContext):
        if message.text == "Заблокировать":
            async with state.proxy() as data:
                await admins_set.block_user(1, data.get("type_user"), data.get("user_id"))
            await bot.send_message(message.from_user.id, "Вы заблокировали этого пользователя!")
        if message.text == "Разблокировать":
            async with state.proxy() as data:
                await admins_set.block_user(0, data.get("type_user"), data.get("user_id"))
            await bot.send_message(message.from_user.id, "Вы разблокировали этого пользователя!!")
        if message.text == "Начислить сумму":
            await bot.send_message(message.from_user.id,
                                   "Введите сумму для начисления",
                                   reply_markup=markup_admin.markup_clean)
            await states.ChangeUsers.add_money.set()
        if message.text == "Вернуться в главное меню":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_admin.admin_main())
            await states.AdminStates.enter.set()

    @staticmethod
    async def add_money(message: types.Message, state: FSMContext):
        if message.text.isdigit():
            async with state.proxy() as data:
                user_id = data.get("user_id")
                money = int(message.text)
                await admins_set.admin_set_money(user_id, money)
            await bot.send_message(message.from_user.id,
                                   f"Успешно начислили {money} рублей для пользователя {user_id}",
                                   reply_markup=markup_admin.admin_main())
            await states.AdminStates.enter.set()
        else:
            await bot.send_message(message.from_user.id, "Нужно ввести целое число")

    @staticmethod
    def register_control_change_handler(dp: Dispatcher):
        dp.register_message_handler(AdminControlChange.change_main, state=states.ChangeUsers.enter)
        dp.register_message_handler(AdminControlChange.add_money, state=states.ChangeUsers.add_money)


class AdminControl:
    @staticmethod
    async def control(message: types.Message):
        if message.text == "Просмотреть всех Заказчиков":
            res = await general_get.all_customers()
            await bot.send_message(message.from_user.id,
                                   f"Вот полный список Заказчиков", reply_markup=markup_admin.about_customers())
            for i in res:
                await bot.send_message(message.from_user.id,
                                       f"ID: {i.user_id} | Username: {i.username} | Firstname: {i.first_name}")
        if message.text == "Просмотреть всех Исполнителей":
            res = await general_get.all_performers()
            await bot.send_message(message.from_user.id,
                                   f"Вот полный список Исполнителей", reply_markup=markup_admin.about_performers())
            for i in res:
                await bot.send_message(message.from_user.id,
                                       f"ID: {i.user_id} | Username: {i.username} | Firstname: {i.first_name}")
        if message.text == "По ID":
            await bot.send_message(message.from_user.id,
                                   "Введите ID пользователя",
                                   reply_markup=markup_admin.back())
            await states.AboutUsers.find_id.set()
        if message.text == "По имени":
            await bot.send_message(message.from_user.id, "Поиск по имени")
            await bot.send_message(message.from_user.id,
                                   "Введите first name пользователя",
                                   reply_markup=markup_admin.back())
            await states.AboutUsers.find_first_name.set()
        if message.text == "По username":
            await bot.send_message(message.from_user.id, "Поиск никнейму")
            await bot.send_message(message.from_user.id,
                                   "Введите username пользователя",
                                   reply_markup=markup_admin.back())
            await states.AboutUsers.find_username.set()
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню Администратора",
                                   reply_markup=markup_admin.admin_main())
            await states.AdminStates.enter.set()

    @staticmethod
    async def find_id(message: types.Message, state: FSMContext):
        if message.text.isdigit():
            async with state.proxy() as data:
                type_user = data.get("type_user")
            res = await admins_get.admin_check_users(type_user, int(message.text))
            if res:
                async with state.proxy() as data:
                    data["user_id"] = res.user_id
                if type_user == "performers":
                    type_user = "Исполнителя"
                    rating = res.performer_rating
                    money = res.performer_money
                    money_add = True
                else:
                    type_user = "Заказчика"
                    rating = res.customer_rating
                    money = res.customer_money
                    money_add = False
                if not bool(res.ban):
                    await bot.send_message(message.from_user.id, "Пользователь найден!")
                    await bot.send_message(message.from_user.id, f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                                                 f"Пользователь НЕ заблокирован! "
                                                                 f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}")
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"Профиль <b>{type_user}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID - <b>{res.user_id}</b>\n"
                                           f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                           f"Никнейм - <b>@{res.username}</b>\n"
                                           f"{config.KEYBOARD.get('TELEPHONE')} "
                                           f"Номер - <b>{res.telephone}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Имя - <b>{res.first_name}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Фамилия - <b>{res.last_name}</b>\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} Рейтинг - <b>{rating}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} Баланс - <b>{money}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}",
                                           reply_markup=markup_admin.find_user(money_add))
                    await states.ChangeUsers.enter.set()
                    AdminControlChange.register_control_change_handler(dp)
                else:
                    await bot.send_message(message.from_user.id, "Пользователь найден!")
                    await bot.send_message(message.from_user.id, f"{config.KEYBOARD.get('CROSS_MARK')} "
                                                                 f"Пользователь ЗАБЛОКИРОВАН! "
                                                                 f"{config.KEYBOARD.get('CROSS_MARK')}")
                    await bot.send_message(message.from_user.id,
                                           f"{config.KEYBOARD.get('DASH') * 14}\n"
                                           f"Профиль <b>{type_user}</b>\n"
                                           f"{config.KEYBOARD.get('ID_BUTTON')} "
                                           f"ID - <b>{res.user_id}</b>\n"
                                           f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                           f"Никнейм - <b>@{res.username}</b>\n"
                                           f"{config.KEYBOARD.get('TELEPHONE')} "
                                           f"Номер - <b>{res.telephone}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Имя - <b>{res.first_name}</b>\n"
                                           f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                           f"Фамилия - <b>{res.last_name}</b>\n"
                                           f"{config.KEYBOARD.get('BAR_CHART')} Рейтинг - <b>{rating}</b>\n"
                                           f"{config.KEYBOARD.get('DOLLAR')} Баланс - <b>{money}</b>\n"
                                           f"{config.KEYBOARD.get('DASH') * 14}",
                                           reply_markup=markup_admin.find_user(money_add))
                    await states.ChangeUsers.enter.set()
                    AdminControlChange.register_control_change_handler(dp)
            else:
                if type_user == "performers":
                    await bot.send_message(message.from_user.id,
                                           "Исполнитель не найден!",
                                           reply_markup=markup_admin.about_performers())
                    await states.AboutUsers.enter.set()
                else:
                    await bot.send_message(message.from_user.id,
                                           "Заказчик не найден!",
                                           reply_markup=markup_admin.about_customers())
                    await states.AboutUsers.enter.set()
        if not message.text.isdigit() and message.text != "Назад":
            await bot.send_message(message.from_user.id, "Надо ввести цифры")
        if message.text == "Назад":
            await bot.send_message(message.from_user.id,
                                   "Вы вернулись в главное меню",
                                   reply_markup=markup_admin.admin_main())
            await states.AdminStates.enter.set()

    @staticmethod
    async def find_first_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            type_user = data.get("type_user")
        if message.text == "Назад":
            if type_user == "performers":
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись назад",
                                       reply_markup=markup_admin.about_performers())
                await states.AboutUsers.enter.set()
            else:
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись назад",
                                       reply_markup=markup_admin.about_customers())
                await states.AboutUsers.enter.set()
        if message.text != "Назад":
            res = await admins_get.admin_check_users_first_name(type_user, message.text)
            if not res:
                if type_user == "performers":
                    await bot.send_message(message.from_user.id,
                                           "Ничего не найдено!",
                                           reply_markup=markup_admin.about_performers())
                    await states.AboutUsers.enter.set()
                else:
                    await bot.send_message(message.from_user.id,
                                           "Ничего не найдено!",
                                           reply_markup=markup_admin.about_customers())
                    await states.AboutUsers.enter.set()
            else:
                for i in res:
                    if type_user == "performers":
                        type_user = "Исполнителя"
                        rating = i.performer_rating
                        money = i.performer_money
                    else:
                        type_user = "Заказчика"
                        rating = i.customer_rating
                        money = i.customer_money
                    if not bool(i.ban):
                        await bot.send_message(message.from_user.id, "Пользователь найден!")
                        await bot.send_message(message.from_user.id, f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                                                     f"Пользователь НЕ заблокирован! "
                                                                     f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}")
                        await bot.send_message(message.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"Профиль <b>{type_user}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID - <b>{i.user_id}</b>\n"
                                               f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                               f"Никнейм - <b>@{i.username}</b>\n"
                                               f"{config.KEYBOARD.get('TELEPHONE')} "
                                               f"Номер - <b>{i.telephone}</b>\n"
                                               f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                               f"Имя - <b>{i.first_name}</b>\n"
                                               f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                               f"Фамилия - <b>{i.last_name}</b>\n"
                                               f"{config.KEYBOARD.get('BAR_CHART')} Рейтинг - <b>{rating}</b>\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} Баланс - <b>{money}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}",
                                               reply_markup=markup_admin.back())
                        await bot.send_message(message.from_user.id,
                                               f"Нажмите сюда `{i.user_id}` чтобы копировать ID",
                                               parse_mode=ParseMode.MARKDOWN)
                    else:
                        await bot.send_message(message.from_user.id, "Пользователь найден!")
                        await bot.send_message(message.from_user.id, f"{config.KEYBOARD.get('CROSS_MARK')} "
                                                                     f"Пользователь ЗАБЛОКИРОВАН! "
                                                                     f"{config.KEYBOARD.get('CROSS_MARK')}")
                        await bot.send_message(message.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"Профиль <b>{type_user}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID - <b>{i.user_id}</b>\n"
                                               f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                               f"Никнейм - <b>@{i.username}</b>\n"
                                               f"{config.KEYBOARD.get('TELEPHONE')} "
                                               f"Номер - <b>{i.telephone}</b>\n"
                                               f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                               f"Имя - <b>{i.first_name}</b>\n"
                                               f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                               f"Фамилия - <b>{i.last_name}</b>\n"
                                               f"{config.KEYBOARD.get('BAR_CHART')} Рейтинг - <b>{rating}</b>\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} Баланс - <b>{money}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}",
                                               reply_markup=markup_admin.back())
                        await bot.send_message(message.from_user.id,
                                               f"Нажмите сюда `{i.user_id}` чтобы копировать ID",
                                               parse_mode=ParseMode.MARKDOWN)
                await bot.send_message(message.from_user.id,
                                       "Если хотите заблокировать пользователя или начислить сумму, "
                                       "то вам нужно воспользоваться поиском по ID (Скопируйте нужный вам ID)")

    @staticmethod
    async def find_username(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            type_user = data.get("type_user")
        if message.text == "Назад":
            if type_user == "performers":
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись назад",
                                       reply_markup=markup_admin.about_performers())
                await states.AboutUsers.enter.set()
            else:
                await bot.send_message(message.from_user.id,
                                       "Вы вернулись назад",
                                       reply_markup=markup_admin.about_customers())
                await states.AboutUsers.enter.set()
        if message.text != "Назад":
            res = await admins_get.admin_check_users_username(type_user, message.text)
            if not res:
                if type_user == "performers":
                    await bot.send_message(message.from_user.id,
                                           "Ничего не найдено!",
                                           reply_markup=markup_admin.about_performers())
                    await states.AboutUsers.enter.set()
                else:
                    await bot.send_message(message.from_user.id,
                                           "Ничего не найдено!",
                                           reply_markup=markup_admin.about_customers())
                    await states.AboutUsers.enter.set()
            else:
                for i in res:
                    if type_user == "performers":
                        type_user = "Исполнителя"
                        rating = i.performer_rating
                        money = i.performer_money
                    else:
                        type_user = "Заказчика"
                        rating = i.customer_rating
                        money = i.customer_money
                    if not bool(i.ban):
                        await bot.send_message(message.from_user.id, "Пользователь найден!")
                        await bot.send_message(message.from_user.id, f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')} "
                                                                     f"Пользователь НЕ заблокирован! "
                                                                     f"{config.KEYBOARD.get('CHECK_MARK_BUTTON')}")
                        await bot.send_message(message.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"Профиль <b>{type_user}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID - <b>{i.user_id}</b>\n"
                                               f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                               f"Никнейм - <b>@{i.username}</b>\n"
                                               f"{config.KEYBOARD.get('TELEPHONE')} "
                                               f"Номер - <b>{i.telephone}</b>\n"
                                               f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                               f"Имя - <b>{i.first_name}</b>\n"
                                               f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                               f"Фамилия - <b>{i.last_name}</b>\n"
                                               f"{config.KEYBOARD.get('BAR_CHART')} Рейтинг - <b>{rating}</b>\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} Баланс - <b>{money}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}",
                                               reply_markup=markup_admin.back())
                        await bot.send_message(message.from_user.id,
                                               f"Нажмите сюда `{i.user_id}` чтобы копировать ID",
                                               parse_mode=ParseMode.MARKDOWN)
                    else:
                        await bot.send_message(message.from_user.id, "Пользователь найден!")
                        await bot.send_message(message.from_user.id, f"{config.KEYBOARD.get('CROSS_MARK')} "
                                                                     f"Пользователь ЗАБЛОКИРОВАН! "
                                                                     f"{config.KEYBOARD.get('CROSS_MARK')}")
                        await bot.send_message(message.from_user.id,
                                               f"{config.KEYBOARD.get('DASH') * 14}\n"
                                               f"Профиль <b>{type_user}</b>\n"
                                               f"{config.KEYBOARD.get('ID_BUTTON')} "
                                               f"ID - <b>{i.user_id}</b>\n"
                                               f"{config.KEYBOARD.get('SMILING_FACE_WITH_SUNGLASSES')} "
                                               f"Никнейм - <b>@{i.username}</b>\n"
                                               f"{config.KEYBOARD.get('TELEPHONE')} "
                                               f"Номер - <b>{i.telephone}</b>\n"
                                               f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                               f"Имя - <b>{i.first_name}</b>\n"
                                               f"{config.KEYBOARD.get('BUST_IN_SILHOUETTE')} "
                                               f"Фамилия - <b>{i.last_name}</b>\n"
                                               f"{config.KEYBOARD.get('BAR_CHART')} Рейтинг - <b>{rating}</b>\n"
                                               f"{config.KEYBOARD.get('DOLLAR')} Баланс - <b>{money}</b>\n"
                                               f"{config.KEYBOARD.get('DASH') * 14}",
                                               reply_markup=markup_admin.back())
                        await bot.send_message(message.from_user.id,
                                               f"Нажмите сюда `{i.user_id}` чтобы копировать ID",
                                               parse_mode=ParseMode.MARKDOWN)
                await bot.send_message(message.from_user.id,
                                       "Если хотите заблокировать пользователя или начислить сумму, "
                                       "то вам нужно воспользоваться поиском по ID (Скопируйте нужный вам ID)")

    @staticmethod
    def register_control_handler(dp: Dispatcher):
        dp.register_message_handler(AdminControl.control, state=states.AboutUsers.enter)
        dp.register_message_handler(AdminControl.find_id, state=states.AboutUsers.find_id)
        dp.register_message_handler(AdminControl.find_first_name, state=states.AboutUsers.find_first_name)
        dp.register_message_handler(AdminControl.find_username, state=states.AboutUsers.find_username)
