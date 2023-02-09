import logging
from data.models.performers import Performers, PerformerPersonalData, AutoSendJobOffer, JobsOffers
from data.models.orders import OrdersStatus, OrdersRating, Reviews, OrdersLoading
from data.commands import performers_get, customers_get, general_get
from sqlalchemy.dialects.postgresql import ARRAY

logger = logging.getLogger("bot.data.commands.performer_set_db")

"""Функции добавления/обновления БД"""


async def performer_add(user_id, username, telephone, first_name, last_name):
    """Исполнитель добавляется в базу данных"""
    logger.info(f'Исполнитель {user_id} добавляется в БД')
    performer = Performers(user_id=user_id, username=username, telephone=telephone, first_name=first_name,
                           last_name=last_name)
    await performer.create()


async def performer_add_personal_data(user_id, telephone, real_first_name, real_last_name, selfie):
    performer = PerformerPersonalData(user_id=user_id, telephone=telephone, real_first_name=real_first_name,
                                      real_last_name=real_last_name, selfie=selfie)
    await performer.create()


async def update_performer_money(user_id, money):
    """Обновляется баланс Исполнителя"""
    performer = await performers_get.performer_select(user_id)
    await performer.update(performer_money=money).apply()


async def performer_set_order(user_id, order_id, order_get):
    """Исполнитель берет заказ"""
    order = await general_get.order_select(order_id)
    """Добавляется +1 счётчик в get_orders"""
    performer = await performers_get.performer_select(user_id)
    """Исполнитель взяв заказ добавляет его в состоянии статуса"""
    orders_status = OrdersStatus(order_id=order_id)
    await order.update(in_work=user_id, order_get=order_get).apply()
    await performer.update(get_orders=performer.get_orders + 1).apply()
    await orders_status.create()


async def performer_set_order_loading(user_id, order_id, order_get):
    """Исполнитель берет заказ Погрузки/Разгрузки"""
    order = await OrdersLoading.query.where(OrdersLoading.order_id == order_id).gino.first()
    """Добавляется +1 счётчик в get_orders"""
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    count_orders = performer.get_orders + 1
    count_person = order.count_person + 1
    await order.update(count_person=count_person, in_work=user_id, order_get=order_get).apply()
    await performer.update(get_orders=count_orders).apply()


async def add_new_price(order_id, new_price):
    """Добавляется новая цена заказа от Заказчика по просьбе Исполнителя"""
    order = await general_get.order_select(order_id)
    await order.update(price=new_price).apply()


async def performer_cancel_order(user_id, order_id):
    """Исполнитель отменяет заказ"""
    order = await general_get.order_select(order_id)
    performer = await performers_get.performer_select(user_id)
    res_cancel = performer.canceled_orders + 1
    order_status = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
    await order.update(in_work=0, order_get=None).apply()
    await performer.update(canceled_orders=res_cancel).apply()
    await order_status.delete()


async def performer_set_commission_for_cancel(user_id, commission):
    """Взимается комиссия с Исполнителя за отменённый заказ"""
    performer = await performers_get.performer_select(user_id)
    money = performer.performer_money - commission
    await performer.update(performer_money=money).apply()


async def performer_set_order_status(order_id):
    """Исполнитель ставит выполнено в состоянии заказа"""
    order_status = await general_get.check_details_status(order_id)
    await order_status.update(performer_status=1).apply()


async def performer_set_rating_to_customer(user_id, input_performer):
    """Исполнитель ставит оценку Заказчику"""
    customer = await customers_get.customer_select(user_id)
    customer_rating = (customer.customer_rating + int(input_performer)) / 2
    await customer.update(customer_rating=customer_rating).apply()


async def performer_set_rating_to_customer_in_review_db(order_id, performer_rating):
    """Ставится оценка Заказчику в таблицу Отзывы"""
    review = await Reviews.query.where(Reviews.order_id == order_id).gino.first()
    await review.update(rating_from_performer=int(performer_rating)).apply()


async def performer_set_review_to_customer_in_review_db(order_id, performer_review):
    """Исполнитель оставляет отзыв Заказчику в таблицу Отзывы"""
    review = await Reviews.query.where(Reviews.order_id == order_id).gino.first()
    await review.update(review_from_performer=performer_review).apply()


async def performer_set_self_status(user_id, performer_category, perf_cat_limit):
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    await performer.update(performer_category=performer_category,
                           performer_category_limit=perf_cat_limit).apply()


async def set_money(user_id, money):
    logger.info(f'Обновляется баланс пользователя - {user_id}')
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    result = performer.performer_money + money
    await performer.update(money=result).apply()


async def performer_set_order_rating(order_id, rating, user_id):
    logger.info(f'Исполнитель {user_id} ставит {rating} заказу {order_id}')
    order = OrdersRating(order_id=order_id, rating=rating, user_id=user_id)
    await order.create()


async def private_chat_money(user_id):
    logger.info(f'Взимается плата 300 рублей за приватный чат с {user_id}')
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    res_money = performer.performer_money - 300
    await performer.update(performer_money=res_money).apply()


async def private_chat_add(user_id, count_word, enter_date):
    performer = Performers(user_id=user_id, count_word=count_word, enter_date=enter_date)
    await performer.create()


async def performer_change_arrive_status(order_id):
    arrive = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
    res = int(arrive.performer_arrive) - 1
    await arrive.update(performer_arrive=str(res)).apply()


async def performer_change_auto_send(user_id):
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    await performer.update(auto_send=1).apply()


async def performer_change_auto_send_close(user_id):
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    await performer.update(auto_send=0).apply()


async def performer_auto_send_pay(user_id, start, end, money):
    auto_send = AutoSendJobOffer(user_id=user_id, start=start, end=end)
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    await performer.update(performer_money=performer.performer_money - int(money)).apply()
    await auto_send.create()


async def performer_jobs_pay(user_id, start, end, money):
    exist = await JobsOffers.query.where(JobsOffers.user_id == user_id).gino.first()
    if exist:
        await exist.delete()
    jobs = JobsOffers(user_id=user_id, start=start, end=end)
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    await performer.update(performer_money=performer.performer_money - int(money)).apply()
    await jobs.create()
