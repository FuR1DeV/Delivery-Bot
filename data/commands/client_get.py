import logging

from sqlalchemy import and_

from data.models.clients import Client
from data.models.stores import StoreOrders

logger = logging.getLogger("bot.data.commands.client_get_db")

"""Функции взятия информации из БД для Клиента"""


async def client_select(user_id):
    client = await Client.query.where(Client.user_id == user_id).gino.first()
    return client


async def client_get_orders(user_id):
    orders = await StoreOrders.query.where(StoreOrders.client_id == user_id).gino.all()
    return orders
