import logging

from sqlalchemy import and_, or_

from data.models.orders import Orders, OrdersRating, OrdersStatus, OrdersLoading
from data.models.performers import Performers
from data.models.admins import PrivateChat

logger = logging.getLogger("bot.data.commands.performer_get_db")

"""Функции взятия информации из БД"""


async def performer_select(user_id):
    """Выбор Исполнителя"""
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    return performer


async def performer_count_orders(user_id):
    """Исполнитель смотрит статистику по заказам"""
    orders = await Performers.query.where(Performers.user_id == user_id).gino.first()
    orders_in_work = await Orders.query.where(and_(Orders.in_work == user_id,
                                                   Orders.completed == 0,
                                                   Orders.order_cancel == None)).gino.all()
    orders_end = await Orders.query.where(and_(Orders.in_work == user_id,
                                               Orders.completed == 1)).gino.all()
    orders_cancel = await Performers.query.where(Performers.user_id == user_id).gino.first()
    return orders.get_orders, len(orders_in_work), len(orders_end), orders_cancel.canceled_orders


async def check_private_chat_status(user_id):
    """Исполнитель проверяет статус приватного чата"""
    private = await PrivateChat.query.where(PrivateChat.user_id == user_id).gino.first()
    return private


async def performer_checks_all_orders(user_id, performer_category):
    """Исполнитель смотрит все заказы"""
    orders = await Orders.query.where(and_(Orders.in_work == 0,
                                           Orders.block == 0,
                                           Orders.order_get == None,
                                           Orders.order_cancel == None,
                                           Orders.user_id != user_id,
                                           or_(Orders.performer_category == performer_category,
                                               Orders.performer_category == 'any'))).gino.all()
    return orders


async def performer_checks_all_orders_loading(user_id):
    """Исполнитель смотрит все заказы Погрузки/Разгрузки"""
    orders = await OrdersLoading.query.where(and_(OrdersLoading.block == 0,
                                                  OrdersLoading.order_end == None,
                                                  OrdersLoading.order_cancel == None,
                                                  OrdersLoading.user_id != user_id)).gino.all()
    return orders


async def performer_checks_all_orders_with_category(user_id, performer_category, category_delivery):
    """Исполнитель смотрит все заказы с определенной категорией"""
    orders = await Orders.query.where(and_(Orders.in_work == 0,
                                           Orders.block == 0,
                                           Orders.order_get == None,
                                           Orders.order_cancel == None,
                                           Orders.user_id != user_id,
                                           or_(Orders.performer_category == performer_category,
                                               Orders.performer_category == 'any'),
                                           Orders.category_delivery == category_delivery)).gino.all()
    return orders


async def performer_check_order_rating(order_id, user_id):
    """Исполнитель смотрит рейтинг заказа"""
    order = await OrdersRating.query.where(and_(OrdersRating.order_id == order_id,
                                                OrdersRating.user_id == user_id)).gino.first()
    if order is None:
        return None
    else:
        return order.rating


async def performer_view_order(order_id):
    """Исполнитель смотрит заказ по order_id"""
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    return order


async def performer_checks_customer_user_id(order_id):
    """Исполнитель смотрит user_id Заказчика по order_id"""
    user_id = await Orders.query.where(Orders.order_id == order_id).gino.first()
    return user_id.user_id


async def performer_view_list_orders(user_id):
    """Исполнитель просматривает взятые заказы"""
    orders = await Orders.query.where(and_(Orders.in_work == user_id,
                                           Orders.completed == 0,
                                           Orders.order_cancel == None)).gino.all()
    return orders


async def performer_get_status_order(order_id):
    """Исполнитель просматривает есть ли заказ в orders_status"""
    order_status = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
    if order_status:
        return True
    else:
        return None


async def performer_all_completed_orders(user_id):
    """Исполнитель выгружает список всех своих завершенных заказов"""
    orders = await Orders.query.where(and_(Orders.in_work == user_id,
                                           Orders.completed == 1)).gino.all()
    return orders


async def performer_get_finished_orders_year(user_id, year):
    """Исполнитель выгружает список всех своих завершенных заказов"""
    """Выбирает год"""
    result = await Orders.query.where(and_(Orders.in_work == user_id,
                                           Orders.order_end.like(f"%{year}%"))).gino.all()
    return result


async def performer_get_finished_orders_month(user_id, year, month):
    """Исполнитель выгружает список всех своих завершенных заказов"""
    """Выбирает месяц"""
    result = await Orders.query.where(and_(Orders.in_work == user_id,
                                           Orders.order_end.like(f"%{month}-{year}%"))).gino.all()
    return result


async def performer_get_finished_orders_day(user_id, year, month, day):
    """Исполнитель выгружает список всех своих завершенных заказов"""
    """Выбирает день"""
    result = await Orders.query.where(and_(Orders.in_work == user_id,
                                           Orders.order_end.like(f"%{day}-{month}-{year}%"))).gino.all()
    return result


async def performer_get_complete_order(order_id):
    """Исполнитель выгружает конкретный завершенный заказ"""
    order = await Orders.query.where(and_(Orders.order_id == order_id,
                                          Orders.completed == 1)).gino.first()
    return order


async def performer_trying_change_self_category(user_id):
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    return performer.performer_category_limit


async def performer_arrive_info(order_id):
    arrive = await OrdersStatus.query.where(OrdersStatus.order_id == order_id).gino.first()
    return arrive.performer_arrive
