import logging

from data.models.admins import Admins, Limitations
from data.models.customers import Customers
from data.models.performers import Performers, PerformerPersonalData, JobsSales
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


async def admin_check_personal_data(user_id):
    performer = await PerformerPersonalData.query.where(PerformerPersonalData.user_id == user_id).gino.first()
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


async def admin_check_users_telephone(type_user: str, telephone):
    logger.info('Админ ищет пользователя в БД по telephone')
    if type_user == "customers":
        customer = await Customers.query.where(Customers.telephone.like(f"%{telephone}%")).gino.all()
        return customer
    else:
        performer = await Performers.query.where(Performers.telephone.like(f"%{telephone}%")).gino.all()
        return performer


async def admin_check_commission():
    logger.info(f'Админ проверяет комиссию')
    commission = await Commission.query.gino.all()
    return commission


async def check_commission_promo(user_id):
    logger.info(f'Проверяется промо комиссия')
    commission = await CommissionPromo.query.where(CommissionPromo.user_id == user_id).gino.first()
    return commission


async def check_jobs_sales():
    auto_send = await JobsSales.query.where(JobsSales.jobs == "auto_send").gino.first()
    twelve = await JobsSales.query.where(JobsSales.jobs == "twelve").gino.first()
    day = await JobsSales.query.where(JobsSales.jobs == "day").gino.first()
    three_day = await JobsSales.query.where(JobsSales.jobs == "3_day").gino.first()
    week = await JobsSales.query.where(JobsSales.jobs == "week").gino.first()
    return [auto_send, twelve, day, three_day, week]


async def check_limitations():
    limitations = await Limitations.query.gino.all()
    return limitations
