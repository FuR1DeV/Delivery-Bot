import logging

from sqlalchemy import and_

from data.models.customers import Customers
from data.models.orders import Orders, OrdersStatus

logger = logging.getLogger("bot.data.commands.customer_get_db")

"""Функции взятия информации из БД для Заказчика"""


async def customer_select(user_id):
    customer = await Customers.query.where(Customers.user_id == user_id).gino.first()
    return customer


async def customer_all_orders(user_id):
    """Заказчик выгружает список всех своих заказов"""
    orders = await Orders.query.where(and_(Orders.user_id == user_id,
                                           Orders.completed == 0,
                                           Orders.order_cancel == None)).gino.all()
    return orders


async def customer_count_orders(user_id):
    """Заказчик смотрит статистику по заказам"""
    orders = await Orders.query.where(Orders.user_id == user_id).gino.all()
    orders_in_work = await Orders.query.where(and_(Orders.user_id == user_id,
                                                   Orders.in_work > 1,
                                                   Orders.completed == 0,
                                                   Orders.order_cancel == None)).gino.all()
    orders_end = await Orders.query.where(and_(Orders.user_id == user_id,
                                               Orders.completed == 1)).gino.all()
    orders_cancel = await Orders.query.where(and_(Orders.user_id == user_id,
                                                  Orders.order_cancel != None)).gino.all()
    return len(orders), len(orders_in_work), len(orders_end), len(orders_cancel)


async def customer_in_work_order(order_id):
    """Заказчик проверяет взят ли заказ"""
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    return order.in_work


async def customer_get_status_order(order_id):
    """Заказчик просматривает есть ли заказ в orders_status"""
    order_status = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
    if order_status:
        return True
    else:
        return None





