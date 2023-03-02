import logging

from sqlalchemy import and_

from data.models.customers import Customers
from data.models.orders import Orders, OrdersStatus, OrdersLoading
from data.models.performers import PerformerPersonalData

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
    """Заказчик выгружает список всех своих заказов в работе"""
    orders = await Orders.query.where(and_(Orders.user_id == user_id,
                                           Orders.completed == 0)).gino.all()
    return orders


async def customer_all_orders_in_work(user_id):
    """Заказчик выгружает список всех своих заказов в работе"""
    orders = await Orders.query.where(and_(Orders.user_id == user_id,
                                           Orders.completed == 0,
                                           Orders.in_work > 0)).gino.all()
    return orders


async def customer_all_orders_not_at_work(user_id):
    """Заказчик выгружает список всех своих заказов в ожидании"""
    orders = await Orders.query.where(and_(Orders.user_id == user_id,
                                           Orders.completed == 0,
                                           Orders.in_work == 0)).gino.all()
    return orders


async def customer_all_orders_loading(user_id):
    """Заказчик выгружает список всех своих заказов погрузки/разгрузки"""
    orders_loading = await OrdersLoading.query.where(and_(OrdersLoading.user_id == user_id,
                                                          OrdersLoading.completed == 0)).gino.all()
    return orders_loading


async def customer_count_orders(user_id) -> tuple:
    """Заказчик смотрит статистику по заказам"""
    customer = await Customers.query.where(Customers.user_id == user_id).gino.first()
    orders_in_work = await Orders.query.where(and_(Orders.user_id == user_id,
                                                   Orders.in_work > 1,
                                                   Orders.completed == 0)).gino.all()
    return customer, len(orders_in_work)


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


async def customer_check_personal_data(user_id):
    performer = await PerformerPersonalData.query.where(PerformerPersonalData.user_id == user_id).gino.first()
    return performer
