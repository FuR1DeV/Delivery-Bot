import logging

from data.models.admins import Admins
from data.models.customers import Customers
from data.models.performers import Performers
from data.models.orders import Orders, Reviews, Commission, CommissionPromo


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
    review = await Reviews.query.where(Reviews.order_id == order_id).gino.first()
    return review


async def admin_check_users_first_name(type_user: str, first_name):
    logger.info('Админ ищет пользователя в БД по first_name')
    if type_user == "customers":
        customer = await Customers.query.where(Customers.first_name.like(f"%{first_name}%")).gino.all()
        return customer
    else:
        performer = await Performers.query.where(Performers.first_name.like(f"%{first_name}%")).gino.all()
        return performer


async def admin_check_users_username(type_user: str, username):
    logger.info('Админ ищет пользователя в БД по username')
    if type_user == "customers":
        customer = await Customers.query.where(Customers.username.like(f"%{username}%")).gino.all()
        return customer
    else:
        performer = await Performers.query.where(Performers.username.like(f"%{username}%")).gino.all()
        return performer


async def admin_check_commission():
    logger.info(f'Админ проверяет комиссию')
    commission = await Commission.query.gino.all()
    return commission


async def check_commission_promo(user_id):
    logger.info(f'Проверяется промо комиссия')
    commission = await CommissionPromo.query.where(CommissionPromo.user_id == user_id).gino.first()
    return commission
