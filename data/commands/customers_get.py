import logging

from sqlalchemy import and_

from data.models.customers import Customers
from data.models.orders import Orders, OrdersStatus, OrdersLoading

logger = logging.getLogger("bot.data.commands.customer_get_db")

"""Функции взятия информации из БД для Заказчика"""


async def customer_select(user_id):
    customer = await Customers.query.where(Customers.user_id == user_id).gino.first()
    return customer


async def customer_view_order(order_id) -> tuple:
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    order_loading = await OrdersLoading.query.where(OrdersLoading.order_id == order_id).gino.first()
    if order:
        return order, "order"
    if order_loading:
        return order_loading, "order_loading"


async def customer_all_orders(user_id):
    """Заказчик выгружает список всех своих заказов"""
    orders = await Orders.query.where(and_(Orders.user_id == user_id,
                                           Orders.completed == 0,
                                           Orders.order_cancel == None)).gino.all()
    return orders


async def customer_all_orders_loading(user_id):
    """Заказчик выгружает список всех своих заказов погрузки/разгрузки"""
    orders_loading = await OrdersLoading.query.where(and_(OrdersLoading.user_id == user_id,
                                                          OrdersLoading.completed == 0,
                                                          OrdersLoading.order_cancel == None)).gino.all()
    return orders_loading


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


async def customer_in_work_order_loading(order_id):
    """Заказчик проверяет взят ли заказ грузчиков"""
    order = await OrdersLoading.query.where(OrdersLoading.order_id == order_id).gino.first()
    return order.in_work


async def customer_get_status_order(order_id):
    """Заказчик просматривает есть ли заказ в orders_status"""
    order_status = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
    if order_status:
        return True
    else:
        return None


async def customer_all_completed_orders(user_id):
    """Заказчик выгружает список всех своих завершенных заказов"""
    orders = await Orders.query.where(and_(Orders.user_id == user_id,
                                           Orders.completed == 1)).gino.all()
    return orders


async def customer_get_finished_orders_year(user_id, year):
    """Заказчик выгружает список всех своих завершенных заказов"""
    """Выбирает год"""
    result = await Orders.query.where(and_(Orders.user_id == user_id,
                                           Orders.order_end.like(f"%{year}%"))).gino.all()
    return result


async def customer_get_finished_orders_month(user_id, year, month):
    """Заказчик выгружает список всех своих завершенных заказов"""
    """Выбирает месяц"""
    result = await Orders.query.where(and_(Orders.user_id == user_id,
                                           Orders.order_end.like(f"%{month}-{year}%"))).gino.all()
    return result


async def customer_get_finished_orders_day(user_id, year, month, day):
    """Заказчик выгружает список всех своих завершенных заказов"""
    """Выбирает день"""
    result = await Orders.query.where(and_(Orders.user_id == user_id,
                                           Orders.order_end.like(f"%{day}-{month}-{year}%"))).gino.all()
    return result


async def customer_get_complete_order(order_id):
    """Заказчик выгружает конкретный завершенный заказ"""
    order = await Orders.query.where(and_(Orders.order_id == order_id,
                                          Orders.completed == 1)).gino.first()
    return order
