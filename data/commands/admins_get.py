import logging

from sqlalchemy import and_

from data.models.admins import Admins
from data.models.customers import Customers
from data.models.performers import Performers
from data.models.orders import Orders, OrdersStatus, Reviews
from data.commands import customers_get, performers_get


logger = logging.getLogger("bot.data.commands.customer_set_db")

"""Функции добавления/обновления БД для Заказчика"""


async def admin_select(user_id):
    admin = await Admins.query.where(Admins.user_id == user_id).gino.first()
    return admin


async def admin_check_order(order_id):
    logger.info(f'Админ просматривает заказ {order_id}')
    order = await Orders.query.where(Orders.order_id == order_id).gino.first()
    return order


async def admin_check_users(type_user, user_id):
    """Админ выбирает пользователя в БД"""
    if type_user == "customers":
        customer = await Customers.query.where(Customers.user_id == user_id).gino.first()
        return customer
    else:
        performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
        return performer


async def admin_check_review(order_id):
    """Админ выбирает отзывы по заказу по order_id"""
    review = Reviews.query.where(Reviews.order_id == order_id).gino.all()
    return review
