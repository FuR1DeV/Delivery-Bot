import logging
from data.models.performers import Performers
from data.models.orders import Orders, OrdersStatus, Reviews
from data.commands import performers_get, customers_get, general_get

logger = logging.getLogger("bot.data.commands.performer_set_db")

"""Функции добавления/обновления БД"""


async def performer_add(user_id, username, telephone, first_name, last_name):
    """Исполнитель добавляется в базу данных"""
    logger.info(f'Исполнитель {user_id} добавляется в БД')
    performer = Performers(user_id=user_id, username=username, telephone=telephone, first_name=first_name,
                           last_name=last_name)
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
    count_orders = performer.get_orders + 1
    """Исполнитель взяв заказ добавляет его в состоянии статуса"""
    orders_status = OrdersStatus(order_id=order_id)
    await order.update(in_work=user_id, order_get=order_get).apply()
    await performer.update(get_orders=count_orders).apply()
    await orders_status.create()


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








