import logging

from sqlalchemy import and_

from data.models.customers import Customers
from data.models.performers import Performers
from data.models.admins import Admins
from data.models.orders import Orders, OrdersStatus, Reviews
from data.commands import customers_get, performers_get


logger = logging.getLogger("bot.data.commands.customer_set_db")

"""Функции добавления/обновления БД для Заказчика"""


async def admin_add(user_id, username, first_name, last_name):
    """Админ добавляется в БД"""
    admin = Admins(user_id=user_id, username=username, first_name=first_name, last_name=last_name)
    await admin.create()


async def block_user(block, type_user, user_id):
    if block:
        logger.info(f'Администратор блокирует пользователя {user_id}')
        if type_user == "performers":
            performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
            await performer.update(ban=1).apply()
        else:
            customer = await Customers.query.where(Customers.user_id == user_id).gino.first()
            await customer.update(ban=1).apply()
    else:
        logger.info(f'Администратор разблокирует пользователя {user_id}')
        if type_user == "performers":
            performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
            await performer.update(ban=0).apply()
        else:
            customer = await Customers.query.where(Customers.user_id == user_id).gino.first()
            await customer.update(ban=0).apply()


async def admin_set_money(user_id, money):
    logger.info(f'Админ добавляет деньги {money} для {user_id}')
    performer = await Performers.query.where(Performers.user_id == user_id).gino.first()
    await performer.update(performer_money=performer.performer_money + money).apply()


