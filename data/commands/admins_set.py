import logging

from sqlalchemy import and_

from data.models.customers import Customers
from data.models.admins import Admins
from data.models.orders import Orders, OrdersStatus, Reviews
from data.commands import customers_get, performers_get


logger = logging.getLogger("bot.data.commands.customer_set_db")

"""Функции добавления/обновления БД для Заказчика"""


async def admin_add(user_id, username, first_name, last_name):
    """Админ добавляется в БД"""
    admin = Admins(user_id=user_id, username=username, first_name=first_name, last_name=last_name)
    await admin.create()




